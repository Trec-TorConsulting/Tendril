"""Integration action policy helpers for AI-initiated connector operations.

This module centralizes Phase 1 connector policy defaults so route/service
layers can enforce allow/deny and risk controls consistently.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

SUPPORTED_INTEGRATION_TYPES = frozenset({"pulse", "openweather", "ecowitt"})

HIGH_RISK_OPERATION_CLASSES = frozenset(
    {
        "outbound_control",
        "device_command",
        "write_remote",
    }
)


def _normalize(value: str) -> str:
    return value.strip().lower()


@dataclass(frozen=True)
class IntegrationActionPolicyDecision:
    integration_type: str
    operation: str
    supported: bool
    allowed: bool
    risk_level: str
    requires_approval: bool
    requires_simulation: bool
    reason: str | None = None


def _is_high_risk_operation(operation: str) -> bool:
    if operation in HIGH_RISK_OPERATION_CLASSES:
        return True
    return operation.startswith(("control_", "set_", "toggle_", "command_"))


def evaluate_integration_action_policy(
    *,
    integration_type: str,
    operation: str,
    allowlist_policy: Mapping[str, set[str]] | None = None,
) -> IntegrationActionPolicyDecision:
    """Evaluate whether an AI integration action is allowed and which controls apply.

    ``allowlist_policy`` maps integration type to allowed operation names.
    Use ``{"*"}`` to allow all operations for a connector.
    """
    normalized_integration = _normalize(integration_type)
    normalized_operation = _normalize(operation)

    if normalized_integration not in SUPPORTED_INTEGRATION_TYPES:
        return IntegrationActionPolicyDecision(
            integration_type=normalized_integration,
            operation=normalized_operation,
            supported=False,
            allowed=False,
            risk_level="high",
            requires_approval=True,
            requires_simulation=True,
            reason=f"Unsupported integration connector: {normalized_integration}",
        )

    is_high_risk = _is_high_risk_operation(normalized_operation)
    risk_level = "high" if is_high_risk else "low"

    if allowlist_policy is not None and normalized_integration in allowlist_policy:
        allowed_operations = allowlist_policy[normalized_integration]
        if "*" not in allowed_operations and normalized_operation not in allowed_operations:
            return IntegrationActionPolicyDecision(
                integration_type=normalized_integration,
                operation=normalized_operation,
                supported=True,
                allowed=False,
                risk_level=risk_level,
                requires_approval=is_high_risk,
                requires_simulation=is_high_risk,
                reason=(
                    "Blocked by tenant integration policy: "
                    f"{normalized_integration}.{normalized_operation}"
                ),
            )

    return IntegrationActionPolicyDecision(
        integration_type=normalized_integration,
        operation=normalized_operation,
        supported=True,
        allowed=True,
        risk_level=risk_level,
        requires_approval=is_high_risk,
        requires_simulation=is_high_risk,
        reason=None,
    )


__all__ = [
    "HIGH_RISK_OPERATION_CLASSES",
    "SUPPORTED_INTEGRATION_TYPES",
    "IntegrationActionPolicyDecision",
    "evaluate_integration_action_policy",
]
