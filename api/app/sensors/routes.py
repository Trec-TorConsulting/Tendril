"""Sensor readings API — bucket-level CRUD + latest + drift analysis.

This module is HTTP-only. All persistence, EC↔PPM derivation,
RDWC propagation, alert evaluation, and drift math live in
``app.sensors.service``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.sensors import service

router = APIRouter()


class SensorReadingCreate(BaseModel):
    bucket_id: UUID
    device_id: str | None = None
    water_temp_f: float | None = None
    ph: float | None = None
    ec: float | None = None
    ppm: float | None = None
    water_level_pct: float | None = None
    dissolved_oxygen: float | None = None
    orp: float | None = None
    salinity: float | None = None
    specific_gravity: float | None = None
    battery_pct: float | None = None
    flow_rate: float | None = None
    mist_pressure: float | None = None
    soil_moisture: float | None = None
    soil_temp: float | None = None
    runoff_ph: float | None = None
    runoff_ec: float | None = None
    # ambient_temp_f and ambient_humidity moved to tent-level readings
    # (POST /tent-sensors). Kept in response for backward compat.


class SensorReadingResponse(BaseModel):
    id: UUID
    bucket_id: UUID
    device_id: str | None
    water_temp_f: float | None
    ph: float | None
    ec: float | None
    ppm: float | None
    water_level_pct: float | None
    dissolved_oxygen: float | None
    orp: float | None
    salinity: float | None
    specific_gravity: float | None
    battery_pct: float | None
    flow_rate: float | None
    mist_pressure: float | None
    soil_moisture: float | None
    soil_temp: float | None
    runoff_ph: float | None
    runoff_ec: float | None
    ambient_temp_f: float | None
    ambient_humidity: float | None
    recorded_at: datetime
    model_config = {"from_attributes": True}


@router.post("", response_model=SensorReadingResponse, status_code=201)
async def create_reading(
    body: SensorReadingCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Record a new bucket sensor reading (pH, EC, temperature, etc.).

    For RDWC header buckets, the reading is automatically propagated to all
    site buckets. Real-time alerts (critical/composite/trend) are evaluated
    best-effort and never block ingest.
    """
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    return await service.create_bucket_reading(session, tenant_id=user.tenant_id, data=body.model_dump())


@router.get("", response_model=PaginatedResponse[SensorReadingResponse])
async def list_readings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    bucket_id: UUID | None = None,
):
    """List bucket sensor readings with optional bucket filtering."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    q = service.list_bucket_readings_query(tenant_id=user.tenant_id, bucket_id=bucket_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/latest/{bucket_id}", response_model=SensorReadingResponse | None)
async def get_latest_reading(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the most recent sensor reading for a bucket."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    return await service.get_latest_bucket_reading(session, tenant_id=user.tenant_id, bucket_id=bucket_id)


@router.get("/drift/{bucket_id}")
async def get_drift(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    hours: int = Query(default=24, le=168),
):
    """Get pH / EC / ORP drift over the specified hours for a bucket."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    stats = await service.compute_bucket_drift(session, tenant_id=user.tenant_id, bucket_id=bucket_id, hours=hours)
    return {
        "bucket_id": str(bucket_id),
        "hours": hours,
        **stats,
    }


@router.get("/{reading_id}", response_model=SensorReadingResponse)
async def get_reading(
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single sensor reading by ID."""
    reading = await service.get_bucket_reading(session, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    return reading


@router.delete("/{reading_id}", status_code=204)
async def delete_reading(
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a sensor reading."""
    reading = await service.get_bucket_reading(session, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    await service.delete_bucket_reading(session, reading)
