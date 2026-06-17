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

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.support.models import (
    CannedResponse,
    ForumCategory,
    ForumPost,
    ForumThread,
    ForumThreadStatus,
    KBArticle,
    KBCategory,
    SupportChannel,
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


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Base — categories + articles
# ─────────────────────────────────────────────────────────────────────────────


_SLUG_NON_WORD_RE = re.compile(r"[^\w\s-]")
_SLUG_SEP_RE = re.compile(r"[\s_]+")
_SLUG_DUP_DASH_RE = re.compile(r"-+")


def slugify(text: str) -> str:
    """Generate a URL-safe slug from ``text``.

    Lowercases, strips diacritics-less punctuation, collapses runs of
    whitespace/underscores into hyphens, and dedupes hyphen runs. Matches
    the previous private ``_slugify`` in ``kb_routes`` byte-for-byte so
    existing slugs remain stable.
    """
    slug = text.lower().strip()
    slug = _SLUG_NON_WORD_RE.sub("", slug)
    slug = _SLUG_SEP_RE.sub("-", slug)
    return _SLUG_DUP_DASH_RE.sub("-", slug).strip("-")


@dataclass(frozen=True, slots=True)
class KBCategoryWithCount:
    """A KB category joined with its published-article count."""

    category: KBCategory
    article_count: int


async def list_kb_categories_with_counts(
    session: AsyncSession,
) -> list[KBCategoryWithCount]:
    """Return all published KB categories with their published-article counts."""
    categories = (
        (
            await session.execute(
                select(KBCategory).where(KBCategory.is_published.is_(True)).order_by(KBCategory.sort_order)
            )
        )
        .scalars()
        .all()
    )

    out: list[KBCategoryWithCount] = []
    for cat in categories:
        count = (
            await session.execute(
                select(func.count(KBArticle.id)).where(
                    KBArticle.category_id == cat.id,
                    KBArticle.is_published.is_(True),
                )
            )
        ).scalar() or 0
        out.append(KBCategoryWithCount(category=cat, article_count=int(count)))
    return out


async def get_kb_category_by_slug(session: AsyncSession, slug: str) -> KBCategory | None:
    return (await session.execute(select(KBCategory).where(KBCategory.slug == slug))).scalar_one_or_none()


async def list_kb_articles_page(
    session: AsyncSession,
    *,
    category_slug: str | None,
    page: int,
    per_page: int,
) -> tuple[list[KBArticle], int]:
    """Return ``(articles, total)`` for the published-articles listing."""
    query = select(KBArticle).where(KBArticle.is_published.is_(True))
    if category_slug:
        cat = await get_kb_category_by_slug(session, category_slug)
        if cat is not None:
            query = query.where(KBArticle.category_id == cat.id)

    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

    articles = (
        (await session.execute(query.order_by(KBArticle.sort_order).offset((page - 1) * per_page).limit(per_page)))
        .scalars()
        .all()
    )
    return list(articles), int(total)


async def search_kb_articles(session: AsyncSession, query_text: str, *, limit: int = 20) -> list[KBArticle]:
    """Simple ILIKE search across published KB title + body. Capped at ``limit``."""
    pattern = f"%{query_text}%"
    result = await session.execute(
        select(KBArticle)
        .where(
            KBArticle.is_published.is_(True),
            or_(
                KBArticle.title.ilike(pattern),
                KBArticle.body_markdown.ilike(pattern),
            ),
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_published_kb_article_by_slug(session: AsyncSession, slug: str) -> KBArticle | None:
    """Fetch a *published* article by slug; unpublished drafts return ``None``."""
    return (
        await session.execute(select(KBArticle).where(KBArticle.slug == slug, KBArticle.is_published.is_(True)))
    ).scalar_one_or_none()


async def get_kb_article_by_slug(session: AsyncSession, slug: str) -> KBArticle | None:
    """Fetch any article by slug (published or not). Used by the vote endpoint."""
    return (await session.execute(select(KBArticle).where(KBArticle.slug == slug))).scalar_one_or_none()


async def increment_kb_article_views(session: AsyncSession, article: KBArticle) -> KBArticle:
    """Bump the article's view counter and commit."""
    article.views += 1
    await session.commit()
    return article


async def vote_kb_article(session: AsyncSession, article: KBArticle, *, helpful: bool) -> KBArticle:
    """Record a helpful/not-helpful vote on an article."""
    if helpful:
        article.helpful_yes += 1
    else:
        article.helpful_no += 1
    await session.commit()
    return article


async def create_kb_category(
    session: AsyncSession,
    *,
    name: str,
    slug: str | None,
    description: str | None,
    icon: str | None,
    sort_order: int,
) -> KBCategory:
    """Create a KB category, generating a slug from ``name`` when absent."""
    cat = KBCategory(
        name=name,
        slug=slug or slugify(name),
        description=description,
        icon=icon,
        sort_order=sort_order,
    )
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return cat


async def get_kb_category(session: AsyncSession, category_id: UUID) -> KBCategory | None:
    return await session.get(KBCategory, category_id)


async def delete_kb_category(session: AsyncSession, cat: KBCategory) -> None:
    await session.delete(cat)
    await session.commit()


async def create_kb_article(
    session: AsyncSession,
    *,
    category_id: UUID,
    author_id: UUID,
    title: str,
    slug: str | None,
    body_markdown: str,
    tags: list[str] | None,
    is_published: bool,
    sort_order: int,
) -> KBArticle:
    """Create a KB article, generating a slug from ``title`` when absent."""
    article = KBArticle(
        category_id=category_id,
        title=title,
        slug=slug or slugify(title),
        body_markdown=body_markdown,
        tags=tags or [],
        is_published=is_published,
        sort_order=sort_order,
        author_id=author_id,
    )
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


async def get_kb_article(session: AsyncSession, article_id: UUID) -> KBArticle | None:
    return await session.get(KBArticle, article_id)


async def update_kb_article(
    session: AsyncSession,
    article: KBArticle,
    *,
    title: str | None = None,
    body_markdown: str | None = None,
    tags: list[str] | None = None,
    is_published: bool | None = None,
    sort_order: int | None = None,
    category_id: UUID | None = None,
) -> KBArticle:
    """Apply partial updates to a KB article and commit."""
    if title is not None:
        article.title = title
    if body_markdown is not None:
        article.body_markdown = body_markdown
    if tags is not None:
        article.tags = tags
    if is_published is not None:
        article.is_published = is_published
    if sort_order is not None:
        article.sort_order = sort_order
    if category_id is not None:
        article.category_id = category_id
    await session.commit()
    return article


async def delete_kb_article(session: AsyncSession, article: KBArticle) -> None:
    await session.delete(article)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Forum — categories, threads, posts, moderation
# ─────────────────────────────────────────────────────────────────────────────


async def list_forum_categories(session: AsyncSession) -> list[ForumCategory]:
    """All forum categories ordered by ``sort_order``."""
    return list((await session.execute(select(ForumCategory).order_by(ForumCategory.sort_order))).scalars().all())


async def get_forum_category(session: AsyncSession, category_id: UUID) -> ForumCategory | None:
    return await session.get(ForumCategory, category_id)


async def get_forum_category_by_slug(session: AsyncSession, slug: str) -> ForumCategory | None:
    return (await session.execute(select(ForumCategory).where(ForumCategory.slug == slug))).scalar_one_or_none()


async def list_forum_threads_page(
    session: AsyncSession,
    *,
    category_slug: str | None,
    page: int,
    per_page: int,
) -> tuple[list[ForumThread], int]:
    """Paginated thread listing, optionally filtered by category. Pinned first."""
    query = select(ForumThread)
    if category_slug:
        cat = await get_forum_category_by_slug(session, category_slug)
        if cat is not None:
            query = query.where(ForumThread.category_id == cat.id)

    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

    threads = (
        (
            await session.execute(
                query.order_by(
                    ForumThread.is_pinned.desc(),
                    ForumThread.last_activity_at.desc(),
                )
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )
    return list(threads), int(total)


async def get_forum_thread_with_posts(session: AsyncSession, thread_id: UUID) -> ForumThread | None:
    """Fetch a thread with its ``posts`` eagerly loaded."""
    return (
        await session.execute(
            select(ForumThread).where(ForumThread.id == thread_id).options(selectinload(ForumThread.posts))
        )
    ).scalar_one_or_none()


async def get_forum_thread(session: AsyncSession, thread_id: UUID) -> ForumThread | None:
    return await session.get(ForumThread, thread_id)


async def get_forum_post(session: AsyncSession, post_id: UUID) -> ForumPost | None:
    return await session.get(ForumPost, post_id)


async def increment_forum_thread_views(session: AsyncSession, thread: ForumThread) -> ForumThread:
    thread.view_count += 1
    await session.commit()
    return thread


async def create_forum_thread(
    session: AsyncSession,
    *,
    category: ForumCategory,
    author_id: UUID,
    title: str,
    body: str,
) -> ForumThread:
    """Create a thread and bump the category's thread count."""
    thread = ForumThread(
        category_id=category.id,
        author_id=author_id,
        title=title,
        body=body,
    )
    session.add(thread)
    category.thread_count += 1
    await session.commit()
    await session.refresh(thread)
    return thread


def is_forum_thread_locked(thread: ForumThread) -> bool:
    """True when the thread is locked; route maps to 403."""
    return thread.status == ForumThreadStatus.locked


async def create_forum_post(
    session: AsyncSession,
    thread: ForumThread,
    *,
    author_id: UUID,
    body: str,
) -> ForumPost:
    """Create a reply, bump thread reply count + last activity, bump category post count."""
    post = ForumPost(
        thread_id=thread.id,
        author_id=author_id,
        body=body,
    )
    session.add(post)

    thread.reply_count += 1
    thread.last_activity_at = datetime.now(UTC)

    category = await session.get(ForumCategory, thread.category_id)
    if category is not None:
        category.post_count += 1

    await session.commit()
    await session.refresh(post)
    return post


async def upvote_forum_thread(session: AsyncSession, thread: ForumThread) -> ForumThread:
    thread.upvotes += 1
    await session.commit()
    return thread


async def upvote_forum_post(session: AsyncSession, post: ForumPost) -> ForumPost:
    post.upvotes += 1
    await session.commit()
    return post


async def mark_forum_solution(
    session: AsyncSession,
    thread: ForumThread,
    post: ForumPost,
) -> ForumThread:
    """Mark ``post`` as the solution for ``thread``.

    Caller must verify that ``post.thread_id == thread.id`` (route does this
    so it can return a precise 404 on mismatch).
    """
    if thread.solution_post_id is not None:
        old_post = await session.get(ForumPost, thread.solution_post_id)
        if old_post is not None:
            old_post.is_solution = False

    thread.solution_post_id = post.id
    thread.status = ForumThreadStatus.solved
    post.is_solution = True

    await session.commit()
    return thread


async def toggle_forum_pin(session: AsyncSession, thread: ForumThread) -> ForumThread:
    thread.is_pinned = not thread.is_pinned
    await session.commit()
    return thread


async def toggle_forum_lock(session: AsyncSession, thread: ForumThread) -> ForumThread:
    """Flip between ``open`` and ``locked``."""
    if thread.status == ForumThreadStatus.locked:
        thread.status = ForumThreadStatus.open
    else:
        thread.status = ForumThreadStatus.locked
    await session.commit()
    return thread


async def delete_forum_thread(session: AsyncSession, thread: ForumThread) -> None:
    await session.delete(thread)
    await session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Admin — ticket management, metrics, canned responses, channels
# ─────────────────────────────────────────────────────────────────────────────


# Statuses that represent an open / actionable ticket. Used by both the
# "list overdue" filter and the open-tickets KPI in metrics so they stay
# consistent.
OPEN_TICKET_STATUSES: tuple[TicketStatus, ...] = (
    TicketStatus.open,
    TicketStatus.in_progress,
    TicketStatus.waiting_on_staff,
)


async def list_admin_tickets_page(
    session: AsyncSession,
    *,
    status: str | None,
    priority: str | None,
    assigned_to: UUID | None,
    category: str | None,
    overdue: bool | None,
    page: int,
    per_page: int,
    now: datetime | None = None,
) -> tuple[list[SupportTicket], int]:
    """Paginated admin ticket listing with the standard filters.

    ``now`` is injectable so callers (and tests) can pin the time used
    in the ``overdue`` cutoff. Defaults to ``datetime.now(UTC)``.
    """
    query = select(SupportTicket)
    if status:
        query = query.where(SupportTicket.status == status)
    if priority:
        query = query.where(SupportTicket.priority == priority)
    if assigned_to is not None:
        query = query.where(SupportTicket.assigned_to_id == assigned_to)
    if category:
        query = query.where(SupportTicket.category == category)
    if overdue:
        cutoff = now if now is not None else datetime.now(UTC)
        query = query.where(
            SupportTicket.due_at < cutoff,
            SupportTicket.status.in_(OPEN_TICKET_STATUSES),
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
    return list(tickets), int(total)


async def get_admin_ticket(session: AsyncSession, ticket_id: UUID) -> SupportTicket | None:
    return await session.get(SupportTicket, ticket_id)


async def get_admin_ticket_with_messages(session: AsyncSession, ticket_id: UUID) -> SupportTicket | None:
    """Admin view — includes internal notes (route does not filter)."""
    return (
        await session.execute(
            select(SupportTicket).where(SupportTicket.id == ticket_id).options(selectinload(SupportTicket.messages))
        )
    ).scalar_one_or_none()


async def update_admin_ticket(
    session: AsyncSession,
    ticket: SupportTicket,
    *,
    status: str | None = None,
    priority: str | None = None,
    assigned_to_id: UUID | None = None,
    tags: list[str] | None = None,
) -> SupportTicket:
    """Apply partial updates with the documented status-side-effects:

    * Setting status → resolved/closed stamps ``resolved_at``.
    * Setting assignee on an ``open`` ticket transitions to ``in_progress``.
    """
    if status:
        ticket.status = status  # type: ignore[assignment]
        if status in (TicketStatus.resolved.value, TicketStatus.closed.value):
            ticket.resolved_at = datetime.now(UTC)
    if priority:
        ticket.priority = priority  # type: ignore[assignment]
    if assigned_to_id is not None:
        ticket.assigned_to_id = assigned_to_id
        if ticket.status == TicketStatus.open:
            ticket.status = TicketStatus.in_progress
    if tags is not None:
        ticket.tags = tags
    await session.commit()
    return ticket


async def add_admin_message(
    session: AsyncSession,
    ticket: SupportTicket,
    *,
    author_id: UUID,
    body: str,
    is_internal: bool,
    attachments: list[dict] | None,
) -> TicketMessage:
    """Add an admin message + apply the documented side effects:

    * Public reply stamps ``first_response_at`` if it wasn't set.
    * Public reply transitions the ticket to ``waiting_on_user`` (unless
      already ``resolved``).
    * Internal notes don't change ticket state.
    """
    message = TicketMessage(
        ticket_id=ticket.id,
        author_id=author_id,
        body=body,
        is_internal=is_internal,
        attachments=attachments or [],
    )
    session.add(message)

    if not is_internal:
        if ticket.first_response_at is None:
            ticket.first_response_at = datetime.now(UTC)
        if ticket.status != TicketStatus.resolved:
            ticket.status = TicketStatus.waiting_on_user

    await session.commit()
    await session.refresh(message)
    return message


async def bulk_update_tickets(
    session: AsyncSession,
    *,
    ticket_ids: list[UUID],
    action: str,
    value: str | None,
) -> int:
    """Apply ``action`` to all listed tickets and return the count updated.

    Supported actions: ``close``, ``assign`` (value=user UUID),
    ``change_priority`` (value=priority), ``change_status`` (value=status).
    Unknown actions are no-ops (matching previous behaviour).
    """
    tickets = (await session.execute(select(SupportTicket).where(SupportTicket.id.in_(ticket_ids)))).scalars().all()

    count = 0
    for ticket in tickets:
        if action == "close":
            ticket.status = TicketStatus.closed
            ticket.resolved_at = datetime.now(UTC)
        elif action == "assign" and value:
            ticket.assigned_to_id = UUID(value)
        elif action == "change_priority" and value:
            ticket.priority = value  # type: ignore[assignment]
        elif action == "change_status" and value:
            ticket.status = value  # type: ignore[assignment]
        count += 1

    await session.commit()
    return count


# ─── Metrics ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TicketMetrics:
    """Aggregated KPI snapshot for the admin metrics endpoint."""

    total_tickets: int
    open_tickets: int
    overdue_tickets: int
    avg_first_response_hours: float | None
    avg_resolution_hours: float | None
    avg_satisfaction: float | None
    tickets_by_status: dict[str, int]
    tickets_by_priority: dict[str, int]


async def compute_ticket_metrics(session: AsyncSession, *, now: datetime | None = None) -> TicketMetrics:
    """Compute the support KPI snapshot in one place.

    ``now`` is injectable for testing.
    """
    cutoff = now if now is not None else datetime.now(UTC)

    total = (await session.execute(select(func.count(SupportTicket.id)))).scalar() or 0

    open_count = (
        await session.execute(
            select(func.count(SupportTicket.id)).where(SupportTicket.status.in_(OPEN_TICKET_STATUSES))
        )
    ).scalar() or 0

    overdue_count = (
        await session.execute(
            select(func.count(SupportTicket.id)).where(
                SupportTicket.due_at < cutoff,
                SupportTicket.status.in_(OPEN_TICKET_STATUSES),
            )
        )
    ).scalar() or 0

    avg_sat = (
        await session.execute(
            select(func.avg(SupportTicket.satisfaction_rating)).where(SupportTicket.satisfaction_rating.isnot(None))
        )
    ).scalar()

    status_counts = (
        await session.execute(select(SupportTicket.status, func.count(SupportTicket.id)).group_by(SupportTicket.status))
    ).all()

    priority_counts = (
        await session.execute(
            select(SupportTicket.priority, func.count(SupportTicket.id)).group_by(SupportTicket.priority)
        )
    ).all()

    avg_first_response = (
        await session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        SupportTicket.first_response_at - SupportTicket.created_at,
                    )
                    / 3600
                )
            ).where(SupportTicket.first_response_at.isnot(None))
        )
    ).scalar()

    avg_resolution = (
        await session.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        SupportTicket.resolved_at - SupportTicket.created_at,
                    )
                    / 3600
                )
            ).where(SupportTicket.resolved_at.isnot(None))
        )
    ).scalar()

    return TicketMetrics(
        total_tickets=int(total),
        open_tickets=int(open_count),
        overdue_tickets=int(overdue_count),
        avg_first_response_hours=(round(float(avg_first_response), 1) if avg_first_response else None),
        avg_resolution_hours=(round(float(avg_resolution), 1) if avg_resolution else None),
        avg_satisfaction=float(avg_sat) if avg_sat else None,
        tickets_by_status={row[0]: row[1] for row in status_counts},
        tickets_by_priority={row[0]: row[1] for row in priority_counts},
    )


