from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.inference import DetectorConfig, _get_session_cached, get_session
from app.runtime import AcceleratorTier


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


if __name__ == "__main__":
    unittest.main()
