"""Admin support dashboard — ticket management, SLA tracking, metrics."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import CurrentUser, get_current_user, require_platform_admin, require_role
from app.database import async_session_factory
from app.support.models import (
    CannedResponse,
    SupportChannel,
    SupportTicket,
    TicketMessage,
    TicketStatus,
)

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
    query = select(SupportTicket)

    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    if assigned_to:
        query = query.where(SupportTicket.assigned_to_id == assigned_to)
    if category:
        query = query.where(SupportTicket.category == category)
    if overdue:
        query = query.where(
            SupportTicket.due_at < datetime.now(UTC),
            SupportTicket.status.in_([TicketStatus.open, TicketStatus.in_progress, TicketStatus.waiting_on_staff]),
        )

    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

    tickets = (
        (
            await session.execute(
                query.order_by(SupportTicket.updated_at.desc()).offset((page - 1) * per_page).limit(per_page)
            )
        )
        .scalars()
        .all()
    )

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
                "is_overdue": t.due_at < datetime.now(UTC) if t.due_at else False,
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
    ticket = (
        await session.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id).options(selectinload(SupportTicket.messages))
        )
    ).scalar_one_or_none()

    if not ticket:
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
    ticket = await session.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if body.status:
        ticket.status = body.status
        if body.status in (TicketStatus.resolved, TicketStatus.closed):
            ticket.resolved_at = datetime.now(UTC)

    if body.priority:
        ticket.priority = body.priority

    if body.assigned_to_id is not None:
        ticket.assigned_to_id = body.assigned_to_id
        if ticket.status == TicketStatus.open:
            ticket.status = TicketStatus.in_progress

    if body.tags is not None:
        ticket.tags = body.tags

    await session.commit()
    return {"status": "updated"}


@router.post("/tickets/{ticket_id}/messages", dependencies=[Depends(require_role("admin"))])
async def add_admin_message(
    ticket_id: UUID,
    body: AdminMessageRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Add a message (reply or internal note) to a ticket."""
    ticket = await session.get(SupportTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=user.user_id,
        body=body.body,
        is_internal=body.is_internal,
        attachments=body.attachments or [],
    )
    session.add(message)

    # Track first response time
    if not body.is_internal and not ticket.first_response_at:
        ticket.first_response_at = datetime.now(UTC)

    # Update status to waiting on user (unless internal note)
    if not body.is_internal and ticket.status != TicketStatus.resolved:
        ticket.status = TicketStatus.waiting_on_user

    await session.commit()
    await session.refresh(message)
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
    tickets = (
        (await session.execute(select(SupportTicket).where(SupportTicket.id.in_(body.ticket_ids)))).scalars().all()
    )

    count = 0
    for ticket in tickets:
        if body.action == "close":
            ticket.status = TicketStatus.closed
            ticket.resolved_at = datetime.now(UTC)
        elif body.action == "assign" and body.value:
            ticket.assigned_to_id = UUID(body.value)
        elif body.action == "change_priority" and body.value:
            ticket.priority = body.value
        elif body.action == "change_status" and body.value:
            ticket.status = body.value
        count += 1

    await session.commit()
    return {"updated": count}


# ─── Metrics ──────────────────────────────────────────────────────────────────


@router.get("/metrics", dependencies=[Depends(require_role("admin"))])
async def ticket_metrics(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> TicketMetricsResponse:
    """Get support ticket metrics and KPIs."""
    now = datetime.now(UTC)

    # Total tickets
    total = (await session.execute(select(func.count(SupportTicket.id)))).scalar() or 0

    # Open tickets
    open_count = (
        await session.execute(
            select(func.count(SupportTicket.id)).where(
                SupportTicket.status.in_([TicketStatus.open, TicketStatus.in_progress, TicketStatus.waiting_on_staff])
            )
        )
    ).scalar() or 0

    # Overdue
    overdue_count = (
        await session.execute(
            select(func.count(SupportTicket.id)).where(
                SupportTicket.due_at < now,
                SupportTicket.status.in_([TicketStatus.open, TicketStatus.in_progress, TicketStatus.waiting_on_staff]),
            )
        )
    ).scalar() or 0

    # Avg satisfaction
    avg_sat = (
        await session.execute(
            select(func.avg(SupportTicket.satisfaction_rating)).where(SupportTicket.satisfaction_rating.isnot(None))
        )
    ).scalar()

    # By status
    status_counts = (
        await session.execute(select(SupportTicket.status, func.count(SupportTicket.id)).group_by(SupportTicket.status))
    ).all()

    # By priority
    priority_counts = (
        await session.execute(
            select(SupportTicket.priority, func.count(SupportTicket.id)).group_by(SupportTicket.priority)
        )
    ).all()

    # Avg first response time (hours)
    avg_first_response = (
        await session.execute(
            select(
                func.avg(func.extract("epoch", SupportTicket.first_response_at - SupportTicket.created_at) / 3600)
            ).where(SupportTicket.first_response_at.isnot(None))
        )
    ).scalar()

    # Avg resolution time (hours)
    avg_resolution = (
        await session.execute(
            select(func.avg(func.extract("epoch", SupportTicket.resolved_at - SupportTicket.created_at) / 3600)).where(
                SupportTicket.resolved_at.isnot(None)
            )
        )
    ).scalar()

    return TicketMetricsResponse(
        total_tickets=total,
        open_tickets=open_count,
        overdue_tickets=overdue_count,
        avg_first_response_hours=round(float(avg_first_response), 1) if avg_first_response else None,
        avg_resolution_hours=round(float(avg_resolution), 1) if avg_resolution else None,
        avg_satisfaction=float(avg_sat) if avg_sat else None,
        tickets_by_status={row[0]: row[1] for row in status_counts},
        tickets_by_priority={row[0]: row[1] for row in priority_counts},
    )


# ─── Canned Responses ─────────────────────────────────────────────────────────


@router.get("/canned-responses", dependencies=[Depends(require_role("admin"))])
async def list_canned_responses(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List all canned responses."""
    responses = (await session.execute(select(CannedResponse))).scalars().all()
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
    cr = CannedResponse(
        title=body.title,
        body=body.body,
        category=body.category,
        shortcut=body.shortcut,
        created_by_id=user.user_id,
    )
    session.add(cr)
    await session.commit()
    await session.refresh(cr)
    return {"id": str(cr.id), "title": cr.title}


@router.delete("/canned-responses/{response_id}", dependencies=[Depends(require_role("admin"))], status_code=204)
async def delete_canned_response(
    response_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a canned response."""
    cr = await session.get(CannedResponse, response_id)
    if not cr:
        raise HTTPException(status_code=404, detail="Canned response not found")
    await session.delete(cr)
    await session.commit()


# ─── Channel Configuration ────────────────────────────────────────────────────


@router.get("/channels", dependencies=[Depends(require_platform_admin)])
async def list_channels(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List all support channels and their config."""
    channels = (await session.execute(select(SupportChannel))).scalars().all()
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
    channel = await session.get(SupportChannel, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    if body.is_enabled is not None:
        channel.is_enabled = body.is_enabled
    if body.min_plan is not None:
        channel.min_plan = body.min_plan
    if body.config_json is not None:
        channel.config_json = body.config_json

    await session.commit()
    return {"status": "updated"}
