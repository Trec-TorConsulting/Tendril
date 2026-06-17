"""Admin support dashboard — ticket management, SLA tracking, metrics, channels.

This module is HTTP-only. All persistence, status transitions, metric
aggregation, and channel config writes live in ``app.support.service``.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, require_platform_admin, require_role
from app.database import async_session_factory
from app.support import service

router = APIRouter()
logger = logging.getLogger("tendril.support.admin")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ─── Schemas ──────────────────────────────────────────────────────────────────


class AssignTicketRequest(BaseModel):
    assigned_to_id: UUID


class UpdateTicketRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to_id: UUID | None = None
    tags: list[str] | None = None


class AdminMessageRequest(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False
    attachments: list[dict] | None = None


class BulkActionRequest(BaseModel):
    ticket_ids: list[UUID]
    action: str  # close, assign, change_priority, change_status
    value: str | None = None  # new status/priority or assignee ID


class CannedResponseCreate(BaseModel):
    title: str
    body: str
    category: str | None = None
    shortcut: str | None = None


class ChannelUpdateRequest(BaseModel):
    is_enabled: bool | None = None
    min_plan: str | None = None
    config_json: dict | None = None


class TicketMetricsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    overdue_tickets: int
    avg_first_response_hours: float | None
    avg_resolution_hours: float | None
    avg_satisfaction: float | None
    tickets_by_status: dict[str, int]
    tickets_by_priority: dict[str, int]


# ─── Ticket Management ────────────────────────────────────────────────────────


@router.get("/tickets", dependencies=[Depends(require_role("admin"))])
async def list_all_tickets(
    session: Annotated[AsyncSession, Depends(_get_db)],
    status: str | None = None,
    priority: str | None = None,
    assigned_to: UUID | None = None,
    category: str | None = None,
    overdue: bool | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict:
    """List all support tickets with filters."""
    tickets, total = await service.list_admin_tickets_page(
        session,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        category=category,
        overdue=overdue,
        page=page,
        per_page=per_page,
    )
    now = datetime.now(UTC)
    return {
        "tickets": [
            {
                "id": str(t.id),
                "subject": t.subject,
                "status": t.status,
                "priority": t.priority,
                "category": t.category,
                "assigned_to_id": str(t.assigned_to_id) if t.assigned_to_id else None,
                "tenant_id": str(t.tenant_id),
                "due_at": t.due_at.isoformat() if t.due_at else None,
                "is_overdue": t.due_at < now if t.due_at else False,
                "created_at": t.created_at.isoformat(),
                "updated_at": t.updated_at.isoformat(),
            }
            for t in tickets
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/tickets/{ticket_id}", dependencies=[Depends(require_role("admin"))])
async def get_ticket_admin(
    ticket_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Get full ticket detail including internal notes (admin view)."""
    ticket = await service.get_admin_ticket_with_messages(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return {
        "id": str(ticket.id),
        "subject": ticket.subject,
        "status": ticket.status,
        "priority": ticket.priority,
        "category": ticket.category,
        "tenant_id": str(ticket.tenant_id),
        "created_by_id": str(ticket.created_by_id),
        "assigned_to_id": str(ticket.assigned_to_id) if ticket.assigned_to_id else None,
        "due_at": ticket.due_at.isoformat() if ticket.due_at else None,
        "first_response_at": ticket.first_response_at.isoformat() if ticket.first_response_at else None,
        "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
        "satisfaction_rating": ticket.satisfaction_rating,
        "satisfaction_comment": ticket.satisfaction_comment,
        "tags": ticket.tags,
        "created_at": ticket.created_at.isoformat(),
        "updated_at": ticket.updated_at.isoformat(),
        "messages": [
            {
                "id": str(m.id),
                "author_id": str(m.author_id),
                "body": m.body,
                "is_internal": m.is_internal,
                "attachments": m.attachments,
                "created_at": m.created_at.isoformat(),
            }
            for m in ticket.messages
        ],
    }


@router.patch("/tickets/{ticket_id}", dependencies=[Depends(require_role("admin"))])
async def update_ticket_admin(
    ticket_id: UUID,
    body: UpdateTicketRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Update ticket status, priority, assignment, or tags."""
    ticket = await service.get_admin_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await service.update_admin_ticket(
        session,
        ticket,
        status=body.status,
        priority=body.priority,
        assigned_to_id=body.assigned_to_id,
        tags=body.tags,
    )
    return {"status": "updated"}


@router.post("/tickets/{ticket_id}/messages", dependencies=[Depends(require_role("admin"))])
async def add_admin_message(
    ticket_id: UUID,
    body: AdminMessageRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Add a message (reply or internal note) to a ticket."""
    ticket = await service.get_admin_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    message = await service.add_admin_message(
        session,
        ticket,
        author_id=user.user_id,
        body=body.body,
        is_internal=body.is_internal,
        attachments=body.attachments,
    )
    return {
        "id": str(message.id),
        "body": message.body,
        "is_internal": message.is_internal,
        "created_at": message.created_at.isoformat(),
    }


@router.post("/tickets/bulk", dependencies=[Depends(require_role("admin"))])
async def bulk_action(
    body: BulkActionRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Perform bulk actions on multiple tickets."""
    count = await service.bulk_update_tickets(session, ticket_ids=body.ticket_ids, action=body.action, value=body.value)
    return {"updated": count}


# ─── Metrics ──────────────────────────────────────────────────────────────────


@router.get("/metrics", dependencies=[Depends(require_role("admin"))])
async def ticket_metrics(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> TicketMetricsResponse:
    """Get support ticket metrics and KPIs."""
    metrics = await service.compute_ticket_metrics(session)
    return TicketMetricsResponse(
        total_tickets=metrics.total_tickets,
        open_tickets=metrics.open_tickets,
        overdue_tickets=metrics.overdue_tickets,
        avg_first_response_hours=metrics.avg_first_response_hours,
        avg_resolution_hours=metrics.avg_resolution_hours,
        avg_satisfaction=metrics.avg_satisfaction,
        tickets_by_status=metrics.tickets_by_status,
        tickets_by_priority=metrics.tickets_by_priority,
    )


# ─── Canned Responses ─────────────────────────────────────────────────────────


@router.get("/canned-responses", dependencies=[Depends(require_role("admin"))])
async def list_canned_responses(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List all canned responses."""
    responses = await service.list_canned_responses(session)
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "body": r.body,
            "category": r.category,
            "shortcut": r.shortcut,
        }
        for r in responses
    ]


@router.post("/canned-responses", dependencies=[Depends(require_role("admin"))], status_code=201)
async def create_canned_response(
    body: CannedResponseCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a canned response template."""
    cr = await service.create_canned_response(
        session,
        author_id=user.user_id,
        title=body.title,
        body=body.body,
        category=body.category,
        shortcut=body.shortcut,
    )
    return {"id": str(cr.id), "title": cr.title}


@router.delete(
    "/canned-responses/{response_id}",
    dependencies=[Depends(require_role("admin"))],
    status_code=204,
)
async def delete_canned_response(
    response_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a canned response."""
    cr = await service.get_canned_response(session, response_id)
    if cr is None:
        raise HTTPException(status_code=404, detail="Canned response not found")
    await service.delete_canned_response(session, cr)


# ─── Channel Configuration ────────────────────────────────────────────────────


@router.get("/channels", dependencies=[Depends(require_platform_admin)])
async def list_channels(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List all support channels and their config."""
    channels = await service.list_support_channels(session)
    return [
        {
            "id": str(c.id),
            "channel_type": c.channel_type,
            "is_enabled": c.is_enabled,
            "min_plan": c.min_plan,
            "config_json": c.config_json,
        }
        for c in channels
    ]


@router.patch("/channels/{channel_id}", dependencies=[Depends(require_platform_admin)])
async def update_channel(
    channel_id: UUID,
    body: ChannelUpdateRequest,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Enable/disable a support channel or update its config."""
    channel = await service.get_support_channel(session, channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    await service.update_support_channel(
        session,
        channel,
        is_enabled=body.is_enabled,
        min_plan=body.min_plan,
        config_json=body.config_json,
    )
    return {"status": "updated"}
