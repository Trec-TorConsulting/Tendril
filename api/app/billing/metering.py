"""Billing usage metering — track and check resource consumption per tenant."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models import BillingPlan, BillingUsageRecord

logger = logging.getLogger("tendril.billing.metering")


def _current_period_start() -> date:
    """Get the first day of the current billing month."""
    today = datetime.now(UTC).date()
    return today.replace(day=1)


def _current_period_end() -> date:
    """Get the last day of the current billing month."""
    today = datetime.now(UTC).date()
    if today.month == 12:
        return today.replace(year=today.year + 1, month=1, day=1)
    return today.replace(month=today.month + 1, day=1)


async def record_usage(
    session: AsyncSession,
    tenant_id: UUID | None,
    metric: str,
    increment: int = 1,
) -> BillingUsageRecord | None:
    """Increment usage counter for a metric in the current period.

    Creates the record if it doesn't exist for this period.
    """
    if tenant_id is None:
        return None
    period_start = _current_period_start()
    period_end = _current_period_end()

    record = (
        await session.execute(
            select(BillingUsageRecord).where(
                BillingUsageRecord.tenant_id == tenant_id,
                BillingUsageRecord.metric == metric,
                BillingUsageRecord.period_start == period_start,
            )
        )
    ).scalar_one_or_none()

    if record:
        record.quantity += increment
    else:
        record = BillingUsageRecord(
            tenant_id=tenant_id,
            metric=metric,
            quantity=increment,
            period_start=period_start,
            period_end=period_end,
        )
        session.add(record)

    return record


async def get_usage_summary(
    session: AsyncSession,
    tenant_id: UUID | None,
) -> dict[str, int]:
    """Get all usage metrics for the current billing period."""
    if tenant_id is None:
        return {}
    period_start = _current_period_start()

    records = (
        (
            await session.execute(
                select(BillingUsageRecord).where(
                    BillingUsageRecord.tenant_id == tenant_id,
                    BillingUsageRecord.period_start == period_start,
                )
            )
        )
        .scalars()
        .all()
    )

    return {r.metric: r.quantity for r in records}


async def check_limit(
    session: AsyncSession,
    tenant_id: UUID,
    metric: str,
    plan: BillingPlan,
) -> tuple[bool, int, int | None]:
    """Check if tenant is within their limit for a metric.

    Returns: (is_within_limit, current_usage, limit)
    Limit of None means unlimited.
    """
    limit_map = {
        "grows": plan.max_grows,
        "devices": plan.max_devices,
        "team_members": plan.max_team_members,
        "ai_analyses": plan.max_ai_analyses_month,
        "storage_gb": plan.max_storage_gb,
        "automations": plan.max_automations,
        "integrations": plan.max_integrations,
        "journal_entries": plan.max_journal_entries_month,
    }

    limit = limit_map.get(metric)
    if limit is None:
        return True, 0, None  # Unlimited

    usage = await get_usage_summary(session, tenant_id)
    current = usage.get(metric, 0)

    return current < limit, current, limit


async def get_usage_percentage(
    session: AsyncSession,
    tenant_id: UUID,
    metric: str,
    plan: BillingPlan,
) -> float | None:
    """Get usage as a percentage of limit. None if unlimited."""
    _is_within, current, limit = await check_limit(session, tenant_id, metric, plan)
    if limit is None:
        return None
    return (current / limit) * 100 if limit > 0 else 0.0
