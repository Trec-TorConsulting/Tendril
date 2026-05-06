"""Tent CRUD API — tenant-scoped grow spaces."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import record_audit
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.database import async_session_factory
from app.grows.models import Tent, TentCamera
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.utils.url_validation import validate_url_safe

router = APIRouter()


class EquipmentItem(BaseModel):
    type: str  # e.g. grow_light, exhaust_fan, humidifier, etc.
    brand: str | None = None
    model: str | None = None
    specs: str | None = None  # e.g. "402 CFM", "16 inch"
    quantity: int = 1


class TentCreate(BaseModel):
    name: str = Field(max_length=255)
    environment_type: str = Field(default="indoor", max_length=255)
    size: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    camera_url: str | None = None
    equipment: list[EquipmentItem] | None = None
    notes: str | None = None


class TentUpdate(BaseModel):
    name: str | None = None
    environment_type: str | None = None
    size: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    camera_url: str | None = None
    equipment: list[EquipmentItem] | None = None
    notes: str | None = None


class TentResponse(BaseModel):
    id: UUID
    name: str
    environment_type: str
    size: str | None
    latitude: float | None
    longitude: float | None
    camera_url: str | None
    equipment: list[dict] | None
    notes: str | None
    model_config = {"from_attributes": True}


@router.post("", response_model=TentResponse, status_code=201)
async def create_tent(
    body: TentCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new grow tent."""
    tent = Tent(tenant_id=user.tenant_id, **body.model_dump())
    session.add(tent)
    await session.commit()
    await session.refresh(tent)
    return tent


