"""Grow cycle CRUD API — tenant-scoped, grow-type-aware."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import Bucket, GrowCycle

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


@router.post("", response_model=GrowResponse, status_code=201)
async def create_grow(
    body: GrowCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    grow = GrowCycle(tenant_id=user.tenant_id, **body.model_dump())
    session.add(grow)
    await session.commit()
    await session.refresh(grow)
    return grow


@router.get("", response_model=list[GrowResponse])
async def list_grows(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    status: str | None = None,
    tent_id: UUID | None = None,
):
    q = select(GrowCycle).order_by(GrowCycle.created_at.desc())
    if status:
        q = q.where(GrowCycle.status == status)
    if tent_id:
        q = q.where(GrowCycle.tent_id == tent_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/{grow_id}", response_model=GrowResponse)
async def get_grow(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    updates = body.model_dump(exclude_unset=True)
    if "status" in updates and updates["status"] in ("completed", "archived"):
        grow.ended_at = datetime.now(timezone.utc)
    # Auto-record milestone when stage changes
    if "stage" in updates:
        ms = dict(grow.milestones or {})
        ms[updates["stage"]] = datetime.now(timezone.utc).isoformat()
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
    await session.refresh(grow)
    return grow


@router.delete("/{grow_id}", status_code=204)
async def delete_grow(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    await session.delete(grow)
    await session.commit()
