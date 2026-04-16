"""Weather API — current conditions, forecast, history, alerts for outdoor/greenhouse tents."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.grows.models import Tent, WeatherReading
from app.weather.client import fetch_weather, evaluate_weather_alerts

router = APIRouter()


@router.get("/{tent_id}/current")
async def get_current_weather(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get live weather data for an outdoor/greenhouse tent."""
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if tent.environment_type == "indoor":
        raise HTTPException(status_code=400, detail="Weather data only for outdoor/greenhouse tents")
    if tent.latitude is None or tent.longitude is None:
        raise HTTPException(status_code=400, detail="Tent location (lat/lng) not set")

    data = await fetch_weather(tent.latitude, tent.longitude)
    alerts = evaluate_weather_alerts(data["current"], data["forecast"])

    return {
        "tent_id": str(tent_id),
        "current": data["current"],
        "alerts": alerts,
    }


@router.get("/{tent_id}/forecast")
async def get_forecast(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get 7-day weather forecast for an outdoor/greenhouse tent."""
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if tent.environment_type == "indoor":
        raise HTTPException(status_code=400, detail="Weather data only for outdoor/greenhouse tents")
    if tent.latitude is None or tent.longitude is None:
        raise HTTPException(status_code=400, detail="Tent location (lat/lng) not set")

    data = await fetch_weather(tent.latitude, tent.longitude)
    return {
        "tent_id": str(tent_id),
        "forecast": data["forecast"],
    }


@router.get("/{tent_id}/history")
async def get_weather_history(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    limit: int = 48,
):
    """Get stored weather reading history for a tent."""
    result = await session.execute(
        select(WeatherReading)
        .where(WeatherReading.tent_id == tent_id)
        .order_by(desc(WeatherReading.recorded_at))
        .limit(limit)
    )
    readings = result.scalars().all()
    return [
        {
            "temperature_c": r.temperature_c,
            "humidity_pct": r.humidity_pct,
            "precipitation_mm": r.precipitation_mm,
            "wind_speed_kmh": r.wind_speed_kmh,
            "uv_index": r.uv_index,
            "weather_code": r.weather_code,
            "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
        }
        for r in readings
    ]
