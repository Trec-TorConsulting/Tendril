from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.runtime import AcceleratorTier, build_runtime_state, load_runtime_config


class RuntimeStateTests(unittest.TestCase):
    def test_unavailable_without_version(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VISION_MODEL_VERSION": "",
                "VISION_MODEL_PATH": "/tmp/model.onnx",
                "VISION_MODEL_STORAGE_KEY": "",
            },
            clear=False,
        ):
            cfg = load_runtime_config()
            state = build_runtime_state(cfg)
            self.assertIsNone(state.model_version)
            self.assertEqual(state.accelerator_tier, AcceleratorTier.UNAVAILABLE)

    def test_available_with_storage_key_and_cpu_fallback(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VISION_MODEL_VERSION": "v1",
                "VISION_MODEL_PATH": "",
                "VISION_MODEL_STORAGE_KEY": "vision/models/v1/model.onnx",
                "VISION_CORAL_ENABLED": "true",
                "VISION_GPU_ENABLED": "false",
                "VISION_CPU_ENABLED": "true",
                "NVIDIA_VISIBLE_DEVICES": "",
            },
            clear=False,
        ):
            with patch("app.runtime.Path.exists", return_value=False):
                cfg = load_runtime_config()
                state = build_runtime_state(cfg)

        self.assertEqual(state.model_version, "v1")
        self.assertEqual(state.accelerator_tier, AcceleratorTier.CPU)

    def test_gpu_selected_when_visible_devices_present(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VISION_MODEL_VERSION": "v2",
                "VISION_MODEL_PATH": "/tmp/model.onnx",
                "VISION_MODEL_STORAGE_KEY": "",
                "VISION_CORAL_ENABLED": "false",
                "VISION_GPU_ENABLED": "true",
                "VISION_CPU_ENABLED": "true",
                "NVIDIA_VISIBLE_DEVICES": "all",
            },
            clear=False,
        ):
            cfg = load_runtime_config()
            state = build_runtime_state(cfg)

        self.assertEqual(state.model_version, "v2")
        self.assertEqual(state.accelerator_tier, AcceleratorTier.GPU)


if __name__ == "__main__":
    unittest.main()
