"""Dose profiles + feeding schedules API — grow-type-aware."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import DoseProfile, FeedingSchedule
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ---------- Dose Profiles ----------

class DoseProfileCreate(BaseModel):
    grow_cycle_id: UUID
    name: str
    dose_type: str
    dose_ml: float
    enabled: bool = True
    settings: dict | None = None


class DoseProfileUpdate(BaseModel):
    name: str | None = None
    dose_ml: float | None = None
    enabled: bool | None = None
    settings: dict | None = None


class DoseProfileResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    name: str
    dose_type: str
    dose_ml: float
    enabled: bool
    settings: dict | None
    model_config = {"from_attributes": True}


@router.post("/doses", response_model=DoseProfileResponse, status_code=201)
async def create_dose_profile(
    body: DoseProfileCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    dose = DoseProfile(tenant_id=user.tenant_id, **body.model_dump())
    session.add(dose)
    await session.commit()
    await session.refresh(dose)
    return dose


@router.get("/doses")
async def list_dose_profiles(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: UUID | None = None,
):
    q = select(DoseProfile)
    if grow_cycle_id:
        q = q.where(DoseProfile.grow_cycle_id == grow_cycle_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/doses/{dose_id}", response_model=DoseProfileResponse)
async def get_dose_profile(
    dose_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single dose profile by ID."""
    dose = await session.get(DoseProfile, dose_id)
    if dose is None:
        raise HTTPException(status_code=404, detail="Dose profile not found")
    return dose


@router.patch("/doses/{dose_id}", response_model=DoseProfileResponse)
async def update_dose_profile(
    dose_id: UUID,
    body: DoseProfileUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    dose = await session.get(DoseProfile, dose_id)
    if dose is None:
        raise HTTPException(status_code=404, detail="Dose profile not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(dose, field, value)
    await session.commit()
    await session.refresh(dose)
    return dose


@router.delete("/doses/{dose_id}", status_code=204)
async def delete_dose_profile(
    dose_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    dose = await session.get(DoseProfile, dose_id)
    if dose is None:
        raise HTTPException(status_code=404, detail="Dose profile not found")
    await session.delete(dose)
    await session.commit()


# ---------- Feeding Schedules ----------

class FeedingScheduleCreate(BaseModel):
    grow_cycle_id: UUID
    name: str
    stage: str
    nutrients: list[dict]
    target_ppm: float | None = None
    target_ec: float | None = None
    notes: str | None = None


class FeedingScheduleUpdate(BaseModel):
    name: str | None = None
    stage: str | None = None
    nutrients: list[dict] | None = None
    target_ppm: float | None = None
    target_ec: float | None = None
    notes: str | None = None


class FeedingScheduleResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    name: str
    stage: str
    nutrients: list[dict]
    target_ppm: float | None = None
    target_ec: float | None = None
    notes: str | None
    model_config = {"from_attributes": True}


@router.post("/feeding", response_model=FeedingScheduleResponse, status_code=201)
async def create_feeding_schedule(
    body: FeedingScheduleCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    schedule = FeedingSchedule(tenant_id=user.tenant_id, **body.model_dump())
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule


@router.get("/feeding")
async def list_feeding_schedules(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: UUID | None = None,
):
    from sqlalchemy import case

    stage_order = case(
        {"seedling": 0, "vegetative": 1, "flowering": 2, "ripening": 3, "drying": 4, "curing": 5},
        value=FeedingSchedule.stage,
        else_=99,
    )
    q = select(FeedingSchedule).order_by(stage_order, FeedingSchedule.name)
    if grow_cycle_id:
        q = q.where(FeedingSchedule.grow_cycle_id == grow_cycle_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/feeding/{schedule_id}", response_model=FeedingScheduleResponse)
async def get_feeding_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single feeding schedule by ID."""
    schedule = await session.get(FeedingSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")
    return schedule


@router.patch("/feeding/{schedule_id}", response_model=FeedingScheduleResponse)
async def update_feeding_schedule(
    schedule_id: UUID,
    body: FeedingScheduleUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    schedule = await session.get(FeedingSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await session.commit()
    await session.refresh(schedule)
    return schedule


@router.delete("/feeding/{schedule_id}", status_code=204)
async def delete_feeding_schedule(
    schedule_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    schedule = await session.get(FeedingSchedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Feeding schedule not found")
    await session.delete(schedule)
    await session.commit()
