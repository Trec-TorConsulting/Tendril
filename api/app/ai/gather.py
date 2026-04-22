"""Gather comprehensive grow data for AI prompts."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import (
    Bucket,
    BucketSensorReading,
    DoseProfile,
    FeedingSchedule,
    GrowCycle,
    HealthEval,
    JournalEntry,
    Strain,
    Tent,
    TentSensorReading,
    WeatherReading,
)

logger = logging.getLogger("tendril.ai.gather")


async def gather_grow_data(
    session: AsyncSession,
    grow: GrowCycle,
    *,
    include_camera: bool = True,
    sensor_history_hours: int = 24,
    journal_limit: int = 10,
) -> dict:
    """Gather ALL available data for a grow cycle into a single dict.

    Used by health-check (Gemini) and chat (Ollama) to build rich context.
    """
    data: dict = {
        "grow_name": grow.name,
        "grow_type": grow.grow_type,
        "stage": grow.stage,
        "status": grow.status,
        "started_at": grow.started_at.isoformat() if grow.started_at else None,
        "milestones": grow.milestones,
        "settings": grow.settings,
        "notes": grow.notes,
    }

    # ── Buckets ──────────────────────────────────────────────────
    buckets = (
        await session.execute(
            select(Bucket)
            .where(Bucket.grow_cycle_id == grow.id)
            .order_by(Bucket.position)
        )
    ).scalars().all()

    bucket_list = []
    for b in buckets:
        bd: dict = {
            "position": b.position,
            "label": b.label,
            "strain_name": b.strain_name,
            "growth_stage": b.growth_stage,
            "status": b.status,
            "volume_gallons": b.volume_gallons,
        }
        # Include full strain profile when linked
        if b.strain_id:
            strain = b.strain or await session.get(Strain, b.strain_id)
            if strain:
                bd["strain_profile"] = {
                    "name": strain.name,
                    "genetics": strain.genetics,
                    "flowering_days": strain.flowering_days,
                    "thc_pct": strain.thc_pct,
                    "cbd_pct": strain.cbd_pct,
                    "terpene_profile": strain.terpene_profile,
                    "notes": strain.notes,
                }
        bucket_list.append(bd)
    data["buckets"] = bucket_list

    # ── Latest sensors per bucket ────────────────────────────────
    bucket_sensors: dict = {}
    for b in buckets:
        reading = (
            await session.execute(
                select(BucketSensorReading)
                .where(BucketSensorReading.bucket_id == b.id)
                .order_by(desc(BucketSensorReading.recorded_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if reading:
            bucket_sensors[b.position] = {
                k: getattr(reading, k)
                for k in (
                    "ph", "ec", "ppm", "water_temp_f", "dissolved_oxygen",
                    "water_level_pct",
                    "soil_moisture", "soil_temp", "runoff_ph", "runoff_ec",
                    "flow_rate", "mist_pressure",
                )
                if getattr(reading, k) is not None
            }
            bucket_sensors[b.position]["recorded_at"] = reading.recorded_at.isoformat()
    data["bucket_sensors"] = bucket_sensors

    # ── Tent ambient readings (shared across all buckets) ────────
    tent_ambient: dict | None = None
    tent_ambient_reading = (
        await session.execute(
            select(TentSensorReading)
            .where(TentSensorReading.tent_id == grow.tent_id)
            .order_by(desc(TentSensorReading.recorded_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if tent_ambient_reading:
        tent_ambient = {}
        if tent_ambient_reading.ambient_temp_f is not None:
            tent_ambient["ambient_temp_f"] = tent_ambient_reading.ambient_temp_f
        if tent_ambient_reading.ambient_humidity is not None:
            tent_ambient["ambient_humidity"] = tent_ambient_reading.ambient_humidity
        if tent_ambient:
            tent_ambient["recorded_at"] = tent_ambient_reading.recorded_at.isoformat()
    data["tent_ambient"] = tent_ambient

    # ── Sensor trends (24h from first bucket) ────────────────────
    if buckets:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=sensor_history_hours)
        trends = (
            await session.execute(
                select(BucketSensorReading)
                .where(
                    BucketSensorReading.bucket_id == buckets[0].id,
                    BucketSensorReading.recorded_at >= cutoff,
                )
                .order_by(BucketSensorReading.recorded_at)
            )
        ).scalars().all()
        if len(trends) > 1:
            trend_data: dict = {"reading_count": len(trends), "period_hours": sensor_history_hours}
            for field in ("ph", "ec", "ppm", "water_temp_f", "dissolved_oxygen", "water_level_pct",
                          "soil_moisture", "soil_temp",
                          "runoff_ph", "runoff_ec", "flow_rate", "mist_pressure"):
                vals = [getattr(r, field) for r in trends if getattr(r, field) is not None]
                if vals:
                    trend_data[f"{field}_min"] = round(min(vals), 2)
                    trend_data[f"{field}_max"] = round(max(vals), 2)
                    trend_data[f"{field}_avg"] = round(sum(vals) / len(vals), 2)
            data["sensor_trends"] = trend_data
        else:
            data["sensor_trends"] = None
    else:
        data["sensor_trends"] = None

    # ── Tent ambient trends (24h) ────────────────────────────────
    cutoff = datetime.now(timezone.utc) - timedelta(hours=sensor_history_hours)
    tent_trends_rows = (
        await session.execute(
            select(TentSensorReading)
            .where(
                TentSensorReading.tent_id == grow.tent_id,
                TentSensorReading.recorded_at >= cutoff,
            )
            .order_by(TentSensorReading.recorded_at)
        )
    ).scalars().all()
    if len(tent_trends_rows) > 1:
        ambient_trend: dict = {"reading_count": len(tent_trends_rows), "period_hours": sensor_history_hours}
        for field in ("ambient_temp_f", "ambient_humidity"):
            vals = [getattr(r, field) for r in tent_trends_rows if getattr(r, field) is not None]
            if vals:
                ambient_trend[f"{field}_min"] = round(min(vals), 2)
                ambient_trend[f"{field}_max"] = round(max(vals), 2)
                ambient_trend[f"{field}_avg"] = round(sum(vals) / len(vals), 2)
        data["ambient_trends"] = ambient_trend
    else:
        data["ambient_trends"] = None

    # ── Feeding schedules ────────────────────────────────────────
    feeds = (
        await session.execute(
            select(FeedingSchedule)
            .where(FeedingSchedule.grow_cycle_id == grow.id)
            .order_by(FeedingSchedule.stage)
        )
    ).scalars().all()
    data["feeding_schedules"] = [
        {
            "name": f.name,
            "stage": f.stage,
            "nutrients": f.nutrients,
            "target_ppm": f.target_ppm,
            "target_ec": f.target_ec,
            "notes": f.notes,
        }
        for f in feeds
    ]

    # ── Dose profiles ────────────────────────────────────────────
    doses = (
        await session.execute(
            select(DoseProfile).where(DoseProfile.grow_cycle_id == grow.id)
        )
    ).scalars().all()
    data["dose_profiles"] = [
        {
            "name": d.name,
            "dose_type": d.dose_type,
            "dose_ml": d.dose_ml,
            "enabled": d.enabled,
        }
        for d in doses
    ]

    # ── Recent journal entries ───────────────────────────────────
    if buckets:
        bucket_ids = [b.id for b in buckets]
        journals = (
            await session.execute(
                select(JournalEntry)
                .where(JournalEntry.bucket_id.in_(bucket_ids))
                .order_by(desc(JournalEntry.created_at))
                .limit(journal_limit)
            )
        ).scalars().all()
        data["journal_entries"] = [
            {
                "event_type": j.event_type,
                "content": j.content,
                "payload": j.payload if j.payload else None,
                "created_at": j.created_at.isoformat(),
            }
            for j in journals
        ]
    else:
        data["journal_entries"] = []

    # ── Previous health evaluation ───────────────────────────────
    prev = (
        await session.execute(
            select(HealthEval)
            .where(HealthEval.grow_cycle_id == grow.id)
            .order_by(desc(HealthEval.created_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if prev:
        data["previous_eval"] = {
            "score": prev.score,
            "issues": prev.issues,
            "actions": prev.actions,
            "raw_analysis": prev.raw_analysis,
            "source": prev.source,
            "created_at": prev.created_at.isoformat(),
        }
    else:
        data["previous_eval"] = None

    # ── Tent + weather ───────────────────────────────────────────
    tent = await session.get(Tent, grow.tent_id)
    data["tent_name"] = tent.name if tent else None
    data["tent_size"] = tent.size if tent else None
    data["environment_type"] = tent.environment_type if tent else None
    data["tent_equipment"] = tent.equipment if tent else []
    data["tent_notes"] = tent.notes if tent else None
    data["camera_url"] = tent.camera_url if tent else None

    weather = None
    if tent and tent.environment_type in ("outdoor", "greenhouse"):
        w = (
            await session.execute(
                select(WeatherReading)
                .where(WeatherReading.tent_id == tent.id)
                .order_by(desc(WeatherReading.recorded_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if w:
            weather = {
                k: getattr(w, k)
                for k in (
                    "temperature_c", "humidity_pct", "precipitation_mm",
                    "wind_speed_kmh", "uv_index",
                )
                if getattr(w, k) is not None
            }
    data["weather"] = weather

    # ── Pending tasks ────────────────────────────────────────────
    from app.commercial.models import Task
    pending_tasks = (
        await session.execute(
            select(Task)
            .where(
                Task.grow_cycle_id == grow.id,
                Task.status.in_(["pending", "in_progress"]),
            )
            .order_by(Task.due_date.asc().nullslast())
            .limit(20)
        )
    ).scalars().all()
    data["pending_tasks"] = [
        {
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "source": t.source,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "status": t.status,
        }
        for t in pending_tasks
    ]

    # Recently completed tasks (last 7 days)
    from datetime import timedelta as _td
    recent_cutoff = datetime.now(timezone.utc) - _td(days=7)
    completed_tasks = (
        await session.execute(
            select(Task)
            .where(
                Task.grow_cycle_id == grow.id,
                Task.status == "completed",
                Task.completed_at >= recent_cutoff,
            )
            .order_by(Task.completed_at.desc())
            .limit(10)
        )
    ).scalars().all()
    data["completed_tasks"] = [
        {
            "title": t.title,
            "category": t.category,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in completed_tasks
    ]

    # ── Camera image ─────────────────────────────────────────────
    camera_image = None
    if include_camera and tent and tent.camera_url:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(tent.camera_url)
                resp.raise_for_status()
                camera_image = resp.content
        except Exception:
            logger.warning("Failed to fetch camera snapshot from %s", tent.camera_url)
    data["camera_image"] = camera_image

    return data
