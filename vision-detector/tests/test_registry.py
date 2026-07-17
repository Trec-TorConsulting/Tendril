from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.registry import (
    ManifestError,
    ModelManifest,
    load_active_manifest,
    load_manifest_document,
    parse_manifest,
    validate_compatibility,
)

_VALID = {
    "version": "v3",
    "onnx_key": "vision/models/v3/model.onnx",
    "edge_tpu_storage_key": "vision/models/v3/model_edgetpu.tflite",
    "input_width": 640,
    "input_height": 640,
    "class_map": {"0": "pest_disease", "1": "bud"},
}


class ManifestParsingTests(unittest.TestCase):
    def test_parse_valid_manifest(self) -> None:
        manifest = parse_manifest(_VALID)
        self.assertIsInstance(manifest, ModelManifest)
        self.assertEqual(manifest.version, "v3")
        self.assertEqual(manifest.onnx_key, "vision/models/v3/model.onnx")
        self.assertEqual(manifest.edgetpu_key, "vision/models/v3/model_edgetpu.tflite")
        self.assertEqual(manifest.class_map, {0: "pest_disease", 1: "bud"})

    def test_missing_version_rejected(self) -> None:
        data = {**_VALID}
        data.pop("version")
        with self.assertRaises(ManifestError):
            parse_manifest(data)

    def test_missing_all_keys_rejected(self) -> None:
        data = {**_VALID}
        data.pop("onnx_key")
        data.pop("edge_tpu_storage_key")
        with self.assertRaises(ManifestError):
            parse_manifest(data)

    def test_empty_class_map_rejected(self) -> None:
        data = {**_VALID, "class_map": {}}
        with self.assertRaises(ManifestError):
            parse_manifest(data)

    def test_incompatible_input_size_rejected(self) -> None:
        manifest = ModelManifest(
            version="v3",
            onnx_key="k",
            edgetpu_key="",
            input_width=0,
            input_height=640,
            class_map={0: "x"},
        )
        with self.assertRaises(ManifestError):
            validate_compatibility(manifest)


class ManifestLoadingTests(unittest.TestCase):
    def test_load_document_from_local_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "active.json"
            path.write_text(json.dumps(_VALID), encoding="utf-8")
            document = load_manifest_document(manifest_path=str(path), manifest_key="", local_path="/tmp/x.json")
        self.assertEqual(document, _VALID)

    def test_load_document_none_when_unconfigured(self) -> None:
        document = load_manifest_document(manifest_path="", manifest_key="", local_path="/tmp/x.json")
        self.assertIsNone(document)

    def test_load_active_manifest_from_env_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "active.json"
            path.write_text(json.dumps(_VALID), encoding="utf-8")
            with patch.dict(os.environ, {"VISION_MODEL_MANIFEST_PATH": str(path)}, clear=False):
                manifest = load_active_manifest()
        assert manifest is not None
        self.assertEqual(manifest.version, "v3")


if __name__ == "__main__":
    unittest.main()
