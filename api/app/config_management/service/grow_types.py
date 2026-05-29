"""Grow type config service — reads from normalized DB tables with caching."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config_management import (
    GrowTypeProfile,
    GrowTypeStage,
)
from app.config_management.service.cache import cache


async def list_profiles(session: AsyncSession) -> list[dict]:
    """List all grow type profiles (cached)."""
    cached = cache.get("profiles:all")
    if cached is not None:
        return cached

    result = await session.execute(select(GrowTypeProfile).order_by(GrowTypeProfile.name))
    profiles = result.scalars().all()
    data = [
        {
            "id": str(p.id),
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "sensor_kit": p.sensor_kit,
            "is_system": p.is_system,
        }
        for p in profiles
    ]
    cache.set("profiles:all", data)
    return data


async def get_profile(session: AsyncSession, slug: str) -> dict | None:
    """Get a single profile by slug with full relationships (cached)."""
    cache_key = f"profile:{slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(
        select(GrowTypeProfile)
        .where(GrowTypeProfile.slug == slug)
        .options(
            selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.environment),
            selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.nutrients),
            selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.watering),
            selectinload(GrowTypeProfile.equipment),
            selectinload(GrowTypeProfile.troubleshooting),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return None

    data = _serialize_profile(profile)
    cache.set(cache_key, data)
    return data


async def get_stage_config(session: AsyncSession, profile_slug: str, stage_slug: str) -> dict | None:
    """Get environment/nutrient/watering config for a specific stage."""
    cache_key = f"stage:{profile_slug}:{stage_slug}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(
        select(GrowTypeStage)
        .join(GrowTypeProfile)
        .where(GrowTypeProfile.slug == profile_slug, GrowTypeStage.slug == stage_slug)
        .options(
            selectinload(GrowTypeStage.environment),
            selectinload(GrowTypeStage.nutrients),
            selectinload(GrowTypeStage.watering),
        )
    )
    stage = result.scalar_one_or_none()
    if stage is None:
        return None

    data = _serialize_stage(stage)
    cache.set(cache_key, data)
    return data


async def get_full_config(session: AsyncSession, slug: str) -> dict | None:
    """Get the complete config for a grow type (profile + all stages + equipment + troubleshooting)."""
    return await get_profile(session, slug)


def _serialize_profile(profile: GrowTypeProfile) -> dict:
    data = {
        "id": str(profile.id),
        "name": profile.name,
        "slug": profile.slug,
        "description": profile.description,
        "sensor_kit": profile.sensor_kit,
        "ai_context_prompt": profile.ai_context_prompt,
        "is_system": profile.is_system,
        "stages": [_serialize_stage(s) for s in sorted(profile.stages, key=lambda x: x.order)],
        "equipment": [
            {
                "id": str(e.id),
                "item_name": e.item_name,
                "category": e.category,
                "required": e.required,
                "notes": e.notes,
            }
            for e in profile.equipment
        ],
        "troubleshooting": [
            {
                "id": str(t.id),
                "symptom": t.symptom,
                "cause": t.cause,
                "solution": t.solution,
                "severity": t.severity,
            }
            for t in profile.troubleshooting
        ],
    }
    # Merge extended_config fields at top level for API consumers
    if profile.extended_config:
        data.update(profile.extended_config)
    return data


def _serialize_stage(stage: GrowTypeStage) -> dict:
    env = stage.environment
    data = {
        "id": str(stage.id),
        "name": stage.name,
        "slug": stage.slug,
        "order": stage.order,
        "duration_days_min": stage.duration_days_min,
        "duration_days_max": stage.duration_days_max,
        "description": stage.description,
        "environment": None,
        "nutrients": [],
        "watering": None,
    }

    if env:
        data["environment"] = {
            "temp_min": env.temp_min,
            "temp_max": env.temp_max,
            "temp_ideal": env.temp_ideal,
            "humidity_min": env.humidity_min,
            "humidity_max": env.humidity_max,
            "humidity_ideal": env.humidity_ideal,
            "vpd_min": env.vpd_min,
            "vpd_max": env.vpd_max,
            "light_hours": env.light_hours,
            "light_ppfd_min": env.light_ppfd_min,
            "light_ppfd_max": env.light_ppfd_max,
            "co2_min": env.co2_min,
            "co2_max": env.co2_max,
            "water_temp_min": env.water_temp_min,
            "water_temp_max": env.water_temp_max,
        }

    if stage.nutrients:
        data["nutrients"] = [
            {
                "id": str(n.id),
                "week": n.week,
                "ec_min": n.ec_min,
                "ec_max": n.ec_max,
                "ec_target": n.ec_target,
                "ph_min": n.ph_min,
                "ph_max": n.ph_max,
                "ph_target": n.ph_target,
                "base_nutrients": n.base_nutrients,
                "supplements": n.supplements,
                "notes": n.notes,
            }
            for n in sorted(stage.nutrients, key=lambda x: x.week)
        ]

    if stage.watering:
        w = stage.watering
        data["watering"] = {
            "method": w.method,
            "frequency_hours": w.frequency_hours,
            "volume_ml": w.volume_ml,
            "runoff_target_pct": w.runoff_target_pct,
            "notes": w.notes,
        }

    return data
