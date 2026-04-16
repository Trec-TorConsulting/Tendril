"""Strains API — tenant-scoped CRUD + leaderboard."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import Strain, Yield, Bucket

router = APIRouter()


class StrainCreate(BaseModel):
    name: str
    breeder: str | None = None
    genetics: str | None = None
    flowering_days: int | None = None
    thc_pct: float | None = None
    cbd_pct: float | None = None
    terpene_profile: list[dict] | None = None
    notes: str | None = None


class StrainUpdate(BaseModel):
    name: str | None = None
    breeder: str | None = None
    genetics: str | None = None
    flowering_days: int | None = None
    thc_pct: float | None = None
    cbd_pct: float | None = None
    terpene_profile: list[dict] | None = None
    notes: str | None = None


class StrainResponse(BaseModel):
    id: UUID
    name: str
    breeder: str | None
    genetics: str | None
    flowering_days: int | None
    thc_pct: float | None
    cbd_pct: float | None
    terpene_profile: list[dict] | None
    notes: str | None
    model_config = {"from_attributes": True}


@router.post("", response_model=StrainResponse, status_code=201)
async def create_strain(
    body: StrainCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = Strain(tenant_id=user.tenant_id, **body.model_dump())
    session.add(strain)
    await session.commit()
    await session.refresh(strain)
    return strain


@router.get("", response_model=list[StrainResponse])
async def list_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    result = await session.execute(select(Strain).order_by(Strain.name))
    return result.scalars().all()


@router.get("/leaderboard")
async def strain_leaderboard(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Strain leaderboard — average dry weight and quality by strain name."""
    result = await session.execute(
        select(
            Bucket.strain_name,
            func.count(Yield.id).label("harvests"),
            func.avg(Yield.dry_weight_g).label("avg_dry_weight_g"),
            func.avg(Yield.quality_rating).label("avg_quality"),
        )
        .join(Yield, Yield.bucket_id == Bucket.id)
        .where(Bucket.strain_name.isnot(None))
        .where(Yield.dry_weight_g.isnot(None))
        .group_by(Bucket.strain_name)
        .order_by(desc("avg_dry_weight_g"))
    )
    return [
        {
            "strain_name": row.strain_name,
            "harvests": row.harvests,
            "avg_dry_weight_g": round(row.avg_dry_weight_g, 1) if row.avg_dry_weight_g else None,
            "avg_quality": round(row.avg_quality, 1) if row.avg_quality else None,
        }
        for row in result
    ]


@router.get("/{strain_id}", response_model=StrainResponse)
async def get_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")
    return strain


@router.patch("/{strain_id}", response_model=StrainResponse)
async def update_strain(
    strain_id: UUID,
    body: StrainUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(strain, field, value)
    await session.commit()
    await session.refresh(strain)
    return strain


@router.delete("/{strain_id}", status_code=204)
async def delete_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")
    await session.delete(strain)
    await session.commit()
