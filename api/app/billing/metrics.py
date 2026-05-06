"""Business metrics API — MRR, churn, conversion, ARPU for platform admins."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, require_role
from app.database import get_db
from app.tenants.models import Account, Tenant

router = APIRouter()


class RevenueMetrics(BaseModel):
    mrr_cents: int  # Monthly Recurring Revenue in cents
    arr_cents: int  # Annual Run Rate
    total_subscribers: int
    total_accounts: int
    arpu_cents: int  # Average Revenue Per User
    plan_distribution: dict[str, int]  # plan_slug -> count
    churn_rate_30d: float  # % of subscribers who cancelled in last 30 days
    new_subscribers_30d: int
    cancelled_30d: int
    dunning_accounts: int  # Currently in grace period
    conversion_rate: float  # free -> paid conversion %


class DailyRevenue(BaseModel):
    date: str
    mrr_cents: int
    subscribers: int


# Plan pricing in cents (for MRR calculation)
_PLAN_PRICES = {
    "free": 0,
    "hobby": 999,
    "pro": 2999,
    "commercial": 7999,
    "enterprise": 24999,
    "dedicated": 49999,  # Placeholder for custom pricing
}


@router.get("/metrics", response_model=RevenueMetrics)
async def get_business_metrics(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Get business revenue and growth metrics. Platform admin only."""
    if not user.is_platform_admin:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Platform admin required")

    # Plan distribution
    plan_counts = await session.execute(select(Tenant.plan, func.count(Tenant.id)).group_by(Tenant.plan))
    plan_distribution: dict[str, int] = {}
    total_subscribers = 0
    mrr_cents = 0

    for plan_slug, count in plan_counts:
        plan_distribution[plan_slug] = count
        if plan_slug != "free":
            total_subscribers += count
        mrr_cents += _PLAN_PRICES.get(plan_slug, 0) * count

    # Total accounts and users
    total_accounts = (await session.execute(select(func.count(Account.id)))).scalar() or 0

    # ARPU (Average Revenue Per User with paid subscription)
    arpu_cents = (mrr_cents // total_subscribers) if total_subscribers > 0 else 0

    # Churn (accounts that were on paid plans 30 days ago but are now free)
    # We approximate using accounts currently in dunning or recently downgraded
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)

    dunning_count = (
        await session.execute(select(func.count(Account.id)).where(Account.dunning_started_at.isnot(None)))
    ).scalar() or 0

    # New subscribers in last 30 days (accounts created in last 30d on paid plans)
    new_paid_tenants = (
        await session.execute(
            select(func.count(Tenant.id)).where(
                Tenant.plan != "free",
                Tenant.created_at >= thirty_days_ago,
            )
        )
    ).scalar() or 0

    # Cancelled in last 30 days (approximation: free accounts with subscription_id = None that were paid)
    total_tenants = sum(plan_distribution.values())

    # Conversion rate: paid / total
    conversion_rate = (total_subscribers / total_tenants * 100) if total_tenants > 0 else 0.0

    # Churn rate: cancelled in 30d / subscribers at start of period
    # Simplified: dunning + recently downgraded / (total subscribers + recently downgraded)
    churn_denominator = total_subscribers + dunning_count
    churn_rate = (dunning_count / churn_denominator * 100) if churn_denominator > 0 else 0.0

    return RevenueMetrics(
        mrr_cents=mrr_cents,
        arr_cents=mrr_cents * 12,
        total_subscribers=total_subscribers,
        total_accounts=total_accounts,
        arpu_cents=arpu_cents,
        plan_distribution=plan_distribution,
        churn_rate_30d=round(churn_rate, 2),
        new_subscribers_30d=new_paid_tenants,
        cancelled_30d=dunning_count,
        dunning_accounts=dunning_count,
        conversion_rate=round(conversion_rate, 2),
    )
