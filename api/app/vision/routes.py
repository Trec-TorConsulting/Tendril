from __future__ import annotations

import asyncio
import base64
from typing import Annotated, Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_permission
from app.auth.permissions import GROW_READ, PHOTO_READ
from app.grows.models import GrowPhoto, Tent, TentCamera
from app.grows.tent_routes import _fetch_camera_image
from app.storage import get_photo as s3_get
from app.vision.client import VisionDetectorClient
from app.vision.contracts import VisionProfile

router = APIRouter()


class VisionScanRequest(BaseModel):
    image_base64: str
    profile: VisionProfile = VisionProfile.TENT_OVERVIEW
    source: str
    source_ref: str


class VisionDetectionBoxResponse(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]


class VisionScanResponse(BaseModel):
    model_version: str | None
    accelerator_tier: str
    detections: list[VisionDetectionBoxResponse]
    message: str | None = None


def get_vision_detector_client() -> VisionDetectorClient:
    return VisionDetectorClient.from_settings()


def _to_scan_response(model_response: Any) -> VisionScanResponse:
    return VisionScanResponse(
        model_version=model_response.model_version,
        accelerator_tier=model_response.accelerator_tier.value,
        detections=[
            VisionDetectionBoxResponse(
                class_name=item.class_name,
                confidence=item.confidence,
                bbox=item.bbox.as_list(),
            )
            for item in model_response.detections
        ],
        message=model_response.message,
    )


@router.post("/scan", response_model=VisionScanResponse)
async def scan_image(
    payload: VisionScanRequest,
    _user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> VisionScanResponse:
    model_response = await client.scan_image(
        image_base64=payload.image_base64,
        profile=payload.profile,
        source=payload.source,
        source_ref=payload.source_ref,
    )
    return _to_scan_response(model_response)


@router.post("/scan/tent/{tent_id}", response_model=VisionScanResponse)
async def scan_tent_snapshot(
    tent_id: UUID,
    _user: Annotated[CurrentUser, Depends(require_permission(GROW_READ))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
    profile: VisionProfile = VisionProfile.TENT_OVERVIEW,
) -> VisionScanResponse:
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")

    result = await session.execute(
        select(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.is_primary.is_(True)).limit(1)
    )
    camera = result.scalar_one_or_none()

    camera_url = camera.url if camera else tent.camera_url
    camera_type = camera.camera_type if camera else "http_snapshot"
    if not camera_url:
        raise HTTPException(status_code=404, detail="No camera configured for this tent")

    try:
        image_bytes = await _fetch_camera_image(camera_url, camera_type)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail=f"Camera unavailable: {exc}") from exc

    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    model_response = await client.scan_image(
        image_base64=image_b64,
        profile=profile,
        source="tent",
        source_ref=str(tent_id),
    )
    return _to_scan_response(model_response)


@router.post("/scan/photo/{photo_id}", response_model=VisionScanResponse)
async def scan_grow_photo(
    photo_id: UUID,
    user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
    profile: VisionProfile = VisionProfile.PHOTO_SCAN,
) -> VisionScanResponse:
    photo = await session.get(GrowPhoto, photo_id)
    if photo is None or photo.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Photo not found")

    loop = asyncio.get_running_loop()
    try:
        image_bytes, _ = await loop.run_in_executor(None, s3_get, photo.storage_key)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to retrieve photo") from None

    image_b64 = base64.b64encode(image_bytes).decode("ascii")
    model_response = await client.scan_image(
        image_base64=image_b64,
        profile=profile,
        source="photo",
        source_ref=str(photo_id),
    )
    return _to_scan_response(model_response)


@router.get("/healthz")
async def vision_healthz(
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> dict[str, Any]:
    return await client.healthz()
