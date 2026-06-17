"""Expense CRUD + ROI calculation routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.tier_gate import require_plan
from app.grows.expense_models import Expense, ExpenseCategory, HarvestValue
from app.grows.models import GrowCycle

router = APIRouter()


# ─── Schemas ──────────────────────────────────────────────────────────────────


class ExpenseCreate(BaseModel):
    grow_cycle_id: UUID
    category: ExpenseCategory
    amount_cents: int = Field(gt=0, description="Amount in cents (e.g. 4500 = $45.00)")
    currency: str = "usd"
    description: str | None = None
    vendor: str | None = None
    date: datetime | None = None
    is_recurring: bool = False
    recurring_interval: str | None = None
    notes: str | None = None


class ExpenseUpdate(BaseModel):
    category: ExpenseCategory | None = None
    amount_cents: int | None = Field(default=None, gt=0)
    description: str | None = None
    vendor: str | None = None
    date: datetime | None = None
    is_recurring: bool | None = None
    recurring_interval: str | None = None
    notes: str | None = None


class ExpenseResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    category: str
    amount_cents: int
    currency: str
    description: str | None
    vendor: str | None
    date: datetime
    is_recurring: bool
    recurring_interval: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HarvestValueCreate(BaseModel):
    grow_cycle_id: UUID
    grade: str = Field(pattern=r"^(A|B|trim|waste)$")
    weight_g: float = Field(gt=0)
    price_per_gram_cents: int = Field(gt=0)
    notes: str | None = None


class HarvestValueResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    grade: str
    weight_g: float
    price_per_gram_cents: int
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ROISummary(BaseModel):
    grow_cycle_id: UUID
    grow_name: str
    total_expenses_cents: int
    total_harvest_value_cents: int
    total_dry_weight_g: float
    cost_per_gram_cents: float | None
    roi_percentage: float | None
    expense_breakdown: dict[str, int]  # category -> total_cents


class GrowComparison(BaseModel):
    grows: list[ROISummary]


# ─── Expense CRUD ─────────────────────────────────────────────────────────────


@router.post(
    "/expenses", response_model=ExpenseResponse, status_code=201, dependencies=[Depends(require_plan("hobby"))]
)
async def create_expense(
    body: ExpenseCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log an expense for a grow cycle. Requires any paid plan."""
    # Verify grow belongs to tenant
    grow = await session.get(GrowCycle, body.grow_cycle_id)
    if not grow or grow.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Grow cycle not found")

    expense = Expense(tenant_id=user.tenant_id, **body.model_dump())
    session.add(expense)
    await session.commit()
    await session.refresh(expense)
    return expense


@router.get("/expenses", response_model=list[ExpenseResponse])
async def list_expenses(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_cycle_id: UUID | None = None,
    category: ExpenseCategory | None = None,
):
    """List expenses with optional filtering by grow or category."""
    q = select(Expense).where(Expense.tenant_id == user.tenant_id).order_by(desc(Expense.date))
    if grow_cycle_id:
        q = q.where(Expense.grow_cycle_id == grow_cycle_id)
    if category:
        q = q.where(Expense.category == category)
    result = await session.execute(q)
    return result.scalars().all()


@router.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: UUID,
    body: ExpenseUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update an expense record."""
    expense = await session.get(Expense, expense_id)
    if not expense or expense.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    await session.commit()
    await session.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}", status_code=204)
async def delete_expense(
    expense_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete an expense record."""
    expense = await session.get(Expense, expense_id)
    if not expense or expense.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Expense not found")
    await session.delete(expense)
    await session.commit()


# ─── Harvest Value ────────────────────────────────────────────────────────────


