"""Sensor readings API — CRUD + latest + drift analysis."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import BucketSensorReading

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
    flow_rate: float | None = None
    mist_pressure: float | None = None
    soil_moisture: float | None = None
    soil_temp: float | None = None
    runoff_ph: float | None = None
    runoff_ec: float | None = None
    ambient_temp_f: float | None = None
    ambient_humidity: float | None = None


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
    reading = BucketSensorReading(tenant_id=user.tenant_id, **body.model_dump())
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


@router.get("", response_model=list[SensorReadingResponse])
async def list_readings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    bucket_id: UUID | None = None,
    limit: int = Query(default=50, le=500),
):
    q = select(BucketSensorReading).order_by(desc(BucketSensorReading.recorded_at)).limit(limit)
    if bucket_id:
        q = q.where(BucketSensorReading.bucket_id == bucket_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/latest/{bucket_id}", response_model=SensorReadingResponse | None)
async def get_latest_reading(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .order_by(desc(BucketSensorReading.recorded_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/drift/{bucket_id}")
async def get_drift(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    hours: int = Query(default=24, le=168),
):
    """Get pH and EC drift over the specified hours for a bucket."""
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.bucket_id == bucket_id)
        .where(BucketSensorReading.recorded_at >= cutoff)
        .order_by(BucketSensorReading.recorded_at)
    )
    readings = result.scalars().all()

    ph_values = [r.ph for r in readings if r.ph is not None]
    ec_values = [r.ec for r in readings if r.ec is not None]

    def drift_stats(values: list[float]) -> dict | None:
        if len(values) < 2:
            return None
        return {
            "min": min(values),
            "max": max(values),
            "first": values[0],
            "last": values[-1],
            "delta": round(values[-1] - values[0], 3),
            "count": len(values),
        }

    return {
        "bucket_id": str(bucket_id),
        "hours": hours,
        "ph": drift_stats(ph_values),
        "ec": drift_stats(ec_values),
    }
