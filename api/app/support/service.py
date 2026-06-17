"""Support — tickets domain service.

Holds the business operations for user-facing support tickets:
creation (with SLA due-time computation), listing, retrieval (with
internal-note filtering), follow-up messages, close, and satisfaction
rating.

Route handlers in ``app.support.routes`` are HTTP-only and delegate
to this module.

Conventions match the project standard (PR #192 / #208 / #209 / #210 /
#211):

* The first positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances or plain primitives; they never
  raise ``HTTPException`` — lookup misses return ``None`` and domain
  validation failures raise typed errors.

NOTE: When the support module's other route files (``kb_routes``,
``forum_routes``, ``admin_routes``) are migrated in follow-up PRs they
will add ``kb_*``, ``forum_*``, and ``admin_*`` helpers to this same
module so the entire ``app/support`` package has a single service
surface — matching the convention established for ``app/sensors``.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.support.models import (
    SupportTicket,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketStatus,
)

# ─────────────────────────────────────────────────────────────────────────────
# SLA / enums
# ─────────────────────────────────────────────────────────────────────────────

# Hours-to-first-response by ticket priority. Kept here (single source of
# truth) so engine, route, and admin views all read from the same table.
SLA_HOURS: dict[TicketPriority, int] = {
    TicketPriority.urgent: 1,
    TicketPriority.high: 4,
    TicketPriority.medium: 24,
    TicketPriority.low: 72,
}


def coerce_category(value: str) -> TicketCategory:
    """Map a user-supplied category string to the enum, falling back to
    ``general`` for unknown values. Matches previous route behaviour."""
    try:
        return TicketCategory(value)
    except ValueError:
        return TicketCategory.general


def coerce_priority(value: str) -> TicketPriority:
    """Map a user-supplied priority string to the enum, falling back to
    ``medium`` for unknown values. Matches previous route behaviour."""
    try:
        return TicketPriority(value)
    except ValueError:
        return TicketPriority.medium


def compute_sla_due(priority: TicketPriority, *, now: datetime | None = None) -> datetime:
    """Compute the SLA due-time for a ticket of ``priority``.

    Pure function so route and engine code can compute identical
    deadlines without touching the database.
    """
    hours = SLA_HOURS.get(priority, 24)
    base = now if now is not None else datetime.now(UTC)
    return base + timedelta(hours=hours)


# ─────────────────────────────────────────────────────────────────────────────
# Ticket CRUD
# ─────────────────────────────────────────────────────────────────────────────


async def create_ticket(
    session: AsyncSession,
    *,
    tenant_id: UUID | None,
    author_id: UUID,
    subject: str,
    body: str,
    category: TicketCategory,
    priority: TicketPriority,
    attachments: list[dict] | None,
) -> SupportTicket:
    """Persist a new ticket plus its initial message in one transaction."""
    ticket = SupportTicket(
        tenant_id=tenant_id,
        created_by_id=author_id,
        subject=subject,
        status=TicketStatus.open,
        priority=priority,
        category=category,
        due_at=compute_sla_due(priority),
    )
    session.add(ticket)
    await session.flush()

    session.add(
        TicketMessage(
            ticket_id=ticket.id,
            author_id=author_id,
            body=body,
            attachments=attachments or [],
        )
    )
    await session.commit()
    await session.refresh(ticket)
    return ticket


async def list_my_tickets_page(
    session: AsyncSession,
    *,
    author_id: UUID,
    status: str | None,
    page: int,
    per_page: int,
) -> tuple[list[SupportTicket], int]:
    """Return ``(tickets, total)`` for a user's own tickets."""
    query = select(SupportTicket).where(SupportTicket.created_by_id == author_id)
    if status:
        query = query.where(SupportTicket.status == status)

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
    return list(tickets), int(total)


async def get_user_ticket_with_messages(
    session: AsyncSession,
    *,
    ticket_id: UUID,
    author_id: UUID,
) -> SupportTicket | None:
    """Fetch the user's own ticket with ``messages`` eagerly loaded.

    Returns ``None`` for not-found / not-owned; route maps to 404. The
    internal-note filter belongs in the route layer (response shaping).
    """
    return (
        await session.execute(
            select(SupportTicket)
            .where(
                SupportTicket.id == ticket_id,
                SupportTicket.created_by_id == author_id,
            )
            .options(selectinload(SupportTicket.messages))
        )
    ).scalar_one_or_none()


async def get_user_ticket(
    session: AsyncSession,
    *,
    ticket_id: UUID,
    author_id: UUID,
) -> SupportTicket | None:
    """Fetch the user's own ticket without messages."""
    return (
        await session.execute(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id,
                SupportTicket.created_by_id == author_id,
            )
        )
    ).scalar_one_or_none()


# ─────────────────────────────────────────────────────────────────────────────
# Ticket actions
# ─────────────────────────────────────────────────────────────────────────────


def is_ticket_closed(ticket: SupportTicket) -> bool:
    """True for ``closed`` / ``resolved`` tickets; new messages are rejected."""
    return ticket.status in (TicketStatus.closed, TicketStatus.resolved)


async def add_user_message(
    session: AsyncSession,
    ticket: SupportTicket,
    *,
    author_id: UUID,
    body: str,
    attachments: list[dict] | None,
) -> TicketMessage:
    """Add a user message to ``ticket`` and bump the status when the
    ticket was previously ``waiting_on_user``."""
    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=author_id,
        body=body,
        attachments=attachments or [],
    )
    session.add(message)

    if ticket.status == TicketStatus.waiting_on_user:
        ticket.status = TicketStatus.waiting_on_staff

    await session.commit()
    await session.refresh(message)
    return message


async def close_ticket(session: AsyncSession, ticket: SupportTicket) -> SupportTicket:
    """Mark ``ticket`` closed and stamp ``resolved_at``."""
    ticket.status = TicketStatus.closed
    ticket.resolved_at = datetime.now(UTC)
    await session.commit()
    return ticket


async def get_rateable_ticket(
    session: AsyncSession,
    *,
    ticket_id: UUID,
    author_id: UUID,
) -> SupportTicket | None:
    """Fetch the user's ticket only if it is ``resolved`` or ``closed``.

    Route maps ``None`` to 404 with a "not resolved" detail.
    """
    return (
        await session.execute(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id,
                SupportTicket.created_by_id == author_id,
                SupportTicket.status.in_([TicketStatus.resolved, TicketStatus.closed]),
            )
        )
    ).scalar_one_or_none()


async def rate_ticket(
    session: AsyncSession,
    ticket: SupportTicket,
    *,
    rating: int,
    comment: str | None,
) -> SupportTicket:
    """Record a satisfaction rating + optional comment on a resolved ticket."""
    ticket.satisfaction_rating = rating
    ticket.satisfaction_comment = comment
    await session.commit()
    return ticket
