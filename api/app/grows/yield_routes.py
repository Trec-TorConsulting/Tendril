"""Yields + harvest workflow API."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import Yield

router = APIRouter()


class YieldCreate(BaseModel):
    bucket_id: UUID
    wet_weight_g: float | None = None
    dry_weight_g: float | None = None
    trim_weight_g: float | None = None
    quality_rating: int | None = None
    terpene_notes: str | None = None
    notes: str | None = None
    harvest_date: datetime | None = None
    dry_start: datetime | None = None
    dry_end: datetime | None = None
    cure_start: datetime | None = None
    cure_end: datetime | None = None
    dry_environment: dict | None = None


class YieldUpdate(BaseModel):
    wet_weight_g: float | None = None
    dry_weight_g: float | None = None
    trim_weight_g: float | None = None
    quality_rating: int | None = None
    terpene_notes: str | None = None
    notes: str | None = None
    harvest_date: datetime | None = None
    dry_start: datetime | None = None
    dry_end: datetime | None = None
    cure_start: datetime | None = None
    cure_end: datetime | None = None
    dry_environment: dict | None = None


class YieldResponse(BaseModel):
    id: UUID
    bucket_id: UUID
    wet_weight_g: float | None
    dry_weight_g: float | None
    trim_weight_g: float | None
    quality_rating: int | None
    terpene_notes: str | None
    notes: str | None
    harvest_date: datetime | None
    dry_start: datetime | None
    dry_end: datetime | None
    cure_start: datetime | None
    cure_end: datetime | None
    dry_environment: dict | None
    model_config = {"from_attributes": True}


@router.post("", response_model=YieldResponse, status_code=201)
async def create_yield(
    body: YieldCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Record a harvest yield for a bucket."""
    y = Yield(tenant_id=user.tenant_id, **body.model_dump())
    session.add(y)
    await session.commit()
    await session.refresh(y)
    return y


@router.get("", response_model=list[YieldResponse])
async def list_yields(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    bucket_id: UUID | None = None,
):
    """List yields with optional bucket filtering."""
    q = select(Yield).where(Yield.tenant_id == user.tenant_id).order_by(desc(Yield.created_at))
    if bucket_id:
        q = q.where(Yield.bucket_id == bucket_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.get("/{yield_id}", response_model=YieldResponse)
async def get_yield(
    yield_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a yield record by ID."""
    y = await session.get(Yield, yield_id)
    if y is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    return y


@router.patch("/{yield_id}", response_model=YieldResponse)
async def update_yield(
    yield_id: UUID,
    body: YieldUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a yield record."""
    y = await session.get(Yield, yield_id)
    if y is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(y, field, value)
    await session.commit()
    await session.refresh(y)
    return y


@router.delete("/{yield_id}", status_code=204)
async def delete_yield(
    yield_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a yield record by ID."""
    y = await session.get(Yield, yield_id)
    if y is None:
        raise HTTPException(status_code=404, detail="Yield not found")
    await session.delete(y)
    await session.commit()
