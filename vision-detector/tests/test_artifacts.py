from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.artifacts import ArtifactError, _use_ssl, resolve_model_path


class ArtifactsTests(unittest.TestCase):
    def setUp(self) -> None:
        resolve_model_path.cache_clear()

    def test_use_ssl_defaults_from_endpoint(self) -> None:
        with patch.dict(os.environ, {"S3_USE_SSL": ""}, clear=False):
            self.assertTrue(_use_ssl("https://minio.example"))
            self.assertFalse(_use_ssl("http://minio.example"))

    def test_resolve_model_path_requires_env(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ArtifactError):
                resolve_model_path(storage_key="vision/model.onnx", local_path="/tmp/model.onnx")

    def test_resolve_model_path_uses_existing_file_without_download(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "model.onnx"
            local_path.write_bytes(b"onnx-bytes")

            with patch.dict(
                os.environ,
                {
                    "S3_ENDPOINT": "http://minio.local:9000",
                    "S3_ACCESS_KEY": "minio",
                    "S3_SECRET_KEY": "secret",
                    "S3_BUCKET": "vision-models",
                },
                clear=False,
            ):
                with patch("app.artifacts.boto3.client") as client_factory:
                    result = resolve_model_path(storage_key="vision/model.onnx", local_path=str(local_path))

            self.assertEqual(result, str(local_path))
            client_factory.assert_not_called()

    def test_resolve_model_path_downloads_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = Path(tmpdir) / "nested" / "model.onnx"
            fake_client = Mock()

            with patch.dict(
                os.environ,
                {
                    "S3_ENDPOINT": "http://minio.local:9000",
                    "S3_ACCESS_KEY": "minio",
                    "S3_SECRET_KEY": "secret",
                    "S3_BUCKET": "vision-models",
                    "S3_REGION": "us-east-2",
                    "S3_USE_SSL": "false",
                },
                clear=False,
            ):
                with patch("app.artifacts.boto3.client", return_value=fake_client) as client_factory:
                    result = resolve_model_path(storage_key="vision/model.onnx", local_path=str(local_path))

            self.assertEqual(result, str(local_path))
            fake_client.download_file.assert_called_once_with("vision-models", "vision/model.onnx", str(local_path))
            self.assertTrue(client_factory.called)


if __name__ == "__main__":
    unittest.main()
