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
from app.grows.models import Tent
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.utils.url_validation import validate_url_safe

router = APIRouter()


class EquipmentItem(BaseModel):
    type: str  # grow_light, exhaust_fan, inline_fan, oscillating_fan, air_pump, water_pump, water_chiller, carbon_filter, humidifier, dehumidifier, heater, ac_unit, co2_system, controller, custom
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
    q = select(Tent).where(Tent.deleted_at.is_(None), Tent.tenant_id == user.tenant_id).order_by(Tent.created_at.desc())
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{tent_id}", response_model=TentResponse)
async def get_tent(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
):
    """Proxy camera snapshot — uses HMAC-signed URLs for <img> tags."""
    from app.auth.signed_url import verify_signed_url
    tenant_id = verify_signed_url(request.url.path, sig, exp, tid)

    async with async_session_factory() as session:
        tid = str(tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid}'"))
        tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if not tent.camera_url:
        raise HTTPException(status_code=404, detail="No camera configured for this tent")
    validate_url_safe(tent.camera_url, allow_private=True)  # cameras are on local network
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(tent.camera_url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Camera fetch failed: {exc}")
    content_type = resp.headers.get("content-type", "image/jpeg")
    return Response(content=resp.content, media_type=content_type, headers={"Cache-Control": "no-store"})
