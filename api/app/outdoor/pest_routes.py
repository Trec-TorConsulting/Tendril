"""Pest scouting API — field observations, treatment tracking, IPM for outdoor grows."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, PestScoutEntry
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ---------- Schemas ----------


class PestScoutCreate(BaseModel):
    scouted_at: datetime | None = None
    pest_type: str  # insect | disease | animal | beneficial | unknown
    species: str
    severity: str = "low"  # low | medium | high | critical
    grid_row: int | None = None
    grid_col: int | None = None
    photo_url: str | None = None
    treatment_applied: str | None = None
    treatment_type: str | None = None  # organic | synthetic | biological | physical | none
    notes: str | None = None


class PestScoutUpdate(BaseModel):
    severity: str | None = None
    treatment_applied: str | None = None
    treatment_type: str | None = None
    notes: str | None = None


class PestScoutResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    scouted_at: datetime
    pest_type: str
    species: str
    severity: str
    grid_row: int | None
    grid_col: int | None
    photo_url: str | None
    treatment_applied: str | None
    treatment_type: str | None
    notes: str | None

    model_config = {"from_attributes": True}


# ---------- Endpoints ----------


@router.post("/{grow_id}/pest-scouts", response_model=PestScoutResponse, status_code=201)
async def create_pest_scout(
    grow_id: UUID,
    body: PestScoutCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a pest/disease/beneficial observation."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    entry = PestScoutEntry(tenant_id=user.tenant_id, grow_cycle_id=grow_id, **body.model_dump())
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("/{grow_id}/pest-scouts", response_model=PaginatedResponse[PestScoutResponse])
async def list_pest_scouts(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    pest_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
):
    """List pest scout entries, optionally filtered by type or severity."""
    q = select(PestScoutEntry).where(PestScoutEntry.grow_cycle_id == grow_id)
    if pest_type:
        q = q.where(PestScoutEntry.pest_type == pest_type)
    if severity:
        q = q.where(PestScoutEntry.severity == severity)
    q = q.order_by(desc(PestScoutEntry.scouted_at))
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{grow_id}/pest-scouts/{entry_id}", response_model=PestScoutResponse)
async def get_pest_scout(
    grow_id: UUID,
    entry_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single pest scout entry by ID."""
    entry = await session.get(PestScoutEntry, entry_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Pest scout entry not found")
    return entry


@router.patch("/{grow_id}/pest-scouts/{entry_id}", response_model=PestScoutResponse)
async def update_pest_scout(
    grow_id: UUID,
    entry_id: UUID,
    body: PestScoutUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a pest scout entry."""
    entry = await session.get(PestScoutEntry, entry_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Pest scout entry not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.delete("/{grow_id}/pest-scouts/{entry_id}", status_code=204)
async def delete_pest_scout(
    grow_id: UUID,
    entry_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a pest scout entry."""
    entry = await session.get(PestScoutEntry, entry_id)
    if entry is None or entry.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Pest scout entry not found")
    await session.delete(entry)
    await session.commit()
