"""Active-model manifest resolution for the vision-detector.

The API owns the authoritative `vision_model_registry` table. When an operator
activates a model version it publishes an ``active.json`` manifest to the shared
MinIO/S3 bucket. The stateless detector reads that manifest (no DB access) to
learn which version is active, where its ONNX / Edge-TPU artifacts live, the
input resolution, and the class map. This keeps the service self-hostable and
lets it hot-refresh without a redeploy.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from app.artifacts import ArtifactError, download_object

MAX_INPUT_DIMENSION = 4096


class ManifestError(RuntimeError):
    """Raised when an active-model manifest is missing, malformed, or incompatible."""


@dataclass(frozen=True, slots=True)
class ModelManifest:
    version: str
    onnx_key: str
    edgetpu_key: str
    input_width: int
    input_height: int
    class_map: dict[int, str]


def _coerce_class_map(raw: object) -> dict[int, str]:
    if not isinstance(raw, dict) or not raw:
        raise ManifestError("manifest class_map must be a non-empty object")
    mapped: dict[int, str] = {}
    for key, value in raw.items():
        try:
            idx = int(key)
        except (TypeError, ValueError) as exc:
            raise ManifestError(f"invalid class_map key: {key!r}") from exc
        if not isinstance(value, str) or not value:
            raise ManifestError(f"invalid class_map value for key {key!r}")
        mapped[idx] = value
    return mapped


def parse_manifest(data: object) -> ModelManifest:
    """Parse and structurally validate a manifest document."""
    if not isinstance(data, dict):
        raise ManifestError("manifest must be a JSON object")

    version = str(data.get("version", "")).strip()
    if not version:
        raise ManifestError("manifest is missing a version")

    onnx_key = str(data.get("onnx_key", "") or data.get("fallback_storage_key", "")).strip()
    edgetpu_key = str(data.get("edgetpu_key", "") or data.get("edge_tpu_storage_key", "")).strip()
    if not onnx_key and not edgetpu_key:
        raise ManifestError("manifest must define at least one model artifact key")

    try:
        input_width = int(data.get("input_width", 640))
        input_height = int(data.get("input_height", 640))
    except (TypeError, ValueError) as exc:
        raise ManifestError("manifest input dimensions must be integers") from exc

    class_map = _coerce_class_map(data.get("class_map"))

    manifest = ModelManifest(
        version=version,
        onnx_key=onnx_key,
        edgetpu_key=edgetpu_key,
        input_width=input_width,
        input_height=input_height,
        class_map=class_map,
    )
    validate_compatibility(manifest)
    return manifest


def validate_compatibility(manifest: ModelManifest) -> None:
    """Refuse a manifest that is incompatible with the runtime.

    Keeps the previously loaded model in place by raising before the caller
    swaps configuration.
    """
    if not 0 < manifest.input_width <= MAX_INPUT_DIMENSION:
        raise ManifestError(f"manifest input_width out of range: {manifest.input_width}")
    if not 0 < manifest.input_height <= MAX_INPUT_DIMENSION:
        raise ManifestError(f"manifest input_height out of range: {manifest.input_height}")
    if not manifest.class_map:
        raise ManifestError("manifest class_map must not be empty")


def load_manifest_document(*, manifest_path: str, manifest_key: str, local_path: str) -> object | None:
    """Load the manifest JSON from a local path or S3/MinIO key.

    Returns ``None`` when neither source is configured (env-only mode).
    """
    if manifest_path:
        path = Path(manifest_path)
        if not path.exists():
            raise ManifestError(f"manifest path does not exist: {manifest_path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ManifestError("manifest file is not valid JSON") from exc

    if manifest_key:
        try:
            raw = download_object(storage_key=manifest_key, local_path=local_path)
        except ArtifactError as exc:
            raise ManifestError(str(exc)) from exc
        try:
            return json.loads(Path(raw).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ManifestError("downloaded manifest is not valid JSON") from exc

    return None


def load_active_manifest() -> ModelManifest | None:
    """Resolve the active-model manifest from configured sources, if any."""
    document = load_manifest_document(
        manifest_path=os.environ.get("VISION_MODEL_MANIFEST_PATH", "").strip(),
        manifest_key=os.environ.get("VISION_MODEL_MANIFEST_KEY", "").strip(),
        local_path=os.environ.get("VISION_MODEL_MANIFEST_LOCAL_PATH", "/tmp/vision/active.json").strip(),
    )
    if document is None:
        return None
    return parse_manifest(document)
