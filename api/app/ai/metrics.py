"""Prometheus metrics for AI action lifecycle observability."""

from __future__ import annotations

from prometheus_client import Counter

AI_ACTION_PROPOSALS_TOTAL = Counter(
    "tendril_ai_action_proposals_total",
    "Total AI action proposals created.",
    labelnames=("action_type", "source"),
)

AI_ACTION_APPROVAL_DECISIONS_TOTAL = Counter(
    "tendril_ai_action_approval_decisions_total",
    "Total AI action approval decisions recorded.",
    labelnames=("decision", "action_type"),
)

AI_ACTION_EXECUTION_OUTCOMES_TOTAL = Counter(
    "tendril_ai_action_execution_outcomes_total",
    "Total AI action execution outcomes recorded.",
    labelnames=("outcome", "action_type"),
)

AI_ACTION_POLICY_BLOCKS_TOTAL = Counter(
    "tendril_ai_action_policy_blocks_total",
    "Total AI action policy blocks recorded.",
    labelnames=("action_type", "integration_type", "operation"),
)


def record_action_proposed(*, action_type: str, source: str) -> None:
    AI_ACTION_PROPOSALS_TOTAL.labels(action_type=action_type, source=source).inc()


def record_approval_decision(*, decision: str, action_type: str) -> None:
    AI_ACTION_APPROVAL_DECISIONS_TOTAL.labels(decision=decision, action_type=action_type).inc()


def record_execution_outcome(*, outcome: str, action_type: str) -> None:
    AI_ACTION_EXECUTION_OUTCOMES_TOTAL.labels(outcome=outcome, action_type=action_type).inc()


def record_policy_block(*, action_type: str, integration_type: str, operation: str) -> None:
    AI_ACTION_POLICY_BLOCKS_TOTAL.labels(
        action_type=action_type,
        integration_type=integration_type,
        operation=operation,
    ).inc()


__all__ = [
    "AI_ACTION_APPROVAL_DECISIONS_TOTAL",
    "AI_ACTION_EXECUTION_OUTCOMES_TOTAL",
    "AI_ACTION_POLICY_BLOCKS_TOTAL",
    "AI_ACTION_PROPOSALS_TOTAL",
    "record_action_proposed",
    "record_approval_decision",
    "record_execution_outcome",
    "record_policy_block",
]
