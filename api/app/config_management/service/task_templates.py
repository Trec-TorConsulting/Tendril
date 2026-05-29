"""Task template service — reads from DB with caching."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config_management import TaskTemplate
from app.config_management.service.cache import cache


async def get_templates(
    session: AsyncSession,
    grow_type_slug: str | None = None,
    stage_slug: str | None = None,
    category: str | None = None,
) -> list[dict]:
    """Get task templates, optionally filtered by grow type, stage, or category."""
    cache_key = f"templates:{grow_type_slug}:{stage_slug}:{category}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    stmt = select(TaskTemplate).options(selectinload(TaskTemplate.steps))

    if category:
        stmt = stmt.where(TaskTemplate.category == category)
    if stage_slug:
        stmt = stmt.where((TaskTemplate.stage_slug == stage_slug) | (TaskTemplate.stage_slug.is_(None)))

    result = await session.execute(stmt)
    templates = result.scalars().all()

    # Filter by grow type in Python (ARRAY contains is awkward in SQLAlchemy)
    if grow_type_slug:
        templates = [t for t in templates if t.grow_type_slugs is None or grow_type_slug in t.grow_type_slugs]

    data = [_serialize_template(t) for t in templates]
    cache.set(cache_key, data)
    return data


async def get_template(session: AsyncSession, template_id: str) -> dict | None:
    """Get a single task template by ID."""
    cache_key = f"template:{template_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    from uuid import UUID

    result = await session.execute(
        select(TaskTemplate).where(TaskTemplate.id == UUID(template_id)).options(selectinload(TaskTemplate.steps))
    )
    template = result.scalar_one_or_none()
    if template is None:
        return None

    data = _serialize_template(template)
    cache.set(cache_key, data)
    return data


def _serialize_template(t: TaskTemplate) -> dict:
    return {
        "id": str(t.id),
        "name": t.name,
        "description": t.description,
        "category": t.category,
        "grow_type_slugs": t.grow_type_slugs,
        "grow_types": t.grow_type_slugs,
        "frequency_hours": t.frequency_hours,
        "stage_slug": t.stage_slug,
        "stages": [t.stage_slug] if t.stage_slug else None,
        "priority": t.priority,
        "routine": t.routine,
        "estimated_minutes": t.estimated_minutes,
        "brief": t.description or "",
        "detail": None,
        "is_system": t.is_system,
        "steps": [
            {
                "id": str(s.id),
                "order": s.order,
                "instruction": s.instruction,
                "duration_minutes": s.duration_minutes,
                "optional": s.optional,
            }
            for s in sorted(t.steps, key=lambda x: x.order)
        ],
    }


async def get_all_templates(session: AsyncSession) -> list[dict]:
    """Get all task templates (no filters). Used by task_generator for full template set."""
    cache_key = "templates:all"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    stmt = select(TaskTemplate).options(selectinload(TaskTemplate.steps))
    result = await session.execute(stmt)
    templates = result.scalars().all()

    if not templates:
        return []

    data = [_serialize_template(t) for t in templates]
    cache.set(cache_key, data)
    return data
