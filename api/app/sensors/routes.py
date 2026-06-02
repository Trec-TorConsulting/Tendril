"""Sensor readings API — CRUD + latest + drift analysis."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import BucketSensorReading
from app.pagination import PaginatedResponse, PaginationParams, paginate

logger = logging.getLogger("tendril.sensors")

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

    For RDWC header buckets, the reading is automatically propagated to all site buckets.
    """
    from app.integrations.connectors.base import propagate_header_bucket_readings

    data = body.model_dump()
    # Auto-derive EC↔PPM when only one is provided
    if data.get("ec") is not None and data.get("ppm") is None:
        data["ppm"] = round(data["ec"] * 500.0, 1)
    elif data.get("ppm") is not None and data.get("ec") is None:
        data["ec"] = round(data["ppm"] / 500.0, 3)
    reading = BucketSensorReading(tenant_id=user.tenant_id, **data)
    session.add(reading)
    await session.flush()  # Flush to get the reading in the session

    # Propagate header readings to all site buckets in RDWC grows
    await propagate_header_bucket_readings(session, str(reading.bucket_id), reading)

    await session.commit()
    await session.refresh(reading)

    # Evaluate real-time alerts in background (non-blocking)
    try:
        from app.automation.engine import (
            evaluate_composite_alerts,
            evaluate_critical_alerts,
            evaluate_trend_alerts,
        )
        from app.grows.models import Bucket, GrowCycle

        bucket = await session.get(Bucket, reading.bucket_id)
        if bucket and bucket.grow_cycle_id:
            grow = await session.get(GrowCycle, bucket.grow_cycle_id)
            if grow:
                await evaluate_critical_alerts(session, grow.grow_type, user.tenant_id, grow.id, reading)
                await evaluate_composite_alerts(session, grow.grow_type, user.tenant_id, grow.id, reading)
                await evaluate_trend_alerts(session, grow.grow_type, user.tenant_id, grow.id, reading.bucket_id)
    except Exception:
        logger.debug("Alert evaluation failed for reading %s", reading.id, exc_info=True)

    return reading


@router.get("", response_model=PaginatedResponse[SensorReadingResponse])
async def list_readings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    bucket_id: UUID | None = None,
):
    """List bucket sensor readings with optional bucket filtering."""
    q = (
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == user.tenant_id)
        .order_by(desc(BucketSensorReading.recorded_at))
    )
    if bucket_id:
        q = q.where(BucketSensorReading.bucket_id == bucket_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/latest/{bucket_id}", response_model=SensorReadingResponse | None)
async def get_latest_reading(
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the most recent sensor reading for a bucket."""
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == user.tenant_id)
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
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    result = await session.execute(
        select(BucketSensorReading)
        .where(BucketSensorReading.tenant_id == user.tenant_id)
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


@router.get("/{reading_id}", response_model=SensorReadingResponse)
async def get_reading(
    reading_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single sensor reading by ID."""
    reading = await session.get(BucketSensorReading, reading_id)
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
    reading = await session.get(BucketSensorReading, reading_id)
    if reading is None:
        raise HTTPException(status_code=404, detail="Sensor reading not found")
    await session.delete(reading)
    await session.commit()
