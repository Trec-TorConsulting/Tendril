"""AI domain service.

Holds the business operations for AI features: conversation persistence
(this file), diagnosis flow (added in 3.11b), and the core AI route
helpers (added in 3.11c).

Route handlers in ``app.ai.*_routes`` are HTTP-only and delegate to
this module.

Conventions match the project standard (PR #192 / #208-#220):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM models, dataclasses, or primitives; they never
  raise ``HTTPException`` — lookup misses return ``None`` and domain
  validation failures raise typed errors.
* Query-builder helpers (``*_query``) return ``Select`` for the route
  layer to paginate.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.models import AgentAction, AgentActionApproval, Conversation, ConversationMessage

AGENT_ACTION_STATUS_PROPOSED = "proposed"
AGENT_ACTION_STATUS_PENDING_APPROVAL = "pending_approval"
AGENT_ACTION_STATUS_APPROVED = "approved"
AGENT_ACTION_STATUS_EXECUTING = "executing"
AGENT_ACTION_STATUS_COMPLETED = "completed"
AGENT_ACTION_STATUS_VERIFIED = "verified"
AGENT_ACTION_STATUS_BLOCKED = "blocked"
AGENT_ACTION_STATUS_REJECTED = "rejected"
AGENT_ACTION_STATUS_EXPIRED = "expired"
AGENT_ACTION_STATUS_FAILED = "failed"
AGENT_ACTION_STATUS_CANCELLED = "cancelled"

AGENT_APPROVAL_STATUS_PENDING = "pending"
AGENT_APPROVAL_STATUS_APPROVED = "approved"
AGENT_APPROVAL_STATUS_REJECTED = "rejected"
AGENT_APPROVAL_STATUS_EXPIRED = "expired"

TERMINAL_AGENT_ACTION_STATUSES = frozenset(
    {
        AGENT_ACTION_STATUS_VERIFIED,
        AGENT_ACTION_STATUS_BLOCKED,
        AGENT_ACTION_STATUS_REJECTED,
        AGENT_ACTION_STATUS_EXPIRED,
        AGENT_ACTION_STATUS_FAILED,
        AGENT_ACTION_STATUS_CANCELLED,
    }
)

ALLOWED_AGENT_ACTION_TRANSITIONS: dict[str, frozenset[str]] = {
    AGENT_ACTION_STATUS_PROPOSED: frozenset(
        {
            AGENT_ACTION_STATUS_PENDING_APPROVAL,
            AGENT_ACTION_STATUS_APPROVED,
            AGENT_ACTION_STATUS_BLOCKED,
            AGENT_ACTION_STATUS_CANCELLED,
        }
    ),
    AGENT_ACTION_STATUS_PENDING_APPROVAL: frozenset(
        {
            AGENT_ACTION_STATUS_APPROVED,
            AGENT_ACTION_STATUS_REJECTED,
            AGENT_ACTION_STATUS_EXPIRED,
            AGENT_ACTION_STATUS_CANCELLED,
        }
    ),
    AGENT_ACTION_STATUS_APPROVED: frozenset(
        {
            AGENT_ACTION_STATUS_EXECUTING,
            AGENT_ACTION_STATUS_CANCELLED,
        }
    ),
    AGENT_ACTION_STATUS_EXECUTING: frozenset(
        {
            AGENT_ACTION_STATUS_COMPLETED,
            AGENT_ACTION_STATUS_FAILED,
            AGENT_ACTION_STATUS_BLOCKED,
        }
    ),
    AGENT_ACTION_STATUS_COMPLETED: frozenset(
        {
            AGENT_ACTION_STATUS_VERIFIED,
            AGENT_ACTION_STATUS_FAILED,
        }
    ),
}


class InvalidAgentActionTransitionError(Exception):
    """Raised when an agent action attempts an invalid lifecycle transition."""


class InvalidAgentApprovalTransitionError(Exception):
    """Raised when an approval record attempts an invalid lifecycle transition."""


class AgentActionApprovalMissingError(Exception):
    """Raised when an action approval decision is requested without a pending approval."""

# ─────────────────────────────────────────────────────────────────────────────
# Conversations
# ─────────────────────────────────────────────────────────────────────────────


def build_agent_action_idempotency_key(
    *,
    tenant_id: UUID,
    source: str,
    action_type: str,
    grow_cycle_id: UUID | None,
    conversation_id: UUID | None,
    dedupe_token: str | None = None,
) -> str:
    """Build a deterministic idempotency key for one logical action."""
    raw = "|".join(
        [
            str(tenant_id),
            source,
            action_type,
            str(grow_cycle_id or ""),
            str(conversation_id or ""),
            dedupe_token or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def classify_health_check_action(action_text: str) -> tuple[str, bool, bool, str]:
    """Classify a health-check recommendation into a lifecycle action policy.

    Returns `(action_type, requires_approval, auto_approved, risk_level)`.
    Phase 1 treats direct equipment/control-style commands as approval-gated.
    """
    normalized = action_text.strip().lower()
    control_markers = (
        "turn on",
        "turn off",
        "set ",
        "increase fan",
        "decrease fan",
        "raise fan",
        "lower fan",
        "start pump",
        "stop pump",
        "toggle",
        "enable",
        "disable",
        "dim light",
        "raise light",
        "lower light",
        "increase light",
        "decrease light",
    )
    if any(marker in normalized for marker in control_markers):
        return ("control_equipment", True, False, "high")
    return ("create_task", False, True, "low")


async def create_agent_action(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    source: str,
    action_type: str,
    title: str,
    idempotency_key: str,
    conversation_id: UUID | None = None,
    grow_cycle_id: UUID | None = None,
    created_by_user_id: UUID | None = None,
    risk_level: str = "low",
    requires_approval: bool = False,
    auto_approved: bool = False,
    summary: str | None = None,
    metadata_json: dict | None = None,
    evidence_json: dict | None = None,
) -> AgentAction:
    """Create and persist an agent action lifecycle record."""
    action = AgentAction(
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        grow_cycle_id=grow_cycle_id,
        created_by_user_id=created_by_user_id,
        source=source,
        action_type=action_type,
        title=title,
        status=AGENT_ACTION_STATUS_PROPOSED,
        idempotency_key=idempotency_key,
        risk_level=risk_level,
        requires_approval=requires_approval,
        auto_approved=auto_approved,
        summary=summary,
        metadata_json=metadata_json or {},
        evidence_json=evidence_json or {},
    )
    session.add(action)
    await session.commit()
    await session.refresh(action)
    return action


async def create_agent_action_approval(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    action_id: UUID,
    requested_by_user_id: UUID | None,
    expires_at: datetime | None = None,
    reason: str | None = None,
) -> AgentActionApproval:
    """Create a pending approval record for an agent action."""
    approval = AgentActionApproval(
        tenant_id=tenant_id,
        action_id=action_id,
        requested_by_user_id=requested_by_user_id,
        status=AGENT_APPROVAL_STATUS_PENDING,
        expires_at=expires_at,
        reason=reason,
    )
    session.add(approval)
    await session.commit()
    await session.refresh(approval)
    return approval


def can_transition_agent_action(current_status: str, next_status: str) -> bool:
    """Return whether an action status change is valid."""
    if current_status == next_status:
        return True
    return next_status in ALLOWED_AGENT_ACTION_TRANSITIONS.get(current_status, frozenset())


async def transition_agent_action(
    session: AsyncSession,
    action: AgentAction,
    *,
    next_status: str,
    execution_json: dict | None = None,
    verification_json: dict | None = None,
    metadata_json: dict | None = None,
) -> AgentAction:
    """Persist one valid action lifecycle transition."""
    if not can_transition_agent_action(action.status, next_status):
        raise InvalidAgentActionTransitionError(f"Invalid action transition: {action.status} -> {next_status}")

    now = datetime.now(UTC)
    action.status = next_status
    if metadata_json is not None:
        action.metadata_json = metadata_json
    if execution_json is not None:
        action.execution_json = execution_json
    if verification_json is not None:
        action.verification_json = verification_json

    if next_status == AGENT_ACTION_STATUS_APPROVED:
        action.approved_at = now
    elif next_status == AGENT_ACTION_STATUS_EXECUTING:
        action.executed_at = now
    elif next_status == AGENT_ACTION_STATUS_VERIFIED:
        action.verified_at = now

    await session.commit()
    await session.refresh(action)
    return action


async def record_agent_action_approval_decision(
    session: AsyncSession,
    approval: AgentActionApproval,
    *,
    decision_status: str,
    reviewed_by_user_id: UUID | None,
    reason: str | None = None,
) -> AgentActionApproval:
    """Persist an approval decision from pending to a terminal state."""
    if approval.status != AGENT_APPROVAL_STATUS_PENDING:
        raise InvalidAgentApprovalTransitionError(
            f"Invalid approval transition: {approval.status} -> {decision_status}"
        )
    if decision_status not in {
        AGENT_APPROVAL_STATUS_APPROVED,
        AGENT_APPROVAL_STATUS_REJECTED,
        AGENT_APPROVAL_STATUS_EXPIRED,
    }:
        raise InvalidAgentApprovalTransitionError(
            f"Invalid approval transition: {approval.status} -> {decision_status}"
        )

    approval.status = decision_status
    approval.reviewed_by_user_id = reviewed_by_user_id
    approval.reviewed_at = datetime.now(UTC)
    if reason is not None:
        approval.reason = reason
    await session.commit()
    await session.refresh(approval)
    return approval


async def record_health_check_task_actions(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID,
    requested_by_user_id: UUID | None,
    health_eval_id: UUID,
    score: int | None,
    issues: list[str],
    actions: list[str],
    created_task_count: int,
    task_error: str | None = None,
) -> list[AgentAction]:
    """Record lifecycle-tracked agent actions for health-check task creation.

    Phase 1 treats health-check task creation as a safe auto-approved action.
    One lifecycle record is created per recommended action string.
    """
    recorded: list[AgentAction] = []
    tasks_created_remaining = created_task_count

    for index, action_text in enumerate(actions):
        action_type, requires_approval, auto_approved, risk_level = classify_health_check_action(action_text)
        action = await create_agent_action(
            session,
            tenant_id=tenant_id,
            source="health_check",
            action_type=action_type,
            title=action_text[:255],
            idempotency_key=build_agent_action_idempotency_key(
                tenant_id=tenant_id,
                source="health_check",
                action_type=action_type,
                grow_cycle_id=grow_cycle_id,
                conversation_id=None,
                dedupe_token=f"{health_eval_id}:{index}:{action_text}",
            ),
            grow_cycle_id=grow_cycle_id,
            created_by_user_id=requested_by_user_id,
            risk_level=risk_level,
            requires_approval=requires_approval,
            auto_approved=auto_approved,
            summary=action_text,
            metadata_json={
                "health_eval_id": str(health_eval_id),
                "health_score": score,
                "issues": issues,
                "phase": "health_check",
                "safe_action": auto_approved,
            },
            evidence_json={
                "recommended_action": action_text,
                "issue_count": len(issues),
            },
        )

        if requires_approval:
            await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_PENDING_APPROVAL)
            await create_agent_action_approval(
                session,
                tenant_id=tenant_id,
                action_id=action.id,
                requested_by_user_id=requested_by_user_id,
                reason="Health-check action requires approval before execution",
            )
            recorded.append(action)
            continue

        await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_APPROVED)
        await transition_agent_action(
            session,
            action,
            next_status=AGENT_ACTION_STATUS_EXECUTING,
            execution_json={"target": "task", "health_eval_id": str(health_eval_id)},
        )

        if task_error is not None or tasks_created_remaining <= 0:
            await transition_agent_action(
                session,
                action,
                next_status=AGENT_ACTION_STATUS_FAILED,
                execution_json={
                    "target": "task",
                    "health_eval_id": str(health_eval_id),
                    "error": task_error or "No task was created for this health-check action",
                },
            )
        else:
            await transition_agent_action(
                session,
                action,
                next_status=AGENT_ACTION_STATUS_COMPLETED,
                execution_json={
                    "target": "task",
                    "health_eval_id": str(health_eval_id),
                    "tasks_created": 1,
                },
            )
            await transition_agent_action(
                session,
                action,
                next_status=AGENT_ACTION_STATUS_VERIFIED,
                verification_json={
                    "result": "task_created",
                    "health_eval_id": str(health_eval_id),
                },
            )
            tasks_created_remaining -= 1

        recorded.append(action)

    return recorded


def split_health_check_actions_by_safety(actions: list[str]) -> tuple[list[str], list[str]]:
    """Split health-check actions into safe-task and approval-required groups."""
    safe_actions: list[str] = []
    approval_actions: list[str] = []
    for action_text in actions:
        action_type, requires_approval, _auto_approved, _risk_level = classify_health_check_action(action_text)
        if action_type == "create_task" and not requires_approval:
            safe_actions.append(action_text)
        else:
            approval_actions.append(action_text)
    return safe_actions, approval_actions


def build_agent_action_lifecycle_steps(action: AgentAction) -> list[dict[str, object]]:
    """Build a UI-oriented lifecycle plan for one agent action."""

    def approval_step_status() -> str:
        if not action.requires_approval:
            return "skipped"
        if action.status == AGENT_ACTION_STATUS_PENDING_APPROVAL:
            return "current"
        if action.status in {
            AGENT_ACTION_STATUS_APPROVED,
            AGENT_ACTION_STATUS_EXECUTING,
            AGENT_ACTION_STATUS_COMPLETED,
            AGENT_ACTION_STATUS_VERIFIED,
            AGENT_ACTION_STATUS_FAILED,
            AGENT_ACTION_STATUS_BLOCKED,
        }:
            return "completed"
        if action.status in {
            AGENT_ACTION_STATUS_REJECTED,
            AGENT_ACTION_STATUS_EXPIRED,
            AGENT_ACTION_STATUS_CANCELLED,
        }:
            return "blocked"
        return "pending"

    def execution_step_status() -> str:
        if action.status == AGENT_ACTION_STATUS_EXECUTING:
            return "current"
        if action.status in {
            AGENT_ACTION_STATUS_COMPLETED,
            AGENT_ACTION_STATUS_VERIFIED,
        }:
            return "completed"
        if action.status == AGENT_ACTION_STATUS_FAILED:
            return "failed"
        if action.status in {
            AGENT_ACTION_STATUS_BLOCKED,
            AGENT_ACTION_STATUS_REJECTED,
            AGENT_ACTION_STATUS_EXPIRED,
            AGENT_ACTION_STATUS_CANCELLED,
        }:
            return "blocked"
        return "pending"

    def verification_step_status() -> str:
        if action.status == AGENT_ACTION_STATUS_VERIFIED:
            return "completed"
        if action.status == AGENT_ACTION_STATUS_COMPLETED:
            return "current"
        if action.status in {
            AGENT_ACTION_STATUS_FAILED,
            AGENT_ACTION_STATUS_BLOCKED,
            AGENT_ACTION_STATUS_REJECTED,
            AGENT_ACTION_STATUS_EXPIRED,
            AGENT_ACTION_STATUS_CANCELLED,
        }:
            return "blocked"
        return "pending"

    return [
        {
            "key": "observe",
            "label": "Observe",
            "status": "completed",
            "description": "Collect grow signals and evidence for this recommendation.",
        },
        {
            "key": "plan",
            "label": "Plan",
            "status": "completed",
            "description": "Convert the recommendation into a lifecycle-tracked action proposal.",
        },
        {
            "key": "approve",
            "label": "Approve",
            "status": approval_step_status(),
            "description": "Wait for an authorized approver when the action is not in the safe auto-approve set.",
            "required": action.requires_approval,
        },
        {
            "key": "execute",
            "label": "Execute",
            "status": execution_step_status(),
            "description": "Run the approved action and capture execution evidence.",
        },
        {
            "key": "verify",
            "label": "Verify",
            "status": verification_step_status(),
            "description": "Confirm the expected postcondition and store the result.",
        },
    ]


def list_agent_actions_query(
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID | None = None,
    status: str | None = None,
) -> Select:
    """Build the listing query for tenant-scoped AI agent actions."""
    query = (
        select(AgentAction)
        .options(selectinload(AgentAction.approvals))
        .where(AgentAction.tenant_id == tenant_id)
        .order_by(desc(AgentAction.created_at))
    )
    if grow_cycle_id is not None:
        query = query.where(AgentAction.grow_cycle_id == grow_cycle_id)
    if status is not None:
        query = query.where(AgentAction.status == status)
    return query


async def get_agent_action(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    action_id: UUID,
) -> AgentAction | None:
    """Fetch one tenant-scoped AI agent action."""
    action = await session.get(AgentAction, action_id)
    if action is None or action.tenant_id != tenant_id:
        return None
    return action


async def get_agent_action_with_approvals(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    action_id: UUID,
) -> AgentAction | None:
    """Fetch one tenant-scoped AI agent action with approvals eager-loaded."""
    result = await session.execute(
        select(AgentAction)
        .options(selectinload(AgentAction.approvals))
        .where(AgentAction.id == action_id, AgentAction.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


def get_pending_approval(action: AgentAction) -> AgentActionApproval | None:
    """Return the pending approval row for an action, if present."""
    for approval in action.approvals:
        if approval.status == AGENT_APPROVAL_STATUS_PENDING:
            return approval
    return None


def get_latest_approval(action: AgentAction) -> AgentActionApproval | None:
    """Return the latest approval row for an action, if present."""
    if not action.approvals:
        return None
    return action.approvals[-1]


def build_agent_action_proposal(action: AgentAction) -> dict[str, object]:
    """Build a normalized proposal payload for UI consumers."""
    metadata = action.metadata_json or {}
    evidence_json = action.evidence_json or {}
    approval = get_pending_approval(action) or get_latest_approval(action)

    evidence: dict[str, object] = {
        "recommended_action": evidence_json.get("recommended_action") or action.summary or action.title,
    }
    if evidence_json.get("issue_count") is not None:
        evidence["issue_count"] = evidence_json["issue_count"]
    if evidence_json.get("integration_id") is not None:
        evidence["integration_id"] = evidence_json["integration_id"]
    if evidence_json.get("integration_type") is not None:
        evidence["integration_type"] = evidence_json["integration_type"]
    if evidence_json.get("operation") is not None:
        evidence["operation"] = evidence_json["operation"]
    if evidence_json.get("command") is not None:
        evidence["command"] = evidence_json["command"]

    context: dict[str, object] = {}
    if metadata.get("phase") is not None:
        context["phase"] = metadata["phase"]
    if metadata.get("health_eval_id") is not None:
        context["health_eval_id"] = metadata["health_eval_id"]
    if metadata.get("health_score") is not None:
        context["health_score"] = metadata["health_score"]
    if metadata.get("issues") is not None:
        context["issues"] = metadata["issues"]
    if metadata.get("safe_action") is not None:
        context["safe_action"] = metadata["safe_action"]
    if metadata.get("integration_id") is not None:
        context["integration_id"] = metadata["integration_id"]
    if metadata.get("integration_name") is not None:
        context["integration_name"] = metadata["integration_name"]
    if metadata.get("integration_type") is not None:
        context["integration_type"] = metadata["integration_type"]
    if metadata.get("operation") is not None:
        context["operation"] = metadata["operation"]
    if metadata.get("command") is not None:
        context["command"] = metadata["command"]
    policy = metadata.get("policy")
    if isinstance(policy, dict):
        if policy.get("risk_level") is not None:
            context["policy_risk_level"] = policy["risk_level"]
        if policy.get("requires_simulation") is not None:
            context["requires_simulation"] = policy["requires_simulation"]

    return {
        "headline": action.title,
        "summary": action.summary,
        "confidence": metadata.get("planner_confidence"),
        "phase": metadata.get("phase"),
        "surface": "ai_side_panel",
        "steps": build_agent_action_lifecycle_steps(action),
        "evidence": evidence,
        "context": context or None,
        "approval": {
            "required": action.requires_approval,
            "status": approval.status if approval is not None else "not_required",
            "reason": approval.reason if approval is not None else None,
            "expires_at": approval.expires_at.isoformat() if approval and approval.expires_at else None,
        },
    }


async def approve_agent_action(
    session: AsyncSession,
    action: AgentAction,
    *,
    reviewed_by_user_id: UUID,
    reason: str | None = None,
) -> AgentAction:
    """Approve an action currently waiting on approval."""
    approval = get_pending_approval(action)
    if approval is None:
        raise AgentActionApprovalMissingError("Action has no pending approval")

    await record_agent_action_approval_decision(
        session,
        approval,
        decision_status=AGENT_APPROVAL_STATUS_APPROVED,
        reviewed_by_user_id=reviewed_by_user_id,
        reason=reason,
    )
    return await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_APPROVED)


async def reject_agent_action(
    session: AsyncSession,
    action: AgentAction,
    *,
    reviewed_by_user_id: UUID,
    reason: str | None = None,
) -> AgentAction:
    """Reject an action currently waiting on approval."""
    approval = get_pending_approval(action)
    if approval is None:
        raise AgentActionApprovalMissingError("Action has no pending approval")

    await record_agent_action_approval_decision(
        session,
        approval,
        decision_status=AGENT_APPROVAL_STATUS_REJECTED,
        reviewed_by_user_id=reviewed_by_user_id,
        reason=reason,
    )
    return await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_REJECTED)


async def create_conversation(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    user_id: UUID,
    grow_cycle_id: UUID | None,
    title: str | None,
) -> Conversation:
    """Create a new AI conversation owned by ``user_id`` in ``tenant_id``."""
    conv = Conversation(
        tenant_id=tenant_id,
        user_id=user_id,
        grow_cycle_id=grow_cycle_id,
        title=title,
    )
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


def list_user_conversations_query(
    *,
    tenant_id: UUID,
    user_id: UUID,
    grow_cycle_id: UUID | None = None,
) -> Select:
    """Build the listing query (most-recently-updated first); route paginates."""
    q = (
        select(Conversation)
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == user_id,
        )
        .order_by(desc(Conversation.updated_at))
    )
    if grow_cycle_id is not None:
        q = q.where(Conversation.grow_cycle_id == grow_cycle_id)
    return q


async def get_conversation(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: UUID,
) -> Conversation | None:
    """Fetch a conversation only if it belongs to ``tenant_id``.

    Returns ``None`` for unknown ids and cross-tenant access alike —
    the route maps either to 404 so we don't leak existence.
    """
    conv = await session.get(Conversation, conversation_id)
    if conv is None or conv.tenant_id != tenant_id:
        return None
    return conv


async def get_conversation_with_messages(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: UUID,
) -> Conversation | None:
    """Same as :func:`get_conversation` but eager-loads ``messages``."""
    result = await session.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def update_conversation_title(
    session: AsyncSession,
    conv: Conversation,
    *,
    title: str,
) -> Conversation:
    conv.title = title
    await session.commit()
    await session.refresh(conv)
    return conv


async def delete_conversation(session: AsyncSession, conv: Conversation) -> None:
    await session.delete(conv)
    await session.commit()


def parse_optional_uuid(value: str | None) -> UUID | None:
    """Pure helper — convert a string/None to ``UUID``/None.

    Raises ``ValueError`` on malformed input; route layer maps to 422.
    Centralised so we don't have ``UUID(x) if x else None`` peppered
    through the route file.
    """
    if value is None or value == "":
        return None
    return UUID(value)


# Type re-export — keeps ``service.ConversationMessage`` and
# ``service.Conversation`` available to callers that want a single
# import surface for the AI domain.
__all__ = [
    "AGENT_ACTION_STATUS_APPROVED",
    "AGENT_ACTION_STATUS_BLOCKED",
    "AGENT_ACTION_STATUS_CANCELLED",
    "AGENT_ACTION_STATUS_COMPLETED",
    "AGENT_ACTION_STATUS_EXECUTING",
    "AGENT_ACTION_STATUS_EXPIRED",
    "AGENT_ACTION_STATUS_FAILED",
    "AGENT_ACTION_STATUS_PENDING_APPROVAL",
    "AGENT_ACTION_STATUS_PROPOSED",
    "AGENT_ACTION_STATUS_REJECTED",
    "AGENT_ACTION_STATUS_VERIFIED",
    "AGENT_APPROVAL_STATUS_APPROVED",
    "AGENT_APPROVAL_STATUS_EXPIRED",
    "AGENT_APPROVAL_STATUS_PENDING",
    "AGENT_APPROVAL_STATUS_REJECTED",
    "AgentAction",
    "AgentActionApproval",
    "AgentActionApprovalMissingError",
    "Conversation",
    "ConversationMessage",
    "InvalidAgentActionTransitionError",
    "InvalidAgentApprovalTransitionError",
    "approve_agent_action",
    "build_agent_action_idempotency_key",
    "build_agent_action_lifecycle_steps",
    "build_agent_action_proposal",
    "can_transition_agent_action",
    "classify_health_check_action",
    "create_agent_action",
    "create_agent_action_approval",
    "create_conversation",
    "delete_conversation",
    "get_agent_action",
    "get_agent_action_with_approvals",
    "get_conversation",
    "get_conversation_with_messages",
    "get_latest_approval",
    "get_pending_approval",
    "list_agent_actions_query",
    "list_user_conversations_query",
    "parse_optional_uuid",
    "record_agent_action_approval_decision",
    "record_health_check_task_actions",
    "reject_agent_action",
    "split_health_check_actions_by_safety",
    "transition_agent_action",
    "update_conversation_title",
]


# ─────────────────────────────────────────────────────────────────────────────
# Diagnose — plant-photo health analysis
# ─────────────────────────────────────────────────────────────────────────────


from dataclasses import dataclass as _dc  # noqa: E402  (kept with section)

# Max accepted photo size for the /diagnose endpoint. 10 MiB matches the
# upstream multipart limit on our reverse proxy + the Pulse/Pulse Wifi
# camera firmware's max single-snap size.
MAX_DIAGNOSE_IMAGE_BYTES: int = 10 * 1024 * 1024

# Default-fallback values returned when the LLM response can't be parsed
# as JSON. Kept here so the route doesn't have to know the defaults.
DEFAULT_DIAGNOSIS_OVERALL_SEVERITY: str = "medium"
DEFAULT_DIAGNOSIS_OVERALL_SCORE: int = 50


# ---- Errors ----


class DiagnoseImageError(Exception):
    """Raised when the request's base64 image is malformed or too large.

    Route maps to HTTP 400.
    """


# ---- Image validation ----


def decode_diagnose_image(image_base64: str) -> bytes:
    """Decode the request's base64 image and enforce the size cap.

    Raises :class:`DiagnoseImageError` for malformed base64 or oversize
    payloads. The cap is documented in
    :data:`MAX_DIAGNOSE_IMAGE_BYTES`.
    """
    import base64 as _b64

    try:
        image_bytes = _b64.b64decode(image_base64)
    except Exception as exc:
        raise DiagnoseImageError("Invalid base64 image data") from exc

    if len(image_bytes) > MAX_DIAGNOSE_IMAGE_BYTES:
        raise DiagnoseImageError(f"Image exceeds {MAX_DIAGNOSE_IMAGE_BYTES // (1024 * 1024)}MB limit")
    return image_bytes


# ---- Prompt building ----


# The instruction block sent to the vision model. Pulled out here so the
# route layer doesn't carry production prompt text (and so tests can
# assert structural properties).
DIAGNOSIS_SYSTEM_PROMPT: str = """You are Tendril, an expert cannabis plant health diagnostic AI.
Analyze the provided photo and identify any health issues.

