from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_permission
from app.auth.permissions import GROW_READ, GROW_UPDATE, PHOTO_READ
from app.grows.models import GrowCycle, GrowPhoto, Tent, TentCamera, VisionDetection, VisionModelRegistry
from app.grows.tent_routes import _fetch_camera_image
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.storage import get_photo as s3_get
from app.vision.client import VisionDetectorClient
from app.vision.contracts import VisionProfile
from app.vision.drafts import propose_vision_drafts

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


class VisionDetectionResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID | None
    source: str
    source_ref: str | None
    image_storage_key: str | None
    class_name: str
    confidence: float
    bbox: list[float]
    model_version: str
    accelerator_tier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VisionModelRegistryResponse(BaseModel):
    id: UUID
    version: str
    edge_tpu_storage_key: str | None
    fallback_storage_key: str | None
    class_map: dict
    input_width: int
    input_height: int
    metrics: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VisionModelActivateRequest(BaseModel):
    version: str


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


async def _resolve_tent_grow_cycle_id(session: AsyncSession, tent_id: UUID) -> UUID | None:
    result = await session.execute(
        select(GrowCycle.id)
        .where(GrowCycle.tent_id == tent_id, GrowCycle.deleted_at.is_(None))
        .order_by(desc(GrowCycle.started_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _persist_detections(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    source: str,
    source_ref: str,
    image_storage_key: str | None,
    model_response: Any,
) -> None:
    if model_response.model_version is None:
        return
    rows = [
        VisionDetection(
            tenant_id=tenant_id,
            grow_cycle_id=grow_cycle_id,
            source=source,
            source_ref=source_ref,
            image_storage_key=image_storage_key,
            class_name=item.class_name,
            confidence=item.confidence,
            bbox=item.bbox.as_list(),
            model_version=model_response.model_version,
            accelerator_tier=model_response.accelerator_tier.value,
        )
        for item in model_response.detections
    ]
    if rows:
        session.add_all(rows)
        await session.commit()


@router.post("/scan", response_model=VisionScanResponse)
async def scan_image(
    payload: VisionScanRequest,
    user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> VisionScanResponse:
    model_response = await client.scan_image(
        image_base64=payload.image_base64,
        profile=payload.profile,
        source=payload.source,
        source_ref=payload.source_ref,
    )
    await _persist_detections(
        session,
        tenant_id=user.tenant_id,
        grow_cycle_id=None,
        source=payload.source,
        source_ref=payload.source_ref,
        image_storage_key=None,
        model_response=model_response,
    )
    return _to_scan_response(model_response)


@router.post("/scan/tent/{tent_id}", response_model=VisionScanResponse)
async def scan_tent_snapshot(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(require_permission(GROW_READ))],
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
    grow_cycle_id = await _resolve_tent_grow_cycle_id(session, tent_id)
    await _persist_detections(
        session,
        tenant_id=tent.tenant_id,
        grow_cycle_id=grow_cycle_id,
        source="tent",
        source_ref=str(tent_id),
        image_storage_key=None,
        model_response=model_response,
    )
    await propose_vision_drafts(
        session,
        tenant_id=tent.tenant_id,
        grow_cycle_id=grow_cycle_id,
        source="tent",
        source_ref=str(tent_id),
        image_storage_key=None,
        detections=model_response.detections,
        model_version=model_response.model_version,
        actor_user_id=user.user_id,
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
    await _persist_detections(
        session,
        tenant_id=photo.tenant_id,
        grow_cycle_id=photo.grow_cycle_id,
        source="photo",
        source_ref=str(photo_id),
        image_storage_key=photo.storage_key,
        model_response=model_response,
    )
    await propose_vision_drafts(
        session,
        tenant_id=photo.tenant_id,
        grow_cycle_id=photo.grow_cycle_id,
        source="photo",
        source_ref=str(photo_id),
        image_storage_key=photo.storage_key,
        detections=model_response.detections,
        model_version=model_response.model_version,
        actor_user_id=user.user_id,
    )
    return _to_scan_response(model_response)


@router.get("/detections", response_model=PaginatedResponse[VisionDetectionResponse])
async def list_detections(
    _user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: UUID | None = None,
    source: str | None = None,
):
    query = select(VisionDetection).order_by(desc(VisionDetection.created_at))
    if grow_cycle_id is not None:
        query = query.where(VisionDetection.grow_cycle_id == grow_cycle_id)
    if source:
        query = query.where(VisionDetection.source == source)
    items, total = await paginate(session, query, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/models", response_model=list[VisionModelRegistryResponse])
async def list_models(
    _user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(select(VisionModelRegistry).order_by(desc(VisionModelRegistry.created_at)))
    return result.scalars().all()


@router.post("/models/activate", response_model=VisionModelRegistryResponse)
async def activate_model(
    body: VisionModelActivateRequest,
    user: Annotated[CurrentUser, Depends(require_permission(GROW_UPDATE))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(
        select(VisionModelRegistry).where(VisionModelRegistry.version == body.version).limit(1)
    )
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="Model version not found")
    existing = await session.execute(select(VisionModelRegistry).where(VisionModelRegistry.is_active.is_(True)))
    for row in existing.scalars().all():
        row.is_active = False
    target.is_active = True
    target.updated_at = datetime.now(UTC)
    session.add(target)
    await session.commit()
    await session.refresh(target)
    return target


@router.get("/healthz")
async def vision_healthz(
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> dict[str, Any]:
    return await client.healthz()
