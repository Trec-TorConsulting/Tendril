from __future__ import annotations

import base64
import io
import json
import logging
import math
import os
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import onnxruntime as ort
from PIL import Image

from app.artifacts import ArtifactError, resolve_model_path
from app.coral import CoralUnavailableError, run_coral_inference
from app.registry import ManifestError, ModelManifest, load_active_manifest
from app.runtime import (
    AcceleratorTier,
    choose_accelerator,
    choose_fallback_accelerator,
    load_runtime_config,
)
from app.telemetry import telemetry

logger = logging.getLogger("tendril.vision.detector.inference")


@dataclass(frozen=True, slots=True)
class DetectorConfig:
    model_path: str
    input_width: int
    input_height: int
    confidence_threshold: float
    iou_threshold: float
    max_detections: int
    class_map: dict[int, str]
    model_version: str = ""
    edgetpu_model_path: str = ""


@dataclass(frozen=True, slots=True)
class DetectionResult:
    class_name: str
    confidence: float
    bbox: list[float]


@dataclass(frozen=True, slots=True)
class DetectionOutput:
    tier: AcceleratorTier
    detections: list[DetectionResult]


class DetectorError(RuntimeError):
    pass


# Cache of the last successfully-loaded config so an incompatible manifest can be
# rejected while keeping the previously active model in service.
_LAST_GOOD_CONFIG: DetectorConfig | None = None


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


def _resolve_storage_key(*, storage_key: str, local_path: str) -> str:
    try:
        return resolve_model_path(storage_key=storage_key, local_path=local_path)
    except ArtifactError as exc:
        raise DetectorError(str(exc)) from exc


def _config_from_manifest(manifest: ModelManifest) -> DetectorConfig:
    model_local = os.environ.get("VISION_MODEL_LOCAL_PATH", "/tmp/vision/model.onnx").strip()
    edgetpu_local = os.environ.get("VISION_MODEL_EDGETPU_LOCAL_PATH", "/tmp/vision/model_edgetpu.tflite").strip()

    model_path = ""
    if manifest.onnx_key:
        model_path = _resolve_storage_key(storage_key=manifest.onnx_key, local_path=model_local)

    edgetpu_path = ""
    if manifest.edgetpu_key:
        try:
            edgetpu_path = _resolve_storage_key(storage_key=manifest.edgetpu_key, local_path=edgetpu_local)
        except DetectorError:
            logger.warning("Edge TPU artifact unavailable for version %s; using fallback tiers", manifest.version)
            edgetpu_path = ""

    if not model_path and not edgetpu_path:
        raise DetectorError("active manifest resolved no usable model artifact")

    return DetectorConfig(
        model_path=model_path,
        edgetpu_model_path=edgetpu_path,
        model_version=manifest.version,
        input_width=manifest.input_width,
        input_height=manifest.input_height,
        confidence_threshold=_env_float("VISION_CONFIDENCE_THRESHOLD", 0.25),
        iou_threshold=_env_float("VISION_IOU_THRESHOLD", 0.45),
        max_detections=_env_int("VISION_MAX_DETECTIONS", 50),
        class_map=manifest.class_map,
    )


def _config_from_env() -> DetectorConfig:
    model_path = os.environ.get("VISION_MODEL_PATH", "").strip()
    model_storage_key = os.environ.get("VISION_MODEL_STORAGE_KEY", "").strip()
    model_local_path = os.environ.get("VISION_MODEL_LOCAL_PATH", "/tmp/vision/model.onnx").strip()

    if not model_path and model_storage_key:
        model_path = _resolve_storage_key(storage_key=model_storage_key, local_path=model_local_path)

    if not model_path:
        raise DetectorError("VISION_MODEL_PATH or VISION_MODEL_STORAGE_KEY is required for inference")

    edgetpu_model_path = os.environ.get("VISION_MODEL_EDGETPU_PATH", "").strip()
    edgetpu_storage_key = os.environ.get("VISION_MODEL_EDGETPU_STORAGE_KEY", "").strip()
    edgetpu_local_path = os.environ.get("VISION_MODEL_EDGETPU_LOCAL_PATH", "/tmp/vision/model_edgetpu.tflite").strip()
    if not edgetpu_model_path and edgetpu_storage_key:
        try:
            edgetpu_model_path = _resolve_storage_key(storage_key=edgetpu_storage_key, local_path=edgetpu_local_path)
        except DetectorError:
            logger.warning("Edge TPU artifact download failed; using fallback tiers")
            edgetpu_model_path = ""

    return DetectorConfig(
        model_path=model_path,
        edgetpu_model_path=edgetpu_model_path,
        model_version=os.environ.get("VISION_MODEL_VERSION", "").strip(),
        input_width=_env_int("VISION_INPUT_WIDTH", 640),
        input_height=_env_int("VISION_INPUT_HEIGHT", 640),
        confidence_threshold=_env_float("VISION_CONFIDENCE_THRESHOLD", 0.25),
        iou_threshold=_env_float("VISION_IOU_THRESHOLD", 0.45),
        max_detections=_env_int("VISION_MAX_DETECTIONS", 50),
        class_map=_load_class_map(),
    )


