"""User-facing support ticket endpoints."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.support.models import (
    SupportTicket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

router = APIRouter()
logger = logging.getLogger("tendril.support.tickets")


# SLA defaults (hours to first response by priority)
SLA_HOURS = {
    TicketPriority.urgent: 1,
    TicketPriority.high: 4,
    TicketPriority.medium: 24,
    TicketPriority.low: 72,
}


# ─── Schemas ──────────────────────────────────────────────────────────────────


class CreateTicketRequest(BaseModel):
    subject: str = Field(min_length=5, max_length=255)
    body: str = Field(min_length=10)
    category: str = "general"
    priority: str = "medium"
    attachments: list[dict] | None = None


class AddMessageRequest(BaseModel):
    body: str = Field(min_length=1)
    attachments: list[dict] | None = None


class RateTicketRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class TicketSummary(BaseModel):
    id: UUID
    subject: str
    status: str
    priority: str
    category: str
    created_at: datetime
    updated_at: datetime
    message_count: int | None = None

    class Config:
        from_attributes = True


class TicketDetail(BaseModel):
    id: UUID
    subject: str
    status: str
    priority: str
    category: str
    due_at: datetime | None
    first_response_at: datetime | None
    resolved_at: datetime | None
    satisfaction_rating: int | None
    tags: list | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse]

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    author_id: UUID
    body: str
    is_internal: bool
    attachments: list | None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def create_ticket(
    body: CreateTicketRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
) -> TicketSummary:
    """Create a new support ticket."""
    # Validate enums
    try:
        cat = TicketCategory(body.category)
    except ValueError:
        cat = TicketCategory.general

    try:
        pri = TicketPriority(body.priority)
    except ValueError:
        pri = TicketPriority.medium

    # Calculate SLA due time
    sla_hours = SLA_HOURS.get(pri, 24)
    due_at = datetime.now(UTC) + timedelta(hours=sla_hours)

    ticket = SupportTicket(
        tenant_id=user.tenant_id,
        created_by_id=user.user_id,
        subject=body.subject,
        status=TicketStatus.open,
        priority=pri,
        category=cat,
        due_at=due_at,
    )
    session.add(ticket)
    await session.flush()

    # Add initial message
    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=user.user_id,
        body=body.body,
        attachments=body.attachments or [],
    )
    session.add(message)
    await session.commit()
    await session.refresh(ticket)

    return TicketSummary(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        priority=ticket.priority,
        category=ticket.category,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        message_count=1,
    )


@router.get("")
async def list_my_tickets(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List the current user's support tickets."""
    query = select(SupportTicket).where(SupportTicket.created_by_id == user.user_id)

    if status:
        query = query.where(SupportTicket.status == status)

    # Count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_q)).scalar() or 0

    # Paginate
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
            TicketSummary(
                id=t.id,
                subject=t.subject,
                status=t.status,
                priority=t.priority,
                category=t.category,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tickets
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
) -> TicketDetail:
    """Get a specific ticket with all messages."""
    ticket = (
        await session.execute(
            select(SupportTicket)
            .where(SupportTicket.id == ticket_id, SupportTicket.created_by_id == user.user_id)
            .options(selectinload(SupportTicket.messages))
        )
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Filter out internal notes for regular users
    messages = [
        MessageResponse(
            id=m.id,
            author_id=m.author_id,
            body=m.body,
            is_internal=m.is_internal,
            attachments=m.attachments,
            created_at=m.created_at,
        )
        for m in ticket.messages
        if not m.is_internal
    ]

    return TicketDetail(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        priority=ticket.priority,
        category=ticket.category,
        due_at=ticket.due_at,
        first_response_at=ticket.first_response_at,
        resolved_at=ticket.resolved_at,
        satisfaction_rating=ticket.satisfaction_rating,
        tags=ticket.tags,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        messages=messages,
    )


@router.post("/{ticket_id}/messages", status_code=201)
async def add_message(
    ticket_id: UUID,
    body: AddMessageRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
) -> MessageResponse:
    """Add a message to an existing ticket."""
    ticket = (
        await session.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id, SupportTicket.created_by_id == user.user_id)
        )
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.status in (TicketStatus.closed, TicketStatus.resolved):
        raise HTTPException(status_code=400, detail="Ticket is closed")

    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=user.user_id,
        body=body.body,
        attachments=body.attachments or [],
    )
    session.add(message)

    # Update ticket status if it was waiting on user
    if ticket.status == TicketStatus.waiting_on_user:
        ticket.status = TicketStatus.waiting_on_staff

    await session.commit()
    await session.refresh(message)

    return MessageResponse(
        id=message.id,
        author_id=message.author_id,
        body=message.body,
        is_internal=message.is_internal,
        attachments=message.attachments,
        created_at=message.created_at,
    )


@router.post("/{ticket_id}/close")
async def close_ticket(
    ticket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Close a ticket (user action)."""
    ticket = (
        await session.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id, SupportTicket.created_by_id == user.user_id)
        )
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = TicketStatus.closed
    ticket.resolved_at = datetime.now(UTC)
    await session.commit()
    return {"status": "closed"}


@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: UUID,
    body: RateTicketRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Rate a resolved/closed ticket."""
    ticket = (
        await session.execute(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id,
                SupportTicket.created_by_id == user.user_id,
                SupportTicket.status.in_([TicketStatus.resolved, TicketStatus.closed]),
            )
        )
    ).scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not resolved")

    ticket.satisfaction_rating = body.rating
    ticket.satisfaction_comment = body.comment
    await session.commit()
    return {"rating": body.rating}