# ─── Canned responses ────────────────────────────────────────────────────────


async def list_canned_responses(session: AsyncSession) -> list[CannedResponse]:
    return list((await session.execute(select(CannedResponse))).scalars().all())


async def create_canned_response(
    session: AsyncSession,
    *,
    author_id: UUID,
    title: str,
    body: str,
    category: str | None,
    shortcut: str | None,
) -> CannedResponse:
    cr = CannedResponse(
        title=title,
        body=body,
        category=category,
        shortcut=shortcut,
        created_by_id=author_id,
    )
    session.add(cr)
    await session.commit()
    await session.refresh(cr)
    return cr


async def get_canned_response(session: AsyncSession, response_id: UUID) -> CannedResponse | None:
    return await session.get(CannedResponse, response_id)


async def delete_canned_response(session: AsyncSession, cr: CannedResponse) -> None:
    await session.delete(cr)
    await session.commit()


# ─── Channels ────────────────────────────────────────────────────────────────


async def list_support_channels(session: AsyncSession) -> list[SupportChannel]:
    return list((await session.execute(select(SupportChannel))).scalars().all())


async def get_support_channel(session: AsyncSession, channel_id: UUID) -> SupportChannel | None:
    return await session.get(SupportChannel, channel_id)


async def update_support_channel(
    session: AsyncSession,
    channel: SupportChannel,
    *,
    is_enabled: bool | None = None,
    min_plan: str | None = None,
    config_json: dict | None = None,
) -> SupportChannel:
    if is_enabled is not None:
        channel.is_enabled = is_enabled
    if min_plan is not None:
        channel.min_plan = min_plan
    if config_json is not None:
        channel.config_json = config_json
    await session.commit()
    return channel