@router.post(
    "/harvest-values",
    response_model=HarvestValueResponse,
    status_code=201,
    dependencies=[Depends(require_plan("hobby"))],
)
async def create_harvest_value(
    body: HarvestValueCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Record the market value of a harvest by quality grade."""
    grow = await session.get(GrowCycle, body.grow_cycle_id)
    if not grow or grow.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Grow cycle not found")

    hv = HarvestValue(tenant_id=user.tenant_id, **body.model_dump())
    session.add(hv)
    await session.commit()
    await session.refresh(hv)
    return hv


@router.get("/harvest-values", response_model=list[HarvestValueResponse])
async def list_harvest_values(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_cycle_id: UUID | None = None,
):
    """List harvest values, optionally filtered by grow."""
    q = select(HarvestValue).where(HarvestValue.tenant_id == user.tenant_id).order_by(desc(HarvestValue.created_at))
    if grow_cycle_id:
        q = q.where(HarvestValue.grow_cycle_id == grow_cycle_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.delete("/harvest-values/{value_id}", status_code=204)
async def delete_harvest_value(
    value_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a harvest value record."""
    hv = await session.get(HarvestValue, value_id)
    if not hv or hv.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Harvest value not found")
    await session.delete(hv)
    await session.commit()


# ─── ROI Calculation ──────────────────────────────────────────────────────────


async def _calculate_roi(session: AsyncSession, grow: GrowCycle, tenant_id: UUID | None) -> ROISummary:
    """Calculate ROI metrics for a single grow cycle."""
    # Sum expenses by category
    expense_rows = await session.execute(
        select(Expense.category, func.sum(Expense.amount_cents))
        .where(Expense.grow_cycle_id == grow.id, Expense.tenant_id == tenant_id)
        .group_by(Expense.category)
    )
    expense_breakdown: dict[str, int] = {}
    total_expenses = 0
    for category, total in expense_rows:
        expense_breakdown[category] = total
        total_expenses += total

    # Sum harvest values
    harvest_rows = await session.execute(
        select(
            func.sum(HarvestValue.weight_g),
            func.sum(HarvestValue.weight_g * HarvestValue.price_per_gram_cents),
        ).where(HarvestValue.grow_cycle_id == grow.id, HarvestValue.tenant_id == tenant_id)
    )
    row = harvest_rows.one()
    total_weight = row[0] or 0.0
    total_value = int(row[1] or 0)

    # Calculate metrics
    cost_per_gram = (total_expenses / total_weight) if total_weight > 0 else None
    roi_pct = (((total_value - total_expenses) / total_expenses) * 100) if total_expenses > 0 else None

    return ROISummary(
        grow_cycle_id=grow.id,
        grow_name=grow.name,
        total_expenses_cents=total_expenses,
        total_harvest_value_cents=total_value,
        total_dry_weight_g=total_weight,
        cost_per_gram_cents=cost_per_gram,
        roi_percentage=roi_pct,
        expense_breakdown=expense_breakdown,
    )


@router.get("/{grow_cycle_id}/roi", response_model=ROISummary, dependencies=[Depends(require_plan("hobby"))])
async def get_grow_roi(
    grow_cycle_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Calculate ROI metrics for a specific grow cycle."""
    grow = await session.get(GrowCycle, grow_cycle_id)
    if not grow or grow.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Grow cycle not found")
    return await _calculate_roi(session, grow, user.tenant_id)


@router.get("/roi-comparison", response_model=GrowComparison, dependencies=[Depends(require_plan("hobby"))])
async def compare_grows_roi(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    grow_ids: list[UUID] = Query(default=[]),
    limit: int = Query(default=10, le=50),
):
    """Compare ROI across multiple grows. If grow_ids empty, returns most recent grows."""
    if grow_ids:
        q = select(GrowCycle).where(GrowCycle.id.in_(grow_ids), GrowCycle.tenant_id == user.tenant_id)
    else:
        q = (
            select(GrowCycle)
            .where(GrowCycle.tenant_id == user.tenant_id, GrowCycle.status == "completed")
            .order_by(desc(GrowCycle.ended_at))
            .limit(limit)
        )

    result = await session.execute(q)
    grows = result.scalars().all()

    summaries = []
    for grow in grows:
        summaries.append(await _calculate_roi(session, grow, user.tenant_id))

    return GrowComparison(grows=summaries)
