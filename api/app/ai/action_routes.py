"""AI agent action routes — list, inspect, approve, and reject lifecycle records."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service
from app.ai.models import AgentAction, AgentActionApproval
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_permission
from app.auth.permissions import AI_APPROVE
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


class ApprovalResponse(BaseModel):
    id: str
    status: str
    requested_by_user_id: str | None
    reviewed_by_user_id: str | None
    reason: str | None
    expires_at: str | None
    reviewed_at: str | None
    created_at: str

    @classmethod
    def from_orm_obj(cls, approval: AgentActionApproval) -> ApprovalResponse:
        return cls(
            id=str(approval.id),
            status=approval.status,
            requested_by_user_id=str(approval.requested_by_user_id) if approval.requested_by_user_id else None,
            reviewed_by_user_id=str(approval.reviewed_by_user_id) if approval.reviewed_by_user_id else None,
            reason=approval.reason,
            expires_at=approval.expires_at.isoformat() if approval.expires_at else None,
            reviewed_at=approval.reviewed_at.isoformat() if approval.reviewed_at else None,
            created_at=approval.created_at.isoformat(),
        )


class PendingApprovalResponse(BaseModel):
    id: str
    requested_by_user_id: str | None
    reason: str | None
    expires_at: str | None
    created_at: str

    @classmethod
    def from_orm_obj(cls, approval: AgentActionApproval) -> PendingApprovalResponse:
        return cls(
            id=str(approval.id),
            requested_by_user_id=str(approval.requested_by_user_id) if approval.requested_by_user_id else None,
            reason=approval.reason,
            expires_at=approval.expires_at.isoformat() if approval.expires_at else None,
            created_at=approval.created_at.isoformat(),
        )


class AgentActionProposalApprovalResponse(BaseModel):
    required: bool
    status: str
    reason: str | None
    expires_at: str | None


class AgentActionProposalStepResponse(BaseModel):
    key: str
    label: str
    status: str
    description: str
    required: bool | None = None


class AgentActionProposalResponse(BaseModel):
    headline: str
    summary: str | None
    confidence: float | None
    phase: str | None
    surface: str
    steps: list[AgentActionProposalStepResponse]
    evidence: dict | None
    context: dict | None
    approval: AgentActionProposalApprovalResponse


class AgentActionResponse(BaseModel):
    id: str
    conversation_id: str | None
    grow_cycle_id: str | None
    source: str
    action_type: str
    title: str
    status: str
    risk_level: str
    requires_approval: bool
    auto_approved: bool
    summary: str | None
    proposal: AgentActionProposalResponse
    pending_approval: PendingApprovalResponse | None
    metadata_json: dict | None
    evidence_json: dict | None
    execution_json: dict | None
    verification_json: dict | None
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_obj(cls, action: AgentAction) -> AgentActionResponse:
        pending_approval = service.get_pending_approval(action)
        return cls(
            id=str(action.id),
            conversation_id=str(action.conversation_id) if action.conversation_id else None,
            grow_cycle_id=str(action.grow_cycle_id) if action.grow_cycle_id else None,
            source=action.source,
            action_type=action.action_type,
            title=action.title,
            status=action.status,
            risk_level=action.risk_level,
            requires_approval=action.requires_approval,
            auto_approved=action.auto_approved,
            summary=action.summary,
            proposal=AgentActionProposalResponse.model_validate(service.build_agent_action_proposal(action)),
            pending_approval=(
                PendingApprovalResponse.from_orm_obj(pending_approval) if pending_approval is not None else None
            ),
            metadata_json=action.metadata_json,
            evidence_json=action.evidence_json,
            execution_json=action.execution_json,
            verification_json=action.verification_json,
            created_at=action.created_at.isoformat(),
            updated_at=action.updated_at.isoformat(),
        )


class AgentActionDetailResponse(AgentActionResponse):
    approvals: list[ApprovalResponse]


class ApprovalDecisionBody(BaseModel):
    reason: str | None = None


@router.get("/actions", response_model=PaginatedResponse[AgentActionResponse])
async def list_agent_actions(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: str | None = None,
    status: str | None = None,
):
    """List AI agent actions for the current tenant."""
    assert user.tenant_id is not None
    try:
        grow_id = service.parse_optional_uuid(grow_cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid grow_cycle_id") from exc

    query = service.list_agent_actions_query(tenant_id=user.tenant_id, grow_cycle_id=grow_id, status=status)
    items, total = await paginate(session, query, pagination)
    return PaginatedResponse(
        items=[AgentActionResponse.from_orm_obj(item) for item in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/actions/{action_id}", response_model=AgentActionDetailResponse)
async def get_agent_action(
    action_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get one AI agent action with approval history."""
    assert user.tenant_id is not None
    action = await service.get_agent_action_with_approvals(session, tenant_id=user.tenant_id, action_id=action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Agent action not found")

    return AgentActionDetailResponse(
        **AgentActionResponse.from_orm_obj(action).model_dump(),
        approvals=[ApprovalResponse.from_orm_obj(item) for item in action.approvals],
    )


@router.post("/actions/{action_id}/approve", response_model=AgentActionDetailResponse)
async def approve_agent_action(
    action_id: UUID,
    body: ApprovalDecisionBody,
    user: Annotated[CurrentUser, Depends(require_permission(AI_APPROVE))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Approve a pending AI agent action."""
    assert user.tenant_id is not None
    action = await service.get_agent_action_with_approvals(session, tenant_id=user.tenant_id, action_id=action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Agent action not found")

    try:
        await service.approve_agent_action(
            session,
            action,
            reviewed_by_user_id=user.user_id,
            reason=body.reason,
        )
    except service.AgentActionApprovalMissingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except service.InvalidAgentActionTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except service.InvalidAgentApprovalTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    refreshed = await service.get_agent_action_with_approvals(session, tenant_id=user.tenant_id, action_id=action_id)
    assert refreshed is not None
    return AgentActionDetailResponse(
        **AgentActionResponse.from_orm_obj(refreshed).model_dump(),
        approvals=[ApprovalResponse.from_orm_obj(item) for item in refreshed.approvals],
    )


@router.post("/actions/{action_id}/reject", response_model=AgentActionDetailResponse)
async def reject_agent_action(
    action_id: UUID,
    body: ApprovalDecisionBody,
    user: Annotated[CurrentUser, Depends(require_permission(AI_APPROVE))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Reject a pending AI agent action."""
    assert user.tenant_id is not None
    action = await service.get_agent_action_with_approvals(session, tenant_id=user.tenant_id, action_id=action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Agent action not found")

    try:
        await service.reject_agent_action(
            session,
            action,
            reviewed_by_user_id=user.user_id,
            reason=body.reason,
        )
    except service.AgentActionApprovalMissingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except service.InvalidAgentActionTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except service.InvalidAgentApprovalTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    refreshed = await service.get_agent_action_with_approvals(session, tenant_id=user.tenant_id, action_id=action_id)
    assert refreshed is not None
    return AgentActionDetailResponse(
        **AgentActionResponse.from_orm_obj(refreshed).model_dump(),
        approvals=[ApprovalResponse.from_orm_obj(item) for item in refreshed.approvals],
    )
