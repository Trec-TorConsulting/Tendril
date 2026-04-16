from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.auth.middleware import CurrentUser, get_current_user

# Feature registry: feature_name -> {plan: limit}
# limit can be int (max count), True (allowed), False (denied)
TIER_LIMITS: dict[str, dict[str, int | bool]] = {
    "tents": {"free": 1, "grower": 2, "pro": 5, "commercial": 999_999},
    "buckets": {"free": 2, "grower": 10, "pro": 25, "commercial": 999_999},
    "devices": {"free": 0, "grower": 5, "pro": 999_999, "commercial": 999_999},
    "sensor_history_days": {"free": 7, "grower": 90, "pro": 365, "commercial": 730},
    "ai_chat": {"free": False, "grower": True, "pro": True, "commercial": True},
    "ai_health_checks_per_day": {"free": 0, "grower": 2, "pro": 10, "commercial": 999_999},
    "ai_coach_tips": {"free": False, "grower": True, "pro": True, "commercial": True},
    "ai_insights": {"free": False, "grower": False, "pro": True, "commercial": True},
    "crop_steering": {"free": False, "grower": False, "pro": True, "commercial": True},
    "automation_rules": {"free": 0, "grower": 0, "pro": 10, "commercial": 999_999},
    "environment_schedules": {"free": False, "grower": True, "pro": True, "commercial": True},
    "push_notifications": {"free": False, "grower": True, "pro": True, "commercial": True},
    "discord_slack_alerts": {"free": False, "grower": False, "pro": True, "commercial": True},
    "sms_alerts": {"free": False, "grower": False, "pro": False, "commercial": True},
    "email_alerts": {"free": False, "grower": True, "pro": True, "commercial": True},
    "data_export": {"free": False, "grower": True, "pro": True, "commercial": True},
    "pdf_reports": {"free": False, "grower": False, "pro": True, "commercial": True},
    "team_members": {"free": 1, "grower": 1, "pro": 3, "commercial": 5},
    "task_management": {"free": False, "grower": False, "pro": False, "commercial": True},
    "audit_trail": {"free": False, "grower": False, "pro": False, "commercial": True},
    "harvest_workflow": {"free": False, "grower": False, "pro": True, "commercial": True},
    "strain_leaderboard": {"free": False, "grower": True, "pro": True, "commercial": True},
    "historical_overlay": {"free": False, "grower": False, "pro": True, "commercial": True},
    "weather_integration": {"free": False, "grower": True, "pro": True, "commercial": True},
    "weather_automation": {"free": False, "grower": False, "pro": True, "commercial": True},
    "custom_grow_types": {"free": False, "grower": False, "pro": True, "commercial": True},
    "strain_database": {"free": True, "grower": True, "pro": True, "commercial": True},
    "barcode_scanning": {"free": False, "grower": True, "pro": True, "commercial": True},
    "api_access": {"free": False, "grower": False, "pro": False, "commercial": True},
}


def get_tier_limit(plan: str, feature: str) -> int | bool:
    """Get the limit for a feature on a given plan."""
    feature_limits = TIER_LIMITS.get(feature)
    if feature_limits is None:
        return False
    return feature_limits.get(plan, False)


def require_feature(feature: str):
    """Dependency that checks if the current tenant's plan allows a feature.

    For boolean features, raises 403 if denied.
    For numeric features, returns the limit (caller must check count).
    """

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> int | bool:
        # TODO: look up tenant.plan from cache/DB; for now use a placeholder
        # In real implementation, this would pull from a lightweight cache
        plan = "free"  # Will be resolved from tenant record
        limit = get_tier_limit(plan, feature)
        if limit is False or limit == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature}' requires a plan upgrade",
            )
        return limit

    return _check