You MUST respond with valid JSON in this exact format:
{
  "issues": [
    {
      "treatment_id": "nitrogen_deficiency",
      "name": "Nitrogen Deficiency",
      "confidence": 0.85,
      "severity": "medium",
      "description": "Brief description of what you see that indicates this issue",
      "treatment": "Brief recommended treatment action"
    }
  ],
  "summary": "Brief 1-2 sentence summary of what you see",
  "recommended_actions": ["Action 1", "Action 2"],
  "overall_severity": "medium",
  "overall_score": 65,
  "grow_stage_assessment": "Early flower, week 2-3"
}

Valid treatment_ids: nitrogen_deficiency, phosphorus_deficiency, potassium_deficiency,
calcium_deficiency, magnesium_deficiency, iron_deficiency, spider_mites, fungus_gnats,
thrips, powdery_mildew, botrytis, root_rot, light_burn, heat_stress, overwatering, ph_lockout

Severity levels: low, medium, high, critical
Confidence: 0.0 to 1.0 (how sure you are of each diagnosis)
overall_score: 0-100 (100 = perfectly healthy, 0 = dead)

If the plant looks healthy, return:
{"issues": [], "summary": "Plant appears healthy", "recommended_actions": [],
"overall_severity": "low", "overall_score": 95, "grow_stage_assessment": "..."}

