"""Tier-based feature gating — DB-driven plan limits enforcement."""

from __future__ import annotations

import logging
import time
from uuid import UUID

from fastapi import HTTPException, Request
from sqlalchemy import select

from app.billing.models import BillingPlan
from app.database import async_session_factory

logger = logging.getLogger("tendril.billing.tier_gate")

# In-memory plan cache (60s TTL)
_plan_cache: dict[str, tuple[float, BillingPlan | None]] = {}
_CACHE_TTL = 60.0


async def _get_plan_cached(plan_slug: str) -> BillingPlan | None:
    """Get a plan with in-memory caching."""
    now = time.time()
    cached = _plan_cache.get(plan_slug)
    if cached and (now - cached[0]) < _CACHE_TTL:
        return cached[1]

    async with async_session_factory() as session:
        plan = (
            await session.execute(
                select(BillingPlan).where(BillingPlan.slug == plan_slug, BillingPlan.is_active.is_(True))
            )
        ).scalar_one_or_none()

    _plan_cache[plan_slug] = (now, plan)
    return plan


def require_feature(feature: str):
    """Dependency that checks if the tenant's plan includes a feature flag.

    Usage:
        @router.get("/...", dependencies=[Depends(require_feature("custom_grow_types"))])
    """

    async def _check(request: Request):
        tenant_plan = getattr(request.state, "tenant_plan", "free")
        plan = await _get_plan_cached(tenant_plan)
        if not plan:
            plan = await _get_plan_cached("free")

        features = plan.features_json if plan else {}
        if not features.get(feature, False):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "feature_locked",
                    "feature": feature,
                    "current_plan": tenant_plan,
                    "message": f"This feature requires a higher plan. Upgrade to access '{feature}'.",
                },
            )

    return _check


def require_plan(min_plan: str):
    """Dependency that requires at least a certain plan tier.

    Plan hierarchy: free < hobby < pro < commercial < enterprise < dedicated
    """
    plan_order = ["free", "hobby", "pro", "commercial", "enterprise", "dedicated"]

    async def _check(request: Request):
        tenant_plan = getattr(request.state, "tenant_plan", "free")
        try:
            current_idx = plan_order.index(tenant_plan)
            required_idx = plan_order.index(min_plan)
        except ValueError:
            current_idx = 0
            required_idx = plan_order.index(min_plan)

        if current_idx < required_idx:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "plan_required",
                    "required_plan": min_plan,
                    "current_plan": tenant_plan,
                    "message": f"This feature requires the '{min_plan}' plan or higher.",
                },
            )

    return _check


async def check_usage_limit(
    tenant_id: UUID,
    metric: str,
    plan_slug: str,
) -> tuple[bool, int, int | None]:
    """Check if tenant is within their usage limit for a metric.

    Returns: (is_within_limit, current_usage, limit)
    """
    plan = await _get_plan_cached(plan_slug)
    if not plan:
        plan = await _get_plan_cached("free")

    limit_map: dict[str, int | None] = {}
    if plan:
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

    # Get current usage from billing records
    from app.billing.metering import get_usage_summary

    async with async_session_factory() as session:
        usage = await get_usage_summary(session, tenant_id)

    current = usage.get(metric, 0)
    return current < limit, current, limit


def require_usage_limit(metric: str):
    """Dependency that blocks the request if usage limit is exceeded.

    Usage:
        @router.post("/...", dependencies=[Depends(require_usage_limit("ai_analyses"))])
    """

    async def _check(request: Request):
        tenant_id = getattr(request.state, "tenant_id", None)
        tenant_plan = getattr(request.state, "tenant_plan", "free")

        if not tenant_id:
            return  # No tenant context — skip check

        within_limit, current, limit = await check_usage_limit(tenant_id, metric, tenant_plan)
        if not within_limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "usage_limit_exceeded",
                    "metric": metric,
                    "current": current,
                    "limit": limit,
                    "current_plan": tenant_plan,
                    "message": f"You've reached your {metric} limit ({current}/{limit}). Upgrade for more.",
                },
                headers={
                    "X-Usage-Current": str(current),
                    "X-Usage-Limit": str(limit or "unlimited"),
                    "X-Plan": tenant_plan,
                },
            )

    return _check


def clear_plan_cache():
    """Clear the plan cache (useful after plan updates)."""
    _plan_cache.clear()
