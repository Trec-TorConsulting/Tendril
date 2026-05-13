"""Outdoor intelligence API — GDD, frost dates, moon phase, manual weather entry."""

from __future__ import annotations

import math
from datetime import UTC, date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, Tent, WeatherReading

router = APIRouter()

# GDD base temperature (°F) — cannabis standard
GDD_BASE_TEMP_F = 50.0


# ---------- Schemas ----------


class ManualWeatherCreate(BaseModel):
    rainfall_in: float | None = None
    temp_high_f: float | None = None
    temp_low_f: float | None = None
    wind_speed_mph: float | None = None
    notes: str | None = None


class GDDResponse(BaseModel):
    grow_id: str
    accumulated_gdd: float
    target_gdd: float | None
    progress_pct: float | None
    daily_log: list[dict]


class FrostDatesResponse(BaseModel):
    tent_id: str
    latitude: float
    longitude: float
    last_spring_frost: str
    first_fall_frost: str
    frost_free_days: int
    hardiness_zone: str


class MoonPhaseResponse(BaseModel):
    phase: str
    illumination_pct: float
    days_until_new: int
    days_until_full: int
    planting_recommendation: str


# ---------- Frost Date Lookup ----------

# Approximate US frost dates by latitude band (simplified — in production use a proper API)
FROST_DATE_TABLE = [
    # (min_lat, max_lat, last_spring_frost_mmdd, first_fall_frost_mmdd, zone)
    (25, 30, "02-15", "12-01", "9b-10a"),
    (30, 33, "03-01", "11-15", "8b-9a"),
    (33, 36, "03-15", "11-01", "7b-8a"),
    (36, 39, "04-01", "10-15", "6b-7a"),
    (39, 42, "04-15", "10-01", "5b-6a"),
    (42, 45, "05-01", "09-25", "4b-5a"),
    (45, 48, "05-15", "09-15", "3b-4a"),
    (48, 55, "06-01", "09-01", "2b-3a"),
]


def _lookup_frost_dates(lat: float) -> tuple[str, str, str]:
    for min_lat, max_lat, spring, fall, zone in FROST_DATE_TABLE:
        if min_lat <= abs(lat) < max_lat:
            return spring, fall, zone
    # Default for unknown latitudes
    return "04-15", "10-15", "6a"


# ---------- Moon Phase Calculation ----------


def _moon_phase(dt: datetime) -> dict:
    """Calculate approximate moon phase using a simple synodic period algorithm."""
    # Known new moon reference: Jan 6, 2000 18:14 UTC
    ref = datetime(2000, 1, 6, 18, 14, tzinfo=UTC)
    synodic = 29.53058867  # days
    days_since = (dt - ref).total_seconds() / 86400
    cycle = days_since / synodic
    phase_frac = cycle - math.floor(cycle)  # 0.0 = new, 0.5 = full

    illumination = round((1 - math.cos(2 * math.pi * phase_frac)) / 2 * 100, 1)
    days_until_new = round((1 - phase_frac) * synodic)
    days_until_full = round(((0.5 - phase_frac) % 1.0) * synodic)

    if phase_frac < 0.03 or phase_frac > 0.97:
        name = "New Moon"
        rec = "Ideal for root development work, transplanting, and starting seeds. Gravitational pull draws water up."
    elif phase_frac < 0.22:
        name = "Waxing Crescent"
        rec = "Good for planting leafy crops and above-ground annuals. Increasing moonlight stimulates leaf growth."
    elif phase_frac < 0.28:
        name = "First Quarter"
        rec = "Strong leaf growth period. Good for transplanting and pruning for growth."
    elif phase_frac < 0.47:
        name = "Waxing Gibbous"
        rec = "Plant flowering and fruiting crops. Increasing light energy supports bud development."
    elif phase_frac < 0.53:
        name = "Full Moon"
        rec = "Peak moisture in soil. Harvest for peak potency. Avoid pruning — sap flow is high."
    elif phase_frac < 0.72:
        name = "Waning Gibbous"
        rec = "Good for harvesting, drying, and curing. Decreasing moisture aids drying process."
    elif phase_frac < 0.78:
        name = "Last Quarter"
        rec = "Ideal for soil work, composting, cover crop planting. Energy moves to roots."
    else:
        name = "Waning Crescent"
        rec = "Rest period. Plan and prepare. Minimal planting. Good for soil testing."

    return {
        "phase": name,
        "illumination_pct": illumination,
        "days_until_new": days_until_new,
        "days_until_full": days_until_full,
        "planting_recommendation": rec,
    }


