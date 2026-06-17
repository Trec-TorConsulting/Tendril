"""User-facing support ticket endpoints.

This module is HTTP-only. All persistence, SLA computation, status
transitions, and rating-window validation live in
``app.support.service``.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.support import service

router = APIRouter()
logger = logging.getLogger("tendril.support.tickets")


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

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    id: UUID
    author_id: UUID
    body: str
    is_internal: bool
    attachments: list | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.post("/", status_code=201)
async def create_ticket(
    body: CreateTicketRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
) -> TicketSummary:
    """Create a new support ticket."""
    ticket = await service.create_ticket(
        session,
        tenant_id=user.tenant_id,
        author_id=user.user_id,
        subject=body.subject,
        body=body.body,
        category=service.coerce_category(body.category),
        priority=service.coerce_priority(body.priority),
        attachments=body.attachments,
    )
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
    tickets, total = await service.list_my_tickets_page(
        session,
        author_id=user.user_id,
        status=status,
        page=page,
        per_page=per_page,
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
    ticket = await service.get_user_ticket_with_messages(session, ticket_id=ticket_id, author_id=user.user_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Filter out internal notes for regular users (response shaping)
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
    ticket = await service.get_user_ticket(session, ticket_id=ticket_id, author_id=user.user_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if service.is_ticket_closed(ticket):
        raise HTTPException(status_code=400, detail="Ticket is closed")

    message = await service.add_user_message(
        session,
        ticket,
        author_id=user.user_id,
        body=body.body,
        attachments=body.attachments,
    )
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
    ticket = await service.get_user_ticket(session, ticket_id=ticket_id, author_id=user.user_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await service.close_ticket(session, ticket)
    return {"status": "closed"}


@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: UUID,
    body: RateTicketRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Rate a resolved/closed ticket."""
    ticket = await service.get_rateable_ticket(session, ticket_id=ticket_id, author_id=user.user_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found or not resolved")
    await service.rate_ticket(session, ticket, rating=body.rating, comment=body.comment)
    return {"rating": body.rating}
