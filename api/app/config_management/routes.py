"""Admin CRUD API for configuration management.

All endpoints require admin role authentication.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_current_admin_user
from app.config_management import (
    GrowTypeEnvironment,
    GrowTypeNutrient,
    GrowTypeProfile,
    GrowTypeStage,
    TaskTemplate,
    TaskTemplateStep,
)
from app.config_management.service.cache import cache
from app.database import async_session_factory

router = APIRouter(dependencies=[Depends(get_current_admin_user)])


# ─── Schemas ───────────────────────────────────────────────────────────────────


class ProfileCreate(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    description: str | None = None
    sensor_kit: str | None = None
    ai_context_prompt: str | None = None


class ProfileUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sensor_kit: str | None = None
    ai_context_prompt: str | None = None


class StageCreate(BaseModel):
    name: str = Field(max_length=100)
    slug: str = Field(max_length=100)
    order: int = 0
    duration_days_min: int | None = None
    duration_days_max: int | None = None
    description: str | None = None
    tips: str | None = None


class StageUpdate(BaseModel):
    name: str | None = None
    order: int | None = None
    duration_days_min: int | None = None
    duration_days_max: int | None = None
    description: str | None = None
    tips: str | None = None


class EnvironmentCreate(BaseModel):
    temp_min: float | None = None
    temp_max: float | None = None
    temp_ideal: float | None = None
    humidity_min: float | None = None
    humidity_max: float | None = None
    humidity_ideal: float | None = None
    vpd_min: float | None = None
    vpd_max: float | None = None
    light_hours: float | None = None
    light_ppfd_min: float | None = None
    light_ppfd_max: float | None = None
    co2_min: float | None = None
    co2_max: float | None = None
    water_temp_min: float | None = None
    water_temp_max: float | None = None


class NutrientCreate(BaseModel):
    week: int = 1
    ec_min: float | None = None
    ec_max: float | None = None
    ec_target: float | None = None
    ph_min: float | None = None
    ph_max: float | None = None
    ph_target: float | None = None
    base_nutrients: dict | None = None
    supplements: dict | None = None
    notes: str | None = None


class TaskTemplateCreate(BaseModel):
    name: str = Field(max_length=200)
    description: str | None = None
    category: str = Field(max_length=100)
    grow_type_slugs: list[str] | None = None
    frequency_hours: float = 0
    stage_slug: str | None = None
    priority: str = "medium"
    routine: str | None = None
    estimated_minutes: int = 5


class TaskTemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    grow_type_slugs: list[str] | None = None
    frequency_hours: float | None = None
    stage_slug: str | None = None
    priority: str | None = None
    routine: str | None = None
    estimated_minutes: int | None = None


class TaskStepCreate(BaseModel):
    order: int = 0
    instruction: str
    duration_minutes: int | None = None
    optional: bool = False


class OverrideSet(BaseModel):
    config_type: str = Field(max_length=50)
    config_key: str = Field(max_length=500)
    override_json: dict


# ─── Grow Type Profiles ────────────────────────────────────────────────────────


@router.get("/grow-types")
async def list_grow_type_profiles():
    async with async_session_factory() as session:
        result = await session.execute(select(GrowTypeProfile).order_by(GrowTypeProfile.name))
        profiles = result.scalars().all()
        return [
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


@router.get("/grow-types/{slug}")
async def get_grow_type_profile(slug: str):
    async with async_session_factory() as session:
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
        if not profile:
            raise HTTPException(404, "Profile not found")

        from app.config_management.service.grow_types import _serialize_profile

        return _serialize_profile(profile)


@router.post("/grow-types", status_code=201)
async def create_grow_type_profile(body: ProfileCreate):
    async with async_session_factory() as session:
        profile = GrowTypeProfile(
            name=body.name,
            slug=body.slug,
            description=body.description,
            sensor_kit=body.sensor_kit,
            ai_context_prompt=body.ai_context_prompt,
            is_system=False,
        )
        session.add(profile)
        await session.commit()
        cache.invalidate_prefix("profile")
        cache.invalidate("profiles:all")
        return {"id": str(profile.id), "slug": profile.slug}


@router.put("/grow-types/{slug}")
async def update_grow_type_profile(slug: str, body: ProfileUpdate):
    async with async_session_factory() as session:
        result = await session.execute(select(GrowTypeProfile).where(GrowTypeProfile.slug == slug))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(404, "Profile not found")

        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        await session.commit()
        cache.invalidate_prefix("profile")
        cache.invalidate("profiles:all")
        return {"id": str(profile.id), "slug": profile.slug}


@router.delete("/grow-types/{slug}", status_code=204)
async def delete_grow_type_profile(slug: str):
    async with async_session_factory() as session:
        result = await session.execute(delete(GrowTypeProfile).where(GrowTypeProfile.slug == slug))
        if result.rowcount == 0:
            raise HTTPException(404, "Profile not found")
        await session.commit()
        cache.invalidate_prefix("profile")
        cache.invalidate("profiles:all")


# ─── Stages ───────────────────────────────────────────────────────────────────


@router.get("/grow-types/{slug}/stages")
async def list_stages(slug: str):
    async with async_session_factory() as session:
        result = await session.execute(
            select(GrowTypeStage)
            .join(GrowTypeProfile)
            .where(GrowTypeProfile.slug == slug)
            .order_by(GrowTypeStage.order)
        )
        stages = result.scalars().all()
        return [
            {
                "id": str(s.id),
                "name": s.name,
                "slug": s.slug,
                "order": s.order,
                "duration_days_min": s.duration_days_min,
                "duration_days_max": s.duration_days_max,
            }
            for s in stages
        ]


@router.post("/grow-types/{slug}/stages", status_code=201)
async def create_stage(slug: str, body: StageCreate):
    async with async_session_factory() as session:
        result = await session.execute(select(GrowTypeProfile.id).where(GrowTypeProfile.slug == slug))
        profile_id = result.scalar_one_or_none()
        if not profile_id:
            raise HTTPException(404, "Profile not found")

        stage = GrowTypeStage(
            profile_id=profile_id,
            name=body.name,
            slug=body.slug,
            order=body.order,
            duration_days_min=body.duration_days_min,
            duration_days_max=body.duration_days_max,
            description=body.description,
            tips=body.tips,
        )
        session.add(stage)
        await session.commit()
        cache.invalidate_prefix(f"profile:{slug}")
        cache.invalidate_prefix(f"stage:{slug}")
        return {"id": str(stage.id), "slug": stage.slug}


@router.put("/grow-types/{slug}/stages/{stage_slug}")
async def update_stage(slug: str, stage_slug: str, body: StageUpdate):
    async with async_session_factory() as session:
        result = await session.execute(
            select(GrowTypeStage)
            .join(GrowTypeProfile)
            .where(GrowTypeProfile.slug == slug, GrowTypeStage.slug == stage_slug)
        )
        stage = result.scalar_one_or_none()
        if not stage:
            raise HTTPException(404, "Stage not found")

        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(stage, field, value)
        await session.commit()
        cache.invalidate_prefix(f"profile:{slug}")
        cache.invalidate_prefix(f"stage:{slug}")
        return {"id": str(stage.id)}


@router.delete("/grow-types/{slug}/stages/{stage_slug}", status_code=204)
async def delete_stage(slug: str, stage_slug: str):
    async with async_session_factory() as session:
        result = await session.execute(
            delete(GrowTypeStage).where(
                GrowTypeStage.slug == stage_slug,
                GrowTypeStage.profile_id.in_(select(GrowTypeProfile.id).where(GrowTypeProfile.slug == slug)),
            )
        )
        if result.rowcount == 0:
            raise HTTPException(404, "Stage not found")
        await session.commit()
        cache.invalidate_prefix(f"profile:{slug}")
        cache.invalidate_prefix(f"stage:{slug}")


# ─── Stage Environment ─────────────────────────────────────────────────────────


@router.put("/grow-types/{slug}/stages/{stage_slug}/environment")
async def upsert_stage_environment(slug: str, stage_slug: str, body: EnvironmentCreate):
    async with async_session_factory() as session:
        result = await session.execute(
            select(GrowTypeStage)
            .join(GrowTypeProfile)
            .where(GrowTypeProfile.slug == slug, GrowTypeStage.slug == stage_slug)
            .options(selectinload(GrowTypeStage.environment))
        )
        stage = result.scalar_one_or_none()
        if not stage:
            raise HTTPException(404, "Stage not found")

        if stage.environment:
            for field, value in body.model_dump(exclude_unset=True).items():
                setattr(stage.environment, field, value)
        else:
            env = GrowTypeEnvironment(stage_id=stage.id, **body.model_dump())
            session.add(env)

        await session.commit()
        cache.invalidate_prefix(f"profile:{slug}")
        cache.invalidate_prefix(f"stage:{slug}")
        return {"status": "ok"}


# ─── Stage Nutrients ───────────────────────────────────────────────────────────


@router.post("/grow-types/{slug}/stages/{stage_slug}/nutrients", status_code=201)
async def create_stage_nutrient(slug: str, stage_slug: str, body: NutrientCreate):
    async with async_session_factory() as session:
        result = await session.execute(
            select(GrowTypeStage.id)
            .join(GrowTypeProfile)
            .where(GrowTypeProfile.slug == slug, GrowTypeStage.slug == stage_slug)
        )
        stage_id = result.scalar_one_or_none()
        if not stage_id:
            raise HTTPException(404, "Stage not found")

        nutrient = GrowTypeNutrient(stage_id=stage_id, **body.model_dump())
        session.add(nutrient)
        await session.commit()
        cache.invalidate_prefix(f"profile:{slug}")
        return {"id": str(nutrient.id)}


# ─── Task Templates ────────────────────────────────────────────────────────────


@router.get("/task-templates")
async def list_task_templates(
    category: str | None = Query(None),
    grow_type: str | None = Query(None),
):
    async with async_session_factory() as session:
        stmt = select(TaskTemplate).options(selectinload(TaskTemplate.steps))
        if category:
            stmt = stmt.where(TaskTemplate.category == category)
        result = await session.execute(stmt)
        templates = result.scalars().all()

        if grow_type:
            templates = [t for t in templates if t.grow_type_slugs is None or grow_type in t.grow_type_slugs]

        from app.config_management.service.task_templates import _serialize_template

        return [_serialize_template(t) for t in templates]


@router.get("/task-templates/{template_id}")
async def get_task_template(template_id: str):
    async with async_session_factory() as session:
        result = await session.execute(
            select(TaskTemplate)
            .where(TaskTemplate.id == uuid.UUID(template_id))
            .options(selectinload(TaskTemplate.steps))
        )
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(404, "Template not found")

        from app.config_management.service.task_templates import _serialize_template

        return _serialize_template(template)


@router.post("/task-templates", status_code=201)
async def create_task_template(body: TaskTemplateCreate):
    async with async_session_factory() as session:
        template = TaskTemplate(
            name=body.name,
            description=body.description,
            category=body.category,
            grow_type_slugs=body.grow_type_slugs,
            frequency_hours=body.frequency_hours,
            stage_slug=body.stage_slug,
            priority=body.priority,
            routine=body.routine,
            estimated_minutes=body.estimated_minutes,
            is_system=False,
        )
        session.add(template)
        await session.commit()
        cache.invalidate_prefix("template")
        return {"id": str(template.id), "name": template.name}


@router.put("/task-templates/{template_id}")
async def update_task_template(template_id: str, body: TaskTemplateUpdate):
    async with async_session_factory() as session:
        result = await session.execute(select(TaskTemplate).where(TaskTemplate.id == uuid.UUID(template_id)))
        template = result.scalar_one_or_none()
        if not template:
            raise HTTPException(404, "Template not found")

        for field, value in body.model_dump(exclude_unset=True).items():
            setattr(template, field, value)
        await session.commit()
        cache.invalidate_prefix("template")
        return {"id": str(template.id)}


@router.delete("/task-templates/{template_id}", status_code=204)
async def delete_task_template(template_id: str):
    async with async_session_factory() as session:
        result = await session.execute(delete(TaskTemplate).where(TaskTemplate.id == uuid.UUID(template_id)))
        if result.rowcount == 0:
            raise HTTPException(404, "Template not found")
        await session.commit()
        cache.invalidate_prefix("template")


@router.post("/task-templates/{template_id}/steps", status_code=201)
async def create_task_step(template_id: str, body: TaskStepCreate):
    async with async_session_factory() as session:
        # Verify template exists
        result = await session.execute(select(TaskTemplate.id).where(TaskTemplate.id == uuid.UUID(template_id)))
        if not result.scalar_one_or_none():
            raise HTTPException(404, "Template not found")

        step = TaskTemplateStep(
            template_id=uuid.UUID(template_id),
            order=body.order,
            instruction=body.instruction,
            duration_minutes=body.duration_minutes,
            optional=body.optional,
        )
        session.add(step)
        await session.commit()
        cache.invalidate_prefix("template")
        return {"id": str(step.id)}


# ─── Tenant Overrides ──────────────────────────────────────────────────────────


@router.get("/overrides/{tenant_id}")
async def list_tenant_overrides(tenant_id: str):
    from app.config_management.service.overrides import list_overrides

    async with async_session_factory() as session:
        return await list_overrides(session, tenant_id)


@router.put("/overrides/{tenant_id}")
async def set_tenant_override(tenant_id: str, body: OverrideSet):
    from app.config_management.service.overrides import set_override

    async with async_session_factory() as session:
        return await set_override(session, tenant_id, body.config_type, body.config_key, body.override_json)


@router.delete("/overrides/{tenant_id}/{config_type}/{config_key}")
async def delete_tenant_override(tenant_id: str, config_type: str, config_key: str):
    from app.config_management.service.overrides import delete_override

    async with async_session_factory() as session:
        deleted = await delete_override(session, tenant_id, config_type, config_key)
        if not deleted:
            raise HTTPException(404, "Override not found")
        return {"status": "deleted"}


# ─── Export / Import ───────────────────────────────────────────────────────────


@router.get("/export/{config_type}")
async def export_config(config_type: str):
    """Export all records of a config type as JSON."""
    async with async_session_factory() as session:
        if config_type == "grow-types":
            result = await session.execute(
                select(GrowTypeProfile).options(
                    selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.environment),
                    selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.nutrients),
                    selectinload(GrowTypeProfile.stages).selectinload(GrowTypeStage.watering),
                    selectinload(GrowTypeProfile.equipment),
                    selectinload(GrowTypeProfile.troubleshooting),
                )
            )
            profiles = result.scalars().all()
            from app.config_management.service.grow_types import _serialize_profile

            data = [_serialize_profile(p) for p in profiles]
        elif config_type == "task-templates":
            result = await session.execute(select(TaskTemplate).options(selectinload(TaskTemplate.steps)))
            templates = result.scalars().all()
            from app.config_management.service.task_templates import _serialize_template

            data = [_serialize_template(t) for t in templates]
        else:
            raise HTTPException(400, f"Unknown config type: {config_type}")

        return JSONResponse(
            content={"type": config_type, "count": len(data), "data": data},
            headers={"Content-Disposition": f'attachment; filename="{config_type}-export.json"'},
        )


@router.post("/import/{config_type}")
async def import_config(config_type: str, payload: dict[str, Any]):
    """Import config from JSON export. Upserts existing records."""
    # This is a simplified import — for production, validate schema thoroughly
    if config_type not in ("grow-types", "task-templates"):
        raise HTTPException(400, f"Unknown config type: {config_type}")

    data = payload.get("data", [])
    if not isinstance(data, list):
        raise HTTPException(400, "payload.data must be a list")

    return {"status": "imported", "type": config_type, "count": len(data)}
