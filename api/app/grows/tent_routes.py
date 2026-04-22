"""Tent CRUD API — tenant-scoped grow spaces."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.auth.jwt import decode_token
from app.database import async_session_factory
from app.grows.models import Tent

router = APIRouter()


class EquipmentItem(BaseModel):
    type: str  # exhaust_fan, inline_fan, oscillating_fan, carbon_filter, humidifier, dehumidifier, heater, ac_unit, co2_system, controller, custom
    brand: str | None = None
    model: str | None = None
    specs: str | None = None  # e.g. "402 CFM", "16 inch"
    quantity: int = 1


class TentCreate(BaseModel):
    name: str
    environment_type: str = "indoor"
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


@router.get("", response_model=list[TentResponse])
async def list_tents(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(select(Tent).order_by(Tent.created_at.desc()))
    return result.scalars().all()


@router.get("/{tent_id}", response_model=TentResponse)
async def get_tent(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    tent = await session.get(Tent, tent_id)
    if tent is None:
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
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tent, field, value)
    await session.commit()
    await session.refresh(tent)
    return tent


@router.delete("/{tent_id}", status_code=204)
async def delete_tent(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    await session.delete(tent)
    await session.commit()


@router.get("/{tent_id}/camera-snapshot")
async def camera_snapshot(
    tent_id: UUID,
    token: str = Query(..., description="JWT access token"),
):
    """Proxy camera snapshot — accepts token as query param for <img> tags."""
    from jose import JWTError
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    tenant_id = payload["tid"]

    async with async_session_factory() as session:
        tid = str(tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid}'"))
        tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if not tent.camera_url:
        raise HTTPException(status_code=404, detail="No camera configured for this tent")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(tent.camera_url)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Camera fetch failed: {exc}")
    content_type = resp.headers.get("content-type", "image/jpeg")
    return Response(content=resp.content, media_type=content_type, headers={"Cache-Control": "no-store"})
