"""Tent sensor readings API — ambient temp & humidity at the tent level."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import TentSensorReading

router = APIRouter()


class TentReadingCreate(BaseModel):
    tent_id: UUID
    device_id: str | None = None
    ambient_temp_f: float | None = None
    ambient_humidity: float | None = None


class TentReadingResponse(BaseModel):
    id: UUID
    tent_id: UUID
    device_id: str | None
    ambient_temp_f: float | None
    ambient_humidity: float | None
    recorded_at: datetime
    model_config = {"from_attributes": True}


@router.post("", response_model=TentReadingResponse, status_code=201)
async def create_tent_reading(
    body: TentReadingCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    reading = TentSensorReading(tenant_id=user.tenant_id, **body.model_dump())
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


@router.get("", response_model=list[TentReadingResponse])
async def list_tent_readings(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    tent_id: UUID | None = None,
    limit: int = Query(default=50, le=500),
):
    q = select(TentSensorReading).order_by(desc(TentSensorReading.recorded_at)).limit(limit)
    if tent_id:
        q = q.where(TentSensorReading.tent_id == tent_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/latest/{tent_id}", response_model=TentReadingResponse | None)
async def get_latest_tent_reading(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(
        select(TentSensorReading)
        .where(TentSensorReading.tent_id == tent_id)
        .order_by(desc(TentSensorReading.recorded_at))
        .limit(1)
    )
    return result.scalar_one_or_none()


@router.get("/trends/{tent_id}")
async def get_tent_trends(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    hours: int = Query(default=24, le=168),
):
    """Get ambient temp & humidity trends for a tent over the specified hours."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    result = await session.execute(
        select(TentSensorReading)
        .where(TentSensorReading.tent_id == tent_id)
        .where(TentSensorReading.recorded_at >= cutoff)
        .order_by(TentSensorReading.recorded_at)
    )
    readings = result.scalars().all()

    def stats(values: list[float]) -> dict | None:
        if not values:
            return None
        return {
            "min": round(min(values), 1),
            "max": round(max(values), 1),
            "avg": round(sum(values) / len(values), 1),
            "count": len(values),
        }

    temps = [r.ambient_temp_f for r in readings if r.ambient_temp_f is not None]
    humids = [r.ambient_humidity for r in readings if r.ambient_humidity is not None]

    return {
        "tent_id": str(tent_id),
        "hours": hours,
        "reading_count": len(readings),
        "ambient_temp_f": stats(temps),
        "ambient_humidity": stats(humids),
    }
