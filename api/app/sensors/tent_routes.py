"""Tent sensor readings API — ambient temp, humidity, VPD, CO2 at the tent level.

This module is HTTP-only. All persistence and trend extraction live in
``app.sensors.service``.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.sensors import service

router = APIRouter()


class TentReadingCreate(BaseModel):
    tent_id: UUID
    device_id: str | None = None
    ambient_temp_f: float | None = None
    ambient_humidity: float | None = None
    vpd: float | None = None
    co2: float | None = None
    lux: float | None = None
    dew_point_f: float | None = None
    par_ppfd: float | None = None
    voc: float | None = None
    air_pressure: float | None = None


class TentReadingResponse(BaseModel):
    id: UUID
    tent_id: UUID
    device_id: str | None
    ambient_temp_f: float | None
    ambient_humidity: float | None
    vpd: float | None = None
    co2: float | None = None
    lux: float | None = None
    dew_point_f: float | None = None
    par_ppfd: float | None = None
    voc: float | None = None
    air_pressure: float | None = None
    recorded_at: datetime
    model_config = {"from_attributes": True}


@router.post("", response_model=TentReadingResponse, status_code=201)
async def create_tent_reading(
    body: TentReadingCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Record a new tent-level sensor reading (temp, humidity, CO2, etc.)."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    return await service.create_tent_reading(session, tenant_id=user.tenant_id, data=body.model_dump())


@router.get("", response_model=PaginatedResponse[TentReadingResponse])
async def list_tent_readings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    tent_id: UUID | None = None,
):
    """List tent sensor readings with optional tent filtering."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    q = service.list_tent_readings_query(tenant_id=user.tenant_id, tent_id=tent_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/latest/{tent_id}", response_model=TentReadingResponse | None)
async def get_latest_tent_reading(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the most recent sensor reading for a tent."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    return await service.get_latest_tent_reading(session, tenant_id=user.tenant_id, tent_id=tent_id)


@router.get("/trends/{tent_id}")
async def get_tent_trends(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    hours: int = Query(default=24, le=168),
):
    """Get ambient temp & humidity trends for a tent over the specified hours."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    readings = await service.list_recent_tent_readings(session, tenant_id=user.tenant_id, tent_id=tent_id, since=cutoff)
    return {
        "timestamps": [r.recorded_at.isoformat() for r in readings],
        "temps": [r.ambient_temp_f for r in readings],
        "humidities": [r.ambient_humidity for r in readings],
        "vpd": [r.vpd for r in readings],
        "co2": [r.co2 for r in readings],
        "lux": [r.lux for r in readings],
    }


@router.get("/{reading_id}", response_model=TentReadingResponse)
async def get_tent_reading(
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single tent sensor reading by ID."""
    reading = await service.get_tent_reading(session, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Tent reading not found")
    return reading


@router.delete("/{reading_id}", status_code=204)
async def delete_tent_reading(
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a tent sensor reading."""
    reading = await service.get_tent_reading(session, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Tent reading not found")
    await service.delete_tent_reading(session, reading)