Important rules:
- Only identify issues you can actually SEE in the photo
- Be conservative with confidence scores — don't overclaim
- Consider the grow type and stage when making recommendations
- Multiple issues can co-exist (e.g., pH lockout causing calcium deficiency)
- Provide a brief description for each issue explaining what visual evidence you see
- Provide a one-line treatment recommendation for each issue
"""


def build_diagnosis_prompt(
    grow_type: str | None = None,
    current_stage: str | None = None,
    observations: str | None = None,
) -> str:
    """Compose the vision-model prompt with optional grow context.

    The base prompt enumerates valid treatment_ids and the required
    JSON schema. ``grow_type`` / ``current_stage`` / ``observations``
    each contribute an additional context line. The instruction line
    at the end always asks for the JSON diagnosis.
    """
    prompt = DIAGNOSIS_SYSTEM_PROMPT

    context_parts: list[str] = []
    if grow_type:
        context_parts.append(f"Grow method: {grow_type}")
    if current_stage:
        context_parts.append(f"Current stage: {current_stage}")
    if observations:
        context_parts.append(f"Grower observations: {observations}")

    if context_parts:
        prompt += "\n\nContext:\n" + "\n".join(context_parts)

    prompt += "\n\nAnalyze the photo and provide your diagnosis as JSON."
    return prompt


# ---- Response parsing ----


@_dc(frozen=True, slots=True)
class ParsedDiagnosisIssue:
    """One issue extracted from the LLM JSON response."""

    treatment_id: str
    name: str
    confidence: float
    severity: str
    description: str
    treatment: str


@_dc(frozen=True, slots=True)
class ParsedDiagnosis:
    """The shape the route layer receives after parsing the LLM output.

    ``issues`` is empty when the LLM returns ``"issues": []`` (healthy)
    or when JSON parsing failed (route falls back to a "could not be
    parsed" summary).
    """

    summary: str
    actions: list[str]
    overall_severity: str
    overall_score: int
    grow_stage_assessment: str | None
    issues: list[ParsedDiagnosisIssue]


def _strip_markdown_fence(raw: str) -> str:
    """Strip a leading/trailing ```…``` fence the LLM sometimes adds.

    Matches previous route behaviour exactly:
    * leading ``` (optionally followed by a language tag and newline)
      is stripped,
    * trailing ``` is stripped,
    * surrounding whitespace is removed.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Drop everything up to and including the first newline (which
        # eats any language hint like ``json``), or just the ``` itself
        # if there's no newline.
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def parse_diagnosis_response(raw_response: str) -> ParsedDiagnosis:
    """Parse the LLM's raw text into a :class:`ParsedDiagnosis`.

    Robust against the model emitting fenced code blocks. On any JSON
    error returns a fallback diagnosis with the first 500 chars of
    ``raw_response`` as the summary and the documented default
    severity/score — same behaviour as the previous route.
    """
    import json as _json

    try:
        cleaned = _strip_markdown_fence(raw_response)
        parsed = _json.loads(cleaned)

        issues: list[ParsedDiagnosisIssue] = []
        for issue_data in parsed.get("issues", []):
            issues.append(
                ParsedDiagnosisIssue(
                    treatment_id=issue_data.get("treatment_id", "unknown"),
                    name=issue_data.get("name", "Unknown Issue"),
                    confidence=min(1.0, max(0.0, float(issue_data.get("confidence", 0.5)))),
                    severity=issue_data.get("severity", "medium"),
                    description=issue_data.get("description", ""),
                    treatment=issue_data.get("treatment", ""),
                )
            )

        return ParsedDiagnosis(
            summary=parsed.get("summary", ""),
            actions=parsed.get("recommended_actions", []),
            overall_severity=parsed.get("overall_severity", DEFAULT_DIAGNOSIS_OVERALL_SEVERITY),
            overall_score=int(parsed.get("overall_score", DEFAULT_DIAGNOSIS_OVERALL_SCORE)),
            grow_stage_assessment=parsed.get("grow_stage_assessment"),
            issues=issues,
        )
    except (_json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Fallback: return whatever raw text we got as the summary so
        # the user sees *something* useful.
        summary = raw_response[:500] if raw_response else "Diagnosis could not be parsed"
        return ParsedDiagnosis(
            summary=summary,
            actions=[],
            overall_severity=DEFAULT_DIAGNOSIS_OVERALL_SEVERITY,
            overall_score=DEFAULT_DIAGNOSIS_OVERALL_SCORE,
            grow_stage_assessment=None,
            issues=[],
        )


# ---- Treatment DB lookups ----


def list_treatments_query(*, category: str | None = None):
    """Build the listing query for the treatment reference table.

    Returns a SQLAlchemy ``Select``. Route layer doesn't paginate this
    one because the treatment library is small and the frontend uses
    the full list for autocomplete.
    """
    from sqlalchemy import select as _select

    from app.grows.models import PlantHealthTreatment

    q = _select(PlantHealthTreatment)
    if category:
        q = q.where(PlantHealthTreatment.category == category)
    return q.order_by(PlantHealthTreatment.category, PlantHealthTreatment.name)


def search_treatments_query(*, query_text: str):
    """Build the search query — case-insensitive ILIKE across name +
    summary + category. Returns a SQLAlchemy ``Select``.
    """
    from sqlalchemy import or_ as _or
    from sqlalchemy import select as _select

    from app.grows.models import PlantHealthTreatment

    search_term = f"%{query_text.lower()}%"
    return _select(PlantHealthTreatment).where(
        _or(
            PlantHealthTreatment.name.ilike(search_term),
            PlantHealthTreatment.summary.ilike(search_term),
            PlantHealthTreatment.category.ilike(search_term),
        )
    )


async def get_treatment(session: AsyncSession, treatment_id: str):
    """Fetch a treatment by id (str — treatments use string primary keys)."""
    from app.grows.models import PlantHealthTreatment

    return await session.get(PlantHealthTreatment, treatment_id)


# ─────────────────────────────────────────────────────────────────────────────
# Health-check helpers (shared with the main ai/routes.py module)
# ─────────────────────────────────────────────────────────────────────────────


def normalize_health_issue(issue) -> str:  # type: ignore[no-untyped-def]
    """Coerce an LLM-produced health issue (dict or str) into a display string.

    Matches the previous private ``_normalize_issue`` in ``ai/routes.py``
    byte-for-byte:

    * Strings pass through unchanged.
    * Dicts: try ``description``, then ``message``, then ``issue``. If a
      category is present, prefix with ``[category]``.
    * Anything else is rendered via ``str()`` as a last resort.
    """
    if isinstance(issue, str):
        return issue
    if isinstance(issue, dict):
        desc = issue.get("description") or issue.get("message") or issue.get("issue")
        if desc:
            cat = issue.get("category")
            return f"[{cat}] {desc}" if cat else str(desc)
    return str(issue)


def normalize_health_action(action) -> str:  # type: ignore[no-untyped-def]
    """Coerce an LLM-produced action (dict or str) into a display string.

    Strings pass through unchanged. For dicts, prefer ``action`` then
    ``message`` then ``description``; fall back to ``str()``.
    """
    if isinstance(action, str):
        return action
    if isinstance(action, dict):
        value = action.get("action") or action.get("message") or action.get("description")
        if value:
            return str(value)
    return str(action)


def normalize_health_history_issue(issue) -> str:  # type: ignore[no-untyped-def]
    """The history-listing endpoint uses a slightly narrower coercion than
    :func:`normalize_health_issue` — it does NOT add the ``[category]``
    prefix because the history rows render in a denser UI. Keep the two
    helpers separate so a future change to one doesn't silently shift the
    other.
    """
    if isinstance(issue, str):
        return issue
    if isinstance(issue, dict):
        return str(issue.get("message", issue.get("issue", str(issue))))
    return str(issue)


def normalize_health_history_action(action) -> str:  # type: ignore[no-untyped-def]
    """Action-side counterpart to :func:`normalize_health_history_issue`."""
    if isinstance(action, str):
        return action
    if isinstance(action, dict):
        return str(action.get("message", action.get("action", str(action))))
    return str(action)


def parse_health_check_json(raw: str) -> tuple[int | None, list, list]:
    """Parse an LLM health-check response into ``(score, issues, actions)``.

    Reuses :func:`_strip_markdown_fence` to handle the LLM's occasional
    fenced output. On JSON parse failure returns ``(None, [], [])`` —
    the route layer logs the failure and writes a HealthEval row with
    no parsed structure (matching previous behaviour).
    """
    import json as _json

    try:
        cleaned = _strip_markdown_fence(raw)
        parsed = _json.loads(cleaned)
    except _json.JSONDecodeError:
        return (None, [], [])

    score = parsed.get("score")
    raw_issues = parsed.get("issues", [])
    raw_actions = parsed.get("actions", [])
    issues = [normalize_health_issue(i) for i in raw_issues]
    actions = [normalize_health_action(a) for a in raw_actions]
    return (score, issues, actions)


# ─────────────────────────────────────────────────────────────────────────────
# Health-check queries
# ─────────────────────────────────────────────────────────────────────────────


# Hard cap on the history-list endpoint — prevents callers from asking
# for arbitrary page sizes that could starve the loop. Kept here so the
# route doesn't carry the magic number.
HEALTH_HISTORY_MAX_LIMIT: int = 50


def list_health_evals_query(*, grow_id: UUID, limit: int):
    """Build the listing query for health evaluations of ``grow_id``,
    most-recent first, capped at :data:`HEALTH_HISTORY_MAX_LIMIT`.
    """
    from sqlalchemy import select as _select

    from app.grows.models import HealthEval

    return (
        _select(HealthEval)
        .where(HealthEval.grow_cycle_id == grow_id)
        .order_by(desc(HealthEval.created_at))
        .limit(min(limit, HEALTH_HISTORY_MAX_LIMIT))
    )


async def get_health_eval(session: AsyncSession, eval_id: UUID):
    """Fetch a health evaluation by id. Route adds the tenant check."""
    from app.grows.models import HealthEval

    return await session.get(HealthEval, eval_id)


def build_photo_url_base() -> str:
    """Build the absolute base URL prefix used to construct photo URLs.

    Centralised so the host-resolution rule (``api.<domain>`` in prod,
    ``localhost:8000`` in dev) doesn't drift between the health-check
    response and the history-listing response.
    """
    from app.config import get_settings as _get_settings

    s = _get_settings()
    return f"https://api.{s.domain}/v1" if s.domain else "http://localhost:8000/v1"


def photo_url_for_key(storage_key: str | None) -> str | None:
    """Build the absolute photo URL for ``storage_key``, or ``None`` if
    the eval has no photo. Uses :func:`build_photo_url_base`.
    """
    if not storage_key:
        return None
    return f"{build_photo_url_base()}/photos/grow/key/{storage_key}"
