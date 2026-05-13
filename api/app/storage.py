"""S3 / MinIO storage helpers for photo uploads."""

from __future__ import annotations

import logging
import uuid
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

logger = logging.getLogger("tendril.storage")

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@lru_cache
def _get_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name="us-east-1",
    )


def ensure_bucket() -> None:
    """Create the photo bucket if it doesn't exist."""
    settings = get_settings()
    client = _get_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        client.create_bucket(Bucket=settings.s3_bucket)
        logger.info("Created S3 bucket %s", settings.s3_bucket)


def upload_photo(data: bytes, content_type: str, tenant_id: str, grow_id: str) -> str:
    """Upload image bytes to S3 and return the storage key."""
    settings = get_settings()
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[content_type]
    key = f"{tenant_id}/{grow_id}/{uuid.uuid4()}.{ext}"
    _get_client().put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return key


def get_photo(key: str) -> tuple[bytes, str]:
    """Download an image from S3. Returns (data, content_type)."""
    settings = get_settings()
    obj = _get_client().get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read(), obj["ContentType"]


def delete_photo(key: str) -> None:
    """Delete an image from S3."""
    settings = get_settings()
    _get_client().delete_object(Bucket=settings.s3_bucket, Key=key)
