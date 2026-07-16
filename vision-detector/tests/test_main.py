from __future__ import annotations

import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import healthz, metrics_prometheus


class MainEndpointsTests(unittest.TestCase):
    def test_healthz_reports_storage_key_source(self) -> None:
        with patch.dict(
            os.environ,
            {
                "VISION_MODEL_VERSION": "v-test",
                "VISION_MODEL_PATH": "",
                "VISION_MODEL_STORAGE_KEY": "vision/models/v-test/model.onnx",
                "VISION_CORAL_ENABLED": "false",
                "VISION_GPU_ENABLED": "false",
                "VISION_CPU_ENABLED": "true",
            },
            clear=False,
        ):
            payload = asyncio.run(healthz())

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["model_version"], "v-test")
        self.assertEqual(payload["model_source"], "storage_key")
        self.assertFalse(payload["model_path_configured"])
        self.assertTrue(payload["model_storage_key_configured"])

    def test_metrics_prometheus_is_exposed(self) -> None:
        response = asyncio.run(metrics_prometheus())

        self.assertIn("text/plain", response.media_type)
        body = response.body.decode("utf-8")
        self.assertIn("vision_detector_requests_total", body)
        self.assertIn("vision_detector_requests_by_tier_total", body)


if __name__ == "__main__":
    unittest.main()