def load_detector_config() -> DetectorConfig:
    """Resolve the active detector configuration.

    Prefers an active-model manifest from the registry (S3/local) and falls back
    to explicit env configuration. An incompatible manifest is rejected while the
    previously loaded model stays in service.
    """
    global _LAST_GOOD_CONFIG
    try:
        manifest = load_active_manifest()
    except ManifestError as exc:
        telemetry.record_manifest_rejection()
        if _LAST_GOOD_CONFIG is not None:
            logger.warning("Rejecting incompatible model manifest; keeping active model: %s", exc)
            return _LAST_GOOD_CONFIG
        raise DetectorError(f"model manifest invalid and no active model loaded: {exc}") from exc

    config = _config_from_manifest(manifest) if manifest is not None else _config_from_env()
    _LAST_GOOD_CONFIG = config
    return config


@lru_cache(maxsize=1)
def _get_session_cached(model_path: str, providers: tuple[str, ...]) -> ort.InferenceSession:
    return ort.InferenceSession(model_path, providers=list(providers))


def _select_providers(accelerator: AcceleratorTier) -> list[str]:
    available = set(ort.get_available_providers())

    providers: list[str] = []
    if accelerator == AcceleratorTier.GPU:
        for provider in ("TensorrtExecutionProvider", "CUDAExecutionProvider"):
            if provider in available:
                providers.append(provider)
    if "CPUExecutionProvider" in available:
        providers.append("CPUExecutionProvider")
    if not providers:
        providers = ["CPUExecutionProvider"]
    return providers


def get_session(accelerator: AcceleratorTier | None = None) -> ort.InferenceSession:
    cfg = load_detector_config()
    if accelerator is None:
        runtime_cfg = load_runtime_config()
        accelerator = choose_accelerator(runtime_cfg)
    providers = _select_providers(accelerator)

    return _get_session_cached(cfg.model_path, tuple(providers))


def _decode_image(image_b64: str) -> Image.Image:
    try:
        raw = base64.b64decode(image_b64, validate=True)
    except (ValueError, TypeError) as exc:
        raise DetectorError("image_base64 is invalid") from exc

    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise DetectorError("image payload is not a valid image") from exc


def _prepare_input(image: Image.Image, cfg: DetectorConfig) -> np.ndarray:
    resized = image.resize((cfg.input_width, cfg.input_height), Image.Resampling.BILINEAR)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, axis=0)
    return arr


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
) -> list[DetectionResult]:
    data = np.squeeze(output)
    if data.ndim != 2:
        raise DetectorError("unsupported model output shape")

    if data.shape[0] < data.shape[1]:
        data = np.transpose(data)

    inv_w = 1.0 / float(cfg.input_width)
    inv_h = 1.0 / float(cfg.input_height)

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

        # Normalize to [0, 1] using the model input resolution so bounding boxes
        # are resolution-independent for overlay rendering on any image size.
        box = (
            min(1.0, max(0.0, x1 * inv_w)),
            min(1.0, max(0.0, y1 * inv_h)),
            min(1.0, max(0.0, x2 * inv_w)),
            min(1.0, max(0.0, y2 * inv_h)),
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
                bbox=[x1, y1, x2 - x1, y2 - y1],
            )
        )
    return results


def _run_onnx_detection(image: Image.Image, cfg: DetectorConfig, tier: AcceleratorTier) -> list[DetectionResult]:
    session = get_session(tier)
    model_input = _prepare_input(image, cfg)
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: model_input})
    if not outputs:
        return []
    return _parse_yolo_output(outputs[0], cfg)


def run_detection(image_b64: str) -> DetectionOutput:
    cfg = load_detector_config()
    runtime_cfg = load_runtime_config()
    tier = choose_accelerator(runtime_cfg)

    image = _decode_image(image_b64)

    if tier == AcceleratorTier.CORAL:
        try:
            raw = run_coral_inference(
                image,
                model_path=cfg.edgetpu_model_path,
                input_width=cfg.input_width,
                input_height=cfg.input_height,
            )
            return DetectionOutput(tier=AcceleratorTier.CORAL, detections=_parse_yolo_output(raw, cfg))
        except CoralUnavailableError as exc:
            logger.warning("Coral Edge TPU unavailable; falling back to ONNX tier: %s", exc)
            tier = choose_fallback_accelerator(runtime_cfg)

    if tier not in (AcceleratorTier.GPU, AcceleratorTier.CPU):
        tier = AcceleratorTier.CPU

    return DetectionOutput(tier=tier, detections=_run_onnx_detection(image, cfg, tier))