# ---------- Endpoints ----------


@router.get("/{tent_id}/frost-dates", response_model=FrostDatesResponse)
async def get_frost_dates(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get estimated frost dates and hardiness zone based on tent location."""
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    if tent.latitude is None or tent.longitude is None:
        raise HTTPException(status_code=400, detail="Tent location (lat/lng) not set")

    spring, fall, zone = _lookup_frost_dates(tent.latitude)
    year = datetime.now(UTC).year
    spring_date = datetime.strptime(f"{year}-{spring}", "%Y-%m-%d").date()
    fall_date = datetime.strptime(f"{year}-{fall}", "%Y-%m-%d").date()
    frost_free = (fall_date - spring_date).days

    return FrostDatesResponse(
        tent_id=str(tent_id),
        latitude=tent.latitude,
        longitude=tent.longitude,
        last_spring_frost=f"{year}-{spring}",
        first_fall_frost=f"{year}-{fall}",
        frost_free_days=frost_free,
        hardiness_zone=zone,
    )


@router.get("/{tent_id}/moon")
async def get_moon_phase(
    tent_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get current moon phase and planting recommendations."""
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")
    return _moon_phase(datetime.now(UTC))


@router.post("/{tent_id}/manual", status_code=201)
async def log_manual_weather(
    tent_id: UUID,
    body: ManualWeatherCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log manual weather observation (rain gauge, temperature, etc.)."""
    tent = await session.get(Tent, tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")

    # Convert to the existing WeatherReading format
    reading = WeatherReading(
        tenant_id=user.tenant_id,
        tent_id=tent_id,
        temperature_c=((body.temp_high_f - 32) * 5 / 9) if body.temp_high_f else None,
        humidity_pct=None,
        precipitation_mm=(body.rainfall_in * 25.4) if body.rainfall_in else None,
        wind_speed_kmh=(body.wind_speed_mph * 1.60934) if body.wind_speed_mph else None,
        uv_index=None,
        weather_code=None,
        forecast={"source": "manual", "notes": body.notes},
    )
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return {"id": str(reading.id), "recorded_at": reading.recorded_at.isoformat()}


@router.get("/{grow_id}/gdd", response_model=GDDResponse)
async def get_growing_degree_days(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Calculate accumulated Growing Degree Days for a grow cycle."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    tent = await session.get(Tent, grow.tent_id)
    if tent is None:
        raise HTTPException(status_code=404, detail="Tent not found")

    # Fetch weather history since grow start
    result = await session.execute(
        select(WeatherReading)
        .where(
            WeatherReading.tent_id == tent.id,
            WeatherReading.recorded_at >= grow.started_at,
        )
        .order_by(WeatherReading.recorded_at)
    )
    readings = result.scalars().all()

    # Calculate daily GDD contributions
    daily_log = []
    total_gdd = 0.0

    # Group readings by date, use max/min temp
    daily_temps: dict[date, list[float]] = {}
    for r in readings:
        if r.temperature_c is not None:
            day = r.recorded_at.date()
            temp_f = r.temperature_c * 9 / 5 + 32
            daily_temps.setdefault(day, []).append(temp_f)

    for day in sorted(daily_temps.keys()):
        temps = daily_temps[day]
        high = max(temps)
        low = min(temps)
        avg = (high + low) / 2
        gdd = max(0, avg - GDD_BASE_TEMP_F)
        total_gdd += gdd
        daily_log.append(
            {
                "date": day.isoformat(),
                "high_f": round(high, 1),
                "low_f": round(low, 1),
                "gdd": round(gdd, 1),
                "cumulative_gdd": round(total_gdd, 1),
            }
        )

    # Target GDD based on strain flowering days (rough: 15 GDD/day avg * flowering_days)
    target_gdd = None
    progress_pct = None
    if grow.settings and grow.settings.get("target_gdd"):
        target_gdd = grow.settings["target_gdd"]
        progress_pct = round(min(100, total_gdd / target_gdd * 100), 1) if target_gdd > 0 else None

    return GDDResponse(
        grow_id=str(grow_id),
        accumulated_gdd=round(total_gdd, 1),
        target_gdd=target_gdd,
        progress_pct=progress_pct,
        daily_log=daily_log,
    )
