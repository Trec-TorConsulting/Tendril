from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import boto3
from botocore.client import Config


class ArtifactError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ArtifactError(f"{name} is required when loading model from S3/MinIO")
    return value


def _use_ssl(endpoint: str) -> bool:
    raw = os.environ.get("S3_USE_SSL", "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return endpoint.startswith("https://")


def download_object(*, storage_key: str, local_path: str, force: bool = False) -> str:
    """Download an object from S3/MinIO to ``local_path`` and return the path.

    Reuses an already-downloaded file unless ``force`` is set. Raises
    :class:`ArtifactError` when required S3 configuration is missing or the
    download fails.
    """
    endpoint = _required_env("S3_ENDPOINT")
    access_key = _required_env("S3_ACCESS_KEY")
    secret_key = _required_env("S3_SECRET_KEY")
    bucket = _required_env("S3_BUCKET")

    target = Path(local_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not force and target.exists() and target.stat().st_size > 0:
        return str(target)

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name=os.environ.get("S3_REGION", "us-east-1"),
        use_ssl=_use_ssl(endpoint),
    )

    try:
        client.download_file(bucket, storage_key, str(target))
    except Exception as exc:
        raise ArtifactError(f"failed to download model artifact s3://{bucket}/{storage_key}") from exc

    return str(target)


@lru_cache(maxsize=8)
def resolve_model_path(*, storage_key: str, local_path: str) -> str:
    return download_object(storage_key=storage_key, local_path=local_path)
