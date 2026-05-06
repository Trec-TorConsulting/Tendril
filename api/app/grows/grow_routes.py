"""Grow cycle CRUD API — tenant-scoped, grow-type-aware."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.audit import record_audit
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.tier_gate import require_usage_limit
from app.grows.models import Bucket, GrowCycle
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


class GrowCreate(BaseModel):
    tent_id: UUID
    name: str
    grow_type: str
    stage: str = "seedling"
    notes: str | None = None
    settings: dict | None = None
    auto_health_check: bool = False


class GrowUpdate(BaseModel):
    name: str | None = None
    stage: str | None = None
    status: str | None = None
    notes: str | None = None
    started_at: datetime | None = None
    milestones: dict | None = None
    settings: dict | None = None
    auto_health_check: bool | None = None


class GrowResponse(BaseModel):
    id: UUID
    tent_id: UUID
    name: str
    grow_type: str
    status: str
    stage: str
    started_at: datetime
    ended_at: datetime | None
    notes: str | None
    milestones: dict | None
    settings: dict | None
    auto_health_check: bool
    model_config = {"from_attributes": True}


@router.post("", response_model=GrowResponse, status_code=201, dependencies=[Depends(require_usage_limit("grows"))])
async def create_grow(
    body: GrowCreate,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new grow cycle."""
    grow = GrowCycle(tenant_id=user.tenant_id, **body.model_dump())
    session.add(grow)
    await session.commit()
    await session.refresh(grow)
    await record_audit(session, user.tenant_id, user.user_id, "create", "grow", str(grow.id), request=request)
    await session.commit()
    return grow


@router.get("", response_model=PaginatedResponse[GrowResponse])
async def list_grows(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    status: str | None = None,
    tent_id: UUID | None = None,
):
    """List all grow cycles for the current tenant."""
    q = (
        select(GrowCycle)
        .where(GrowCycle.deleted_at.is_(None), GrowCycle.tenant_id == user.tenant_id)
        .order_by(GrowCycle.created_at.desc())
    )
    if status:
        q = q.where(GrowCycle.status == status)
    if tent_id:
        q = q.where(GrowCycle.tent_id == tent_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


class HarvestCountdownItem(BaseModel):
    grow_id: UUID
    grow_name: str
    bucket_id: UUID
    bucket_label: str | None
    strain_name: str | None
    flowering_days: int
    flowering_start: str
    estimated_harvest: str
    days_remaining: int


@router.get("/harvest-countdown", response_model=list[HarvestCountdownItem])
async def harvest_countdown(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Return harvest countdown for active grows with strain-linked buckets."""
    result = await session.execute(
        select(GrowCycle)
        .options(selectinload(GrowCycle.buckets).selectinload(Bucket.strain))
        .where(GrowCycle.status == "active")
    )
    grows = result.scalars().all()
    items: list[HarvestCountdownItem] = []
    now = datetime.now(UTC)
    for grow in grows:
        milestones = grow.milestones or {}
        for bucket in grow.buckets:
            if bucket.status != "active":
                continue
            strain = bucket.strain
            if not strain or not strain.flowering_days:
                continue
            flowering_start_str = milestones.get("flowering") or milestones.get("flower")
            if not flowering_start_str:
                continue
            flowering_start = datetime.fromisoformat(flowering_start_str)
            if flowering_start.tzinfo is None:
                flowering_start = flowering_start.replace(tzinfo=UTC)
            estimated_harvest = flowering_start + timedelta(days=strain.flowering_days)
            days_remaining = (estimated_harvest - now).days
            items.append(
                HarvestCountdownItem(
                    grow_id=grow.id,
                    grow_name=grow.name,
                    bucket_id=bucket.id,
                    bucket_label=bucket.label,
                    strain_name=strain.name,
                    flowering_days=strain.flowering_days,
                    flowering_start=flowering_start.isoformat(),
                    estimated_harvest=estimated_harvest.isoformat(),
                    days_remaining=days_remaining,
                )
            )
    items.sort(key=lambda x: x.days_remaining)
    return items


@router.get("/{grow_id}", response_model=GrowResponse)
async def get_grow(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a grow cycle by ID."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    return grow


@router.patch("/{grow_id}", response_model=GrowResponse)
async def update_grow(
    grow_id: UUID,
    body: GrowUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a grow cycle's details."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    updates = body.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] in ("completed", "archived"):
        grow.ended_at = datetime.now(UTC)
    # Auto-record milestone when stage changes
    if "stage" in updates:
        ms = dict(grow.milestones or {})
        ms[updates["stage"]] = datetime.now(UTC).isoformat()
        updates["milestones"] = ms
    # Merge milestones if client sends partial updates
    if "milestones" in updates and updates["milestones"] is not None:
        merged = dict(grow.milestones or {})
        merged.update(updates["milestones"])
        updates["milestones"] = merged
    for field, value in updates.items():
        setattr(grow, field, value)
    # Cascade stage change to all active buckets in this grow
    if "stage" in updates:
        await session.execute(
            update(Bucket)
            .where(Bucket.grow_cycle_id == grow_id, Bucket.status == "active")
            .values(growth_stage=updates["stage"])
        )
    await session.commit()

    # Create stage transition tasks when stage changes
    if "stage" in updates:
        try:
            from app.scheduler.task_generator import create_stage_transition_tasks

            await create_stage_transition_tasks(session, grow, updates["stage"])
        except Exception as exc:
            import logging

            logging.getLogger(__name__).warning("Stage task creation failed: %s", exc)

    await session.refresh(grow)
    return grow


@router.delete("/{grow_id}", status_code=204)
async def delete_grow(
    grow_id: UUID,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Soft-delete a grow cycle."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None or grow.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    await record_audit(session, user.tenant_id, user.user_id, "delete", "grow", str(grow_id), request=request)
    grow.deleted_at = datetime.now(UTC)
    await session.commit()
