"""Soil health API — soil tests and amendment tracking for outdoor grows."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, SoilTest, SoilAmendment
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


# ---------- Schemas ----------

class SoilTestCreate(BaseModel):
    tested_at: datetime | None = None
    ph: float | None = None
    nitrogen_ppm: float | None = None
    phosphorus_ppm: float | None = None
    potassium_ppm: float | None = None
    organic_matter_pct: float | None = None
    cec: float | None = None
    calcium_ppm: float | None = None
    magnesium_ppm: float | None = None
    sulfur_ppm: float | None = None
    source: str = "home_kit"
    notes: str | None = None


class SoilTestResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    tested_at: datetime
    ph: float | None
    nitrogen_ppm: float | None
    phosphorus_ppm: float | None
    potassium_ppm: float | None
    organic_matter_pct: float | None
    cec: float | None
    calcium_ppm: float | None
    magnesium_ppm: float | None
    sulfur_ppm: float | None
    source: str
    notes: str | None

    model_config = {"from_attributes": True}


class SoilTestUpdate(BaseModel):
    ph: float | None = None
    nitrogen_ppm: float | None = None
    phosphorus_ppm: float | None = None
    potassium_ppm: float | None = None
    organic_matter_pct: float | None = None
    cec: float | None = None
    notes: str | None = None


class AmendmentCreate(BaseModel):
    applied_at: datetime | None = None
    amendment_type: str
    product_name: str
    quantity: str | None = None
    area_applied: str | None = None
    cost: float | None = None
    notes: str | None = None


class AmendmentResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    applied_at: datetime
    amendment_type: str
    product_name: str
    quantity: str | None
    area_applied: str | None
    cost: float | None
    notes: str | None

    model_config = {"from_attributes": True}


class AmendmentUpdate(BaseModel):
    quantity: str | None = None
    area_applied: str | None = None
    cost: float | None = None
    notes: str | None = None


# ---------- Soil Test Endpoints ----------

@router.post("/{grow_id}/soil-tests", response_model=SoilTestResponse, status_code=201)
async def create_soil_test(
    grow_id: UUID,
    body: SoilTestCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a soil test result."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    data = body.model_dump()
    test = SoilTest(tenant_id=user.tenant_id, grow_cycle_id=grow_id, **data)
    session.add(test)
    await session.commit()
    await session.refresh(test)
    return test


@router.get("/{grow_id}/soil-tests", response_model=PaginatedResponse[SoilTestResponse])
async def list_soil_tests(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all soil tests for a grow, newest first."""
    q = (
        select(SoilTest)
        .where(SoilTest.grow_cycle_id == grow_id)
        .order_by(desc(SoilTest.tested_at))
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{grow_id}/soil-tests/latest", response_model=SoilTestResponse)
async def get_latest_soil_test(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the most recent soil test."""
    result = await session.execute(
        select(SoilTest)
        .where(SoilTest.grow_cycle_id == grow_id)
        .order_by(desc(SoilTest.tested_at))
        .limit(1)
    )
    test = result.scalar_one_or_none()
    if test is None:
        raise HTTPException(status_code=404, detail="No soil tests found")
    return test


@router.get("/{grow_id}/soil-tests/{test_id}", response_model=SoilTestResponse)
async def get_soil_test(
    grow_id: UUID,
    test_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single soil test by ID."""
    test = await session.get(SoilTest, test_id)
    if test is None or test.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Soil test not found")
    return test


@router.patch("/{grow_id}/soil-tests/{test_id}", response_model=SoilTestResponse)
async def update_soil_test(
    grow_id: UUID,
    test_id: UUID,
    body: SoilTestUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a soil test."""
    test = await session.get(SoilTest, test_id)
    if test is None or test.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Soil test not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(test, field, value)
    await session.commit()
    await session.refresh(test)
    return test


@router.delete("/{grow_id}/soil-tests/{test_id}", status_code=204)
async def delete_soil_test(
    grow_id: UUID,
    test_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a soil test."""
    test = await session.get(SoilTest, test_id)
    if test is None or test.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Soil test not found")
    await session.delete(test)
    await session.commit()


# ---------- Soil Amendment Endpoints ----------

@router.post("/{grow_id}/amendments", response_model=AmendmentResponse, status_code=201)
async def create_amendment(
    grow_id: UUID,
    body: AmendmentCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a soil amendment application."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    amendment = SoilAmendment(tenant_id=user.tenant_id, grow_cycle_id=grow_id, **body.model_dump())
    session.add(amendment)
    await session.commit()
    await session.refresh(amendment)
    return amendment


@router.get("/{grow_id}/amendments", response_model=PaginatedResponse[AmendmentResponse])
async def list_amendments(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all soil amendments for a grow, newest first."""
    q = (
        select(SoilAmendment)
        .where(SoilAmendment.grow_cycle_id == grow_id)
        .order_by(desc(SoilAmendment.applied_at))
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{grow_id}/amendments/{amendment_id}", response_model=AmendmentResponse)
async def get_amendment(
    grow_id: UUID,
    amendment_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single amendment by ID."""
    amendment = await session.get(SoilAmendment, amendment_id)
    if amendment is None or amendment.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Amendment not found")
    return amendment


@router.patch("/{grow_id}/amendments/{amendment_id}", response_model=AmendmentResponse)
async def update_amendment(
    grow_id: UUID,
    amendment_id: UUID,
    body: AmendmentUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a soil amendment."""
    amendment = await session.get(SoilAmendment, amendment_id)
    if amendment is None or amendment.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Amendment not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(amendment, field, value)
    await session.commit()
    await session.refresh(amendment)
    return amendment


@router.delete("/{grow_id}/amendments/{amendment_id}", status_code=204)
async def delete_amendment(
    grow_id: UUID,
    amendment_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a soil amendment."""
    amendment = await session.get(SoilAmendment, amendment_id)
    if amendment is None or amendment.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Amendment not found")
    await session.delete(amendment)
    await session.commit()
