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
from app.grows.models import Strain, Yield, Bucket, GrowCycle
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


class StrainCreate(BaseModel):
    name: str
    breeder: str | None = None
    genetics: str | None = None
    flowering_days: int | None = None
    thc_pct: float | None = None
    cbd_pct: float | None = None
    terpene_profile: dict | None = None
    notes: str | None = None


class StrainUpdate(BaseModel):
    name: str | None = None
    breeder: str | None = None
    genetics: str | None = None
    flowering_days: int | None = None
    thc_pct: float | None = None
    cbd_pct: float | None = None
    terpene_profile: dict | None = None
    notes: str | None = None


class StrainResponse(BaseModel):
    id: UUID
    name: str
    breeder: str | None
    genetics: str | None
    flowering_days: int | None
    thc_pct: float | None
    cbd_pct: float | None
    terpene_profile: dict | None
    notes: str | None
    is_global: bool = False
    model_config = {"from_attributes": True}

    @classmethod
    def from_strain(cls, strain: "Strain") -> "StrainResponse":
        return cls(
            id=strain.id,
            name=strain.name,
            breeder=strain.breeder,
            genetics=strain.genetics,
            flowering_days=strain.flowering_days,
            thc_pct=strain.thc_pct,
            cbd_pct=strain.cbd_pct,
            terpene_profile=strain.terpene_profile,
            notes=strain.notes,
            is_global=strain.tenant_id is None,
        )


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


@router.get("")
async def list_strains(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    q = select(Strain).order_by(Strain.name)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[StrainResponse.from_strain(s) for s in items],
        total=total, page=pagination.page, page_size=pagination.page_size,
    )


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


class StrainGrowComparison(BaseModel):
    grow_id: UUID
    grow_name: str
    grow_type: str
    bucket_count: int
    avg_dry_weight_g: float | None
    avg_quality: float | None
    total_dry_weight_g: float | None
    grow_duration_days: int | None


@router.get("/{strain_id}/comparison", response_model=list[StrainGrowComparison])
async def strain_comparison(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Compare a strain's performance across different grows."""
    from datetime import datetime, timezone

    # Get all buckets with this strain_id or matching strain_name
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")

    result = await session.execute(
        select(
            GrowCycle.id.label("grow_id"),
            GrowCycle.name.label("grow_name"),
            GrowCycle.grow_type,
            GrowCycle.started_at,
            GrowCycle.ended_at,
            func.count(func.distinct(Bucket.id)).label("bucket_count"),
            func.avg(Yield.dry_weight_g).label("avg_dry_weight_g"),
            func.sum(Yield.dry_weight_g).label("total_dry_weight_g"),
            func.avg(Yield.quality_rating).label("avg_quality"),
        )
        .select_from(Bucket)
        .join(GrowCycle, GrowCycle.id == Bucket.grow_cycle_id)
        .outerjoin(Yield, Yield.bucket_id == Bucket.id)
        .where(
            (Bucket.strain_id == strain_id) | (func.lower(Bucket.strain_name) == func.lower(strain.name))
        )
        .group_by(GrowCycle.id, GrowCycle.name, GrowCycle.grow_type, GrowCycle.started_at, GrowCycle.ended_at)
        .order_by(desc(GrowCycle.started_at))
    )

    items = []
    now = datetime.now(timezone.utc)
    for row in result:
        duration = None
        if row.started_at:
            end = row.ended_at or now
            duration = (end - row.started_at).days
        items.append(StrainGrowComparison(
            grow_id=row.grow_id,
            grow_name=row.grow_name,
            grow_type=row.grow_type,
            bucket_count=row.bucket_count,
            avg_dry_weight_g=round(row.avg_dry_weight_g, 1) if row.avg_dry_weight_g else None,
            total_dry_weight_g=round(row.total_dry_weight_g, 1) if row.total_dry_weight_g else None,
            avg_quality=round(row.avg_quality, 1) if row.avg_quality else None,
            grow_duration_days=duration,
        ))
    return items


@router.get("/{strain_id}", response_model=StrainResponse)
async def get_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")
    return StrainResponse.from_strain(strain)


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
    if strain.tenant_id is None:
        raise HTTPException(status_code=403, detail="Cannot modify global strains")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(strain, field, value)
    await session.commit()
    await session.refresh(strain)
    return StrainResponse.from_strain(strain)


@router.delete("/{strain_id}", status_code=204)
async def delete_strain(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")
    if strain.tenant_id is None:
        raise HTTPException(status_code=403, detail="Cannot delete global strains")
    await session.delete(strain)
    await session.commit()


class FeedingSuggestion(BaseModel):
    stage: str
    target_ec: float
    target_ppm: float
    notes: str


@router.get("/{strain_id}/feeding-suggestions", response_model=list[FeedingSuggestion])
async def get_feeding_suggestions(
    strain_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Return strain-specific feeding suggestions based on genetics."""
    strain = await session.get(Strain, strain_id)
    if strain is None:
        raise HTTPException(status_code=404, detail="Strain not found")

    genetics = (strain.genetics or "").lower()
    is_indica = "indica" in genetics
    is_sativa = "sativa" in genetics
    is_auto = "auto" in genetics
    cbd_heavy = (strain.cbd_pct or 0) > 5

    # Base EC/PPM ranges by stage (adjust for genetics)
    # Indica: slightly lower EC tolerance, sativa: higher, auto: much lower
    stages = [
        ("seedling", 0.4, 200, "Light feed only. Let roots establish."),
        ("vegetative", 1.2, 600, "Increase N for vegetative growth."),
        ("transition", 1.4, 700, "Begin shifting to bloom nutrients."),
        ("flowering", 1.6, 800, "Full bloom nutrients. Watch for tip burn."),
        ("late_flower", 1.4, 700, "Reduce strength. Monitor trichomes."),
        ("flush", 0.0, 0, "Plain pH'd water only for final flush."),
    ]

    suggestions: list[FeedingSuggestion] = []
    for stage, base_ec, base_ppm, note in stages:
        ec = base_ec
        ppm = base_ppm
        extra = note

        if is_auto:
            ec *= 0.7
            ppm = int(ppm * 0.7)
            extra += " [Auto — reduce strength 30%]"
        elif is_indica:
            ec *= 0.9
            ppm = int(ppm * 0.9)
            extra += " [Indica — slightly lower tolerance]"
        elif is_sativa:
            ec *= 1.1
            ppm = int(ppm * 1.1)
            extra += " [Sativa — can handle stronger feeds]"

        if cbd_heavy and stage in ("flowering", "late_flower"):
            extra += f" [High CBD ({strain.cbd_pct}%) — extend flowering for cannabinoid development]"

        # Terpene-specific late-flower advice
        terps = strain.terpene_profile or {}
        if stage == "late_flower" and terps:
            dominant = sorted(terps.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
            if dominant:
                terp_name = dominant[0][0].lower()
                if terp_name in ("myrcene", "linalool", "terpinolene"):
                    extra += f" [Drop temps to 65-70°F at night to preserve {dominant[0][0]}]"
                elif terp_name in ("caryophyllene", "limonene"):
                    extra += f" [Moderate stress (light LST) can boost {dominant[0][0]}]"

        suggestions.append(FeedingSuggestion(
            stage=stage,
            target_ec=round(ec, 2),
            target_ppm=round(ppm),
            notes=extra,
        ))

    return suggestions
