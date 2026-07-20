from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.coral import CoralUnavailableError
from app.inference import (
    DetectionOutput,
    DetectionResult,
    DetectorConfig,
    _get_session_cached,
    _parse_yolo_output,
    get_session,
    run_detection,
)
from app.runtime import AcceleratorTier


def _config(**overrides: object) -> DetectorConfig:
    base = {
        "model_path": "/tmp/model.onnx",
        "edgetpu_model_path": "/tmp/model_edgetpu.tflite",
        "model_version": "v1",
        "input_width": 640,
        "input_height": 640,
        "confidence_threshold": 0.25,
        "iou_threshold": 0.45,
        "max_detections": 50,
        "class_map": {0: "pest_disease", 1: "bud"},
    }
    base.update(overrides)
    return DetectorConfig(**base)  # type: ignore[arg-type]



class InferenceSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        _get_session_cached.cache_clear()

    def test_get_session_uses_gpu_provider_when_available(self) -> None:
        cfg = DetectorConfig(
            model_path="/tmp/model-gpu.onnx",
            input_width=640,
            input_height=640,
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=50,
            class_map={0: "cannabis"},
        )

        with (
            patch("app.inference.load_detector_config", return_value=cfg),
            patch("app.inference.load_runtime_config"),
            patch("app.inference.choose_accelerator", return_value=AcceleratorTier.GPU),
            patch("app.inference.ort.get_available_providers", return_value=["CUDAExecutionProvider", "CPUExecutionProvider"]),
            patch("app.inference.ort.InferenceSession", return_value=object()) as session_ctor,
        ):
            _ = get_session()

        session_ctor.assert_called_once_with(
            "/tmp/model-gpu.onnx",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )

    def test_get_session_cache_keys_by_model_path(self) -> None:
        cfg_a = DetectorConfig(
            model_path="/tmp/model-a.onnx",
            input_width=640,
            input_height=640,
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=50,
            class_map={0: "cannabis"},
        )
        cfg_b = DetectorConfig(
            model_path="/tmp/model-b.onnx",
            input_width=640,
            input_height=640,
            confidence_threshold=0.25,
            iou_threshold=0.45,
            max_detections=50,
            class_map={0: "cannabis"},
        )

        with (
            patch("app.inference.load_runtime_config"),
            patch("app.inference.choose_accelerator", return_value=AcceleratorTier.CPU),
            patch("app.inference.ort.get_available_providers", return_value=["CPUExecutionProvider"]),
            patch("app.inference.ort.InferenceSession", return_value=object()) as session_ctor,
            patch("app.inference.load_detector_config", side_effect=[cfg_a, cfg_a, cfg_b]),
        ):
            _ = get_session()
            _ = get_session()
            _ = get_session()

        self.assertEqual(session_ctor.call_count, 2)


class ParseOutputTests(unittest.TestCase):
    def test_bbox_is_normalized_xywh(self) -> None:
        cfg = _config()
        # YOLO-style output: (batch, features=6, boxes=10). Box 0 is a centered
        # 64x64 box on a 640x640 input; remaining boxes stay below threshold.
        data = np.zeros((1, 6, 10), dtype=np.float32)
        data[0, 0, 0] = 320.0  # cx
        data[0, 1, 0] = 320.0  # cy
        data[0, 2, 0] = 64.0  # w
        data[0, 3, 0] = 64.0  # h
        data[0, 4, 0] = 0.9  # class 0 score
        data[0, 5, 0] = 0.1  # class 1 score

        results = _parse_yolo_output(data, cfg)

        self.assertEqual(len(results), 1)
        det = results[0]
        self.assertEqual(det.class_name, "pest_disease")
        self.assertAlmostEqual(det.confidence, 0.9, places=5)
        x, y, w, h = det.bbox
        for value in det.bbox:
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)
        self.assertAlmostEqual(x, 0.45, places=4)
        self.assertAlmostEqual(y, 0.45, places=4)
        self.assertAlmostEqual(w, 0.1, places=4)
        self.assertAlmostEqual(h, 0.1, places=4)


class RunDetectionTierTests(unittest.TestCase):
    def test_falls_back_to_cpu_when_coral_unavailable(self) -> None:
        cfg = _config()
        with (
            patch("app.inference.load_detector_config", return_value=cfg),
            patch("app.inference.load_runtime_config", return_value=object()),
            patch("app.inference.choose_accelerator", return_value=AcceleratorTier.CORAL),
            patch("app.inference.choose_fallback_accelerator", return_value=AcceleratorTier.CPU),
            patch("app.inference._decode_image", return_value=object()),
            patch(
                "app.inference.run_coral_inference",
                side_effect=CoralUnavailableError("no edge tpu device"),
            ),
            patch(
                "app.inference._run_onnx_detection",
                return_value=[DetectionResult(class_name="bud", confidence=0.8, bbox=[0.1, 0.1, 0.2, 0.2])],
            ) as onnx_mock,
        ):
            output = run_detection("")

        self.assertIsInstance(output, DetectionOutput)
        self.assertEqual(output.tier, AcceleratorTier.CPU)
        self.assertEqual(len(output.detections), 1)
        onnx_mock.assert_called_once()

    def test_uses_coral_tier_when_available(self) -> None:
        cfg = _config()
        with (
            patch("app.inference.load_detector_config", return_value=cfg),
            patch("app.inference.load_runtime_config", return_value=object()),
            patch("app.inference.choose_accelerator", return_value=AcceleratorTier.CORAL),
            patch("app.inference._decode_image", return_value=object()),
            patch("app.inference.run_coral_inference", return_value=np.zeros((1, 6, 4), dtype=np.float32)),
            patch(
                "app.inference._parse_yolo_output",
                return_value=[DetectionResult(class_name="pest_disease", confidence=0.95, bbox=[0.0, 0.0, 0.5, 0.5])],
            ),
            patch("app.inference._run_onnx_detection") as onnx_mock,
        ):
            output = run_detection("")

        self.assertEqual(output.tier, AcceleratorTier.CORAL)
        self.assertEqual(len(output.detections), 1)
        onnx_mock.assert_not_called()

    def test_cpu_tier_returned_without_coral(self) -> None:
        cfg = _config()
        with (
            patch("app.inference.load_detector_config", return_value=cfg),
            patch("app.inference.load_runtime_config", return_value=object()),
            patch("app.inference.choose_accelerator", return_value=AcceleratorTier.CPU),
            patch("app.inference._decode_image", return_value=object()),
            patch("app.inference.run_coral_inference") as coral_mock,
            patch(
                "app.inference._run_onnx_detection",
                return_value=[],
            ) as onnx_mock,
        ):
            output = run_detection("")

        self.assertEqual(output.tier, AcceleratorTier.CPU)
        coral_mock.assert_not_called()
        onnx_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
