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

from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.models import Conversation, ConversationMessage

# ─────────────────────────────────────────────────────────────────────────────
# Conversations
# ─────────────────────────────────────────────────────────────────────────────


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
    "Conversation",
    "ConversationMessage",
    "create_conversation",
    "delete_conversation",
    "get_conversation",
    "get_conversation_with_messages",
    "list_user_conversations_query",
    "parse_optional_uuid",
    "update_conversation_title",
]
