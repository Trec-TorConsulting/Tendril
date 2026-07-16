from __future__ import annotations

import base64
import io
import json
import math
import os
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import onnxruntime as ort
from PIL import Image

from app.artifacts import ArtifactError, resolve_model_path


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    model_path: str
    input_width: int
    input_height: int
    confidence_threshold: float
    iou_threshold: float
    max_detections: int
    class_map: dict[int, str]


@dataclass(frozen=True, slots=True)
class DetectionResult:
    class_name: str
    confidence: float
    bbox: list[float]


class DetectorError(RuntimeError):
    pass


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise DetectorError(f"invalid integer for {name}: {raw}") from exc


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise DetectorError(f"invalid float for {name}: {raw}") from exc


def _load_class_map() -> dict[int, str]:
    raw = os.environ.get("VISION_CLASS_MAP", "").strip()
    if not raw:
        return {0: "cannabis"}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DetectorError("VISION_CLASS_MAP must be valid JSON") from exc

    if not isinstance(parsed, dict):
        raise DetectorError("VISION_CLASS_MAP must be a JSON object")

    mapped: dict[int, str] = {}
    for key, value in parsed.items():
        try:
            idx = int(key)
        except (TypeError, ValueError) as exc:
            raise DetectorError(f"invalid class map key: {key}") from exc
        if not isinstance(value, str) or not value:
            raise DetectorError(f"invalid class map value for key {key}")
        mapped[idx] = value
    return mapped


def load_detector_config() -> DetectorConfig:
    model_path = os.environ.get("VISION_MODEL_PATH", "").strip()
    model_storage_key = os.environ.get("VISION_MODEL_STORAGE_KEY", "").strip()
    model_local_path = os.environ.get("VISION_MODEL_LOCAL_PATH", "/tmp/vision/model.onnx").strip()

    if not model_path and model_storage_key:
        try:
            model_path = resolve_model_path(storage_key=model_storage_key, local_path=model_local_path)
        except ArtifactError as exc:
            raise DetectorError(str(exc)) from exc

    if not model_path:
        raise DetectorError("VISION_MODEL_PATH or VISION_MODEL_STORAGE_KEY is required for inference")

    return DetectorConfig(
        model_path=model_path,
        input_width=_env_int("VISION_INPUT_WIDTH", 640),
        input_height=_env_int("VISION_INPUT_HEIGHT", 640),
        confidence_threshold=_env_float("VISION_CONFIDENCE_THRESHOLD", 0.25),
        iou_threshold=_env_float("VISION_IOU_THRESHOLD", 0.45),
        max_detections=_env_int("VISION_MAX_DETECTIONS", 50),
        class_map=_load_class_map(),
    )


@lru_cache(maxsize=1)
def get_session() -> ort.InferenceSession:
    cfg = load_detector_config()
    providers = ["CPUExecutionProvider"]
    return ort.InferenceSession(cfg.model_path, providers=providers)


def _decode_image(image_b64: str) -> Image.Image:
    try:
        raw = base64.b64decode(image_b64, validate=True)
    except (ValueError, TypeError) as exc:
        raise DetectorError("image_base64 is invalid") from exc

    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise DetectorError("image payload is not a valid image") from exc


def _prepare_input(image: Image.Image, cfg: DetectorConfig) -> tuple[np.ndarray, int, int]:
    original_width, original_height = image.size
    resized = image.resize((cfg.input_width, cfg.input_height), Image.Resampling.BILINEAR)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, axis=0)
    return arr, original_width, original_height


def _xywh_to_xyxy(cx: float, cy: float, w: float, h: float) -> tuple[float, float, float, float]:
    half_w = w / 2.0
    half_h = h / 2.0
    return (cx - half_w, cy - half_h, cx + half_w, cy + half_h)


def _iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    inter_w = max(0.0, x2 - x1)
    inter_h = max(0.0, y2 - y1)
    inter = inter_w * inter_h
    if inter == 0.0:
        return 0.0

    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    denom = area_a + area_b - inter
    if denom <= 0.0:
        return 0.0
    return inter / denom


def _nms(
    rows: list[tuple[float, int, tuple[float, float, float, float]]],
    iou_threshold: float,
    max_detections: int,
) -> list[tuple[float, int, tuple[float, float, float, float]]]:
    rows = sorted(rows, key=lambda item: item[0], reverse=True)
    selected: list[tuple[float, int, tuple[float, float, float, float]]] = []

    for candidate in rows:
        if len(selected) >= max_detections:
            break
        suppress = False
        for chosen in selected:
            if candidate[1] != chosen[1]:
                continue
            if _iou(candidate[2], chosen[2]) >= iou_threshold:
                suppress = True
                break
        if not suppress:
            selected.append(candidate)
    return selected


def _parse_yolo_output(
    output: np.ndarray,
    cfg: DetectorConfig,
    original_width: int,
    original_height: int,
) -> list[DetectionResult]:
    data = np.squeeze(output)
    if data.ndim != 2:
        raise DetectorError("unsupported ONNX output shape")

    if data.shape[0] < data.shape[1]:
        data = np.transpose(data)

    candidates: list[tuple[float, int, tuple[float, float, float, float]]] = []
    for row in data:
        if row.shape[0] < 6:
            continue

        cx, cy, w, h = row[0], row[1], row[2], row[3]
        class_scores = row[4:]
        class_idx = int(np.argmax(class_scores))
        score = float(class_scores[class_idx])

        if math.isnan(score) or score < cfg.confidence_threshold:
            continue

        x1, y1, x2, y2 = _xywh_to_xyxy(float(cx), float(cy), float(w), float(h))
        x_scale = original_width / cfg.input_width
        y_scale = original_height / cfg.input_height

        box = (
            max(0.0, min(original_width, x1 * x_scale)),
            max(0.0, min(original_height, y1 * y_scale)),
            max(0.0, min(original_width, x2 * x_scale)),
            max(0.0, min(original_height, y2 * y_scale)),
        )
        candidates.append((score, class_idx, box))

    selected = _nms(candidates, cfg.iou_threshold, cfg.max_detections)

    results: list[DetectionResult] = []
    for score, class_idx, (x1, y1, x2, y2) in selected:
        label = cfg.class_map.get(class_idx, f"class_{class_idx}")
        results.append(
            DetectionResult(
                class_name=label,
                confidence=score,
                bbox=[x1, y1, x2, y2],
            )
        )
    return results


def run_detection(image_b64: str) -> list[DetectionResult]:
    cfg = load_detector_config()
    session = get_session()

    image = _decode_image(image_b64)
    model_input, original_width, original_height = _prepare_input(image, cfg)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: model_input})
    if not outputs:
        return []

    return _parse_yolo_output(outputs[0], cfg, original_width, original_height)