@router.get("", response_model=PaginatedResponse[TentResponse])
async def list_tents(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all tents for the current tenant."""
    q = select(Tent).where(Tent.deleted_at.is_(None), Tent.tenant_id == user.tenant_id).order_by(Tent.created_at.desc())
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{tent_id}", response_model=TentResponse)
async def get_tent(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a tent by ID."""
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")
    return tent


@router.patch("/{tent_id}", response_model=TentResponse)
async def update_tent(
    tent_id: UUID,
    body: TentUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a tent's configuration."""
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tent, field, value)
    await session.commit()
    await session.refresh(tent)
    return tent


@router.delete("/{tent_id}", status_code=204)
async def delete_tent(
    tent_id: UUID,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a tent by ID."""
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")
    await record_audit(session, user.tenant_id, user.user_id, "delete", "tent", str(tent_id), request=request)
    tent.deleted_at = datetime.now(UTC)
    await session.commit()


@router.get("/{tent_id}/camera-snapshot")
async def camera_snapshot(
    tent_id: UUID,
    request: Request,
    sig: str = Query(..., description="HMAC signature"),
    exp: str = Query(..., description="Expiry timestamp"),
    tid: str = Query(..., description="Tenant ID"),
    camera_id: UUID | None = Query(None, description="Specific camera ID (default: primary)"),
):
    """Proxy camera snapshot — uses HMAC-signed URLs for <img> tags."""
    from app.auth.signed_url import verify_signed_url

    tenant_id = verify_signed_url(request.url.path, sig, exp, tid)

    async with async_session_factory() as session:
        tid_str = str(tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid_str}'"))
        tent = await session.get(Tent, tent_id)
        if tent is None:
            raise HTTPException(status_code=404, detail="Tent not found")

        # Resolve camera URL — from tent_cameras table or legacy camera_url
        camera_url = None
        if camera_id:
            cam = await session.get(TentCamera, camera_id)
            if cam and cam.tent_id == tent_id:
                camera_url = cam.url
        else:
            # Get primary camera from tent_cameras
            result = await session.execute(
                select(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.is_primary.is_(True)).limit(1)
            )
            cam = result.scalar_one_or_none()
            if cam:
                camera_url = cam.url
            elif tent.camera_url:
                camera_url = tent.camera_url  # Legacy fallback

    if not camera_url:
        raise HTTPException(status_code=404, detail="No camera configured for this tent")
    validate_url_safe(camera_url, allow_private=True)  # cameras are on local network
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(camera_url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Camera fetch failed: {exc}") from exc
    content_type = resp.headers.get("content-type", "image/jpeg")
    return Response(content=resp.content, media_type=content_type, headers={"Cache-Control": "no-store"})


@router.get("/{tent_id}/camera-snapshot-b64")
async def camera_snapshot_b64(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    camera_id: UUID | None = Query(None, description="Specific camera ID (default: primary)"),
):
    """Proxy camera snapshot — JWT-authenticated, returns base64 JSON for the frontend."""
    import base64

    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")

    camera_url = None
    if camera_id:
        cam = await session.get(TentCamera, camera_id)
        if cam and cam.tent_id == tent_id:
            camera_url = cam.url
    else:
        result = await session.execute(
            select(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.is_primary.is_(True)).limit(1)
        )
        cam = result.scalar_one_or_none()
        if cam:
            camera_url = cam.url
        elif tent.camera_url:
            camera_url = tent.camera_url

    if not camera_url:
        raise HTTPException(status_code=404, detail="No camera configured for this tent")
    validate_url_safe(camera_url, allow_private=True)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(camera_url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Camera fetch failed: {exc}") from exc
    image_b64 = base64.b64encode(resp.content).decode("ascii")
    return {"image_base64": image_b64, "timestamp": datetime.now(UTC).isoformat()}


# ---------- Camera CRUD ----------


class CameraCreate(BaseModel):
    label: str = Field(default="Camera", max_length=100)
    camera_type: str = Field(default="http_snapshot", max_length=20)
    url: str = Field(max_length=1024)
    sort_order: int = 0
    is_primary: bool = False


class CameraUpdate(BaseModel):
    label: str | None = None
    camera_type: str | None = None
    url: str | None = None
    sort_order: int | None = None
    is_primary: bool | None = None


class CameraResponse(BaseModel):
    id: UUID
    tent_id: UUID
    label: str
    camera_type: str
    url: str
    sort_order: int
    is_primary: bool
    model_config = {"from_attributes": True}


VALID_CAMERA_TYPES = {"http_snapshot", "rtsp", "frigate"}


@router.get("/{tent_id}/cameras", response_model=list[CameraResponse])
async def list_cameras(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all cameras for a tent, ordered by sort_order."""
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")
    result = await session.execute(
        select(TentCamera).where(TentCamera.tent_id == tent_id).order_by(TentCamera.sort_order)
    )
    return result.scalars().all()


@router.post("/{tent_id}/cameras", response_model=CameraResponse, status_code=201)
async def create_camera(
    tent_id: UUID,
    body: CameraCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Add a camera to a tent."""
    tent = await session.get(Tent, tent_id)
    if tent is None or tent.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if body.camera_type not in VALID_CAMERA_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid camera_type. Must be one of: {VALID_CAMERA_TYPES}")
    validate_url_safe(body.url, allow_private=True)

    # If first camera for tent, make it primary
    existing = await session.execute(select(TentCamera).where(TentCamera.tent_id == tent_id).limit(1))
    is_first = existing.scalar_one_or_none() is None

    camera = TentCamera(
        tent_id=tent_id,
        label=body.label,
        camera_type=body.camera_type,
        url=body.url,
        sort_order=body.sort_order,
        is_primary=body.is_primary or is_first,
    )
    session.add(camera)

    # If this camera is primary, demote others
    if camera.is_primary and not is_first:
        await session.execute(select(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.is_primary.is_(True)))
        from sqlalchemy import update

        await session.execute(
            update(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.id != camera.id).values(is_primary=False)
        )

    await session.commit()
    await session.refresh(camera)
    return camera


@router.patch("/{tent_id}/cameras/{camera_id}", response_model=CameraResponse)
async def update_camera(
    tent_id: UUID,
    camera_id: UUID,
    body: CameraUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a camera's configuration."""
    camera = await session.get(TentCamera, camera_id)
    if camera is None or camera.tent_id != tent_id:
        raise HTTPException(status_code=404, detail="Camera not found")

    data = body.model_dump(exclude_unset=True)
    if "camera_type" in data and data["camera_type"] not in VALID_CAMERA_TYPES:
        raise HTTPException(status_code=422, detail=f"Invalid camera_type. Must be one of: {VALID_CAMERA_TYPES}")
    if "url" in data:
        validate_url_safe(data["url"], allow_private=True)

    for field, value in data.items():
        setattr(camera, field, value)

    # If promoting to primary, demote others
    if data.get("is_primary"):
        from sqlalchemy import update

        await session.execute(
            update(TentCamera).where(TentCamera.tent_id == tent_id, TentCamera.id != camera_id).values(is_primary=False)
        )

    await session.commit()
    await session.refresh(camera)
    return camera


@router.delete("/{tent_id}/cameras/{camera_id}", status_code=204)
async def delete_camera(
    tent_id: UUID,
    camera_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a camera. If it was primary, promote next by sort_order."""
    camera = await session.get(TentCamera, camera_id)
    if camera is None or camera.tent_id != tent_id:
        raise HTTPException(status_code=404, detail="Camera not found")

    was_primary = camera.is_primary
    await session.delete(camera)
    await session.flush()

    # Promote next camera if deleted was primary
    if was_primary:
        result = await session.execute(
            select(TentCamera).where(TentCamera.tent_id == tent_id).order_by(TentCamera.sort_order).limit(1)
        )
        next_cam = result.scalar_one_or_none()
        if next_cam:
            next_cam.is_primary = True

    await session.commit()
