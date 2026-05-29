"""Treatment service — reads from plant_health_treatments table."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_management.service.cache import cache
from app.grows.models import PlantHealthTreatment


async def search_treatments(session: AsyncSession, query: str) -> list[dict]:
    """Search treatments by name, symptoms, or category."""
    cache_key = f"treatments:search:{query.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    like_pattern = f"%{query}%"
    result = await session.execute(
        select(PlantHealthTreatment)
        .where(
            or_(
                PlantHealthTreatment.name.ilike(like_pattern),
                PlantHealthTreatment.category.ilike(like_pattern),
                PlantHealthTreatment.summary.ilike(like_pattern),
            )
        )
        .limit(20)
    )
    treatments = result.scalars().all()
    data = [_serialize_treatment(t) for t in treatments]
    cache.set(cache_key, data)
    return data


async def list_by_category(session: AsyncSession, category: str) -> list[dict]:
    """List treatments filtered by category."""
    cache_key = f"treatments:category:{category.lower()}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(select(PlantHealthTreatment).where(PlantHealthTreatment.category == category))
    treatments = result.scalars().all()
    data = [_serialize_treatment(t) for t in treatments]
    cache.set(cache_key, data)
    return data


async def list_all(session: AsyncSession) -> list[dict]:
    """List all treatments."""
    cache_key = "treatments:all"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(select(PlantHealthTreatment))
    treatments = result.scalars().all()
    data = [_serialize_treatment(t) for t in treatments]
    cache.set(cache_key, data)
    return data


async def get_treatment(session: AsyncSession, treatment_id: str) -> dict | None:
    """Get a single treatment by ID (string ID, not UUID)."""
    cache_key = f"treatment:{treatment_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(select(PlantHealthTreatment).where(PlantHealthTreatment.id == treatment_id))
    treatment = result.scalar_one_or_none()
    if treatment is None:
        return None

    data = _serialize_treatment(treatment)
    cache.set(cache_key, data)
    return data


def _serialize_treatment(t: PlantHealthTreatment) -> dict:
    return {
        "id": t.id,
        "name": t.name,
        "category": t.category,
        "aka": t.aka or [],
        "summary": t.summary,
        "symptoms": t.symptoms or [],
        "identification_tips": t.identification_tips or [],
        "causes": t.causes or [],
        "severity_criteria": t.severity_criteria or {},
        "treatments": t.treatments or {},
        "prevention": t.prevention or [],
        "recovery_time": t.recovery_time or "",
        "commonly_confused_with": t.commonly_confused_with or [],
    }
