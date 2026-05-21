"""Community Forum — threads, posts, voting, moderation."""

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

from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.database import async_session_factory
from app.support.models import ForumCategory, ForumPost, ForumThread, ForumThreadStatus

router = APIRouter()
logger = logging.getLogger("tendril.support.forum")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ─── Schemas ──────────────────────────────────────────────────────────────────


class CreateThreadRequest(BaseModel):
    category_id: UUID
    title: str = Field(min_length=5, max_length=255)
    body: str = Field(min_length=10)


class CreatePostRequest(BaseModel):
    body: str = Field(min_length=1)


# ─── Public Routes ────────────────────────────────────────────────────────────


@router.get("/categories")
async def list_forum_categories(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List forum categories with counts."""
    categories = (await session.execute(select(ForumCategory).order_by(ForumCategory.sort_order))).scalars().all()

    return [
        {
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "icon": c.icon,
            "thread_count": c.thread_count,
            "post_count": c.post_count,
        }
        for c in categories
    ]


@router.get("/threads")
async def list_threads(
    session: Annotated[AsyncSession, Depends(_get_db)],
    category_slug: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List forum threads, optionally filtered by category."""
    query = select(ForumThread)

    if category_slug:
        cat = (
            await session.execute(select(ForumCategory).where(ForumCategory.slug == category_slug))
        ).scalar_one_or_none()
        if cat:
            query = query.where(ForumThread.category_id == cat.id)

    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

    # Pinned first, then by last activity
    threads = (
        (
            await session.execute(
                query.order_by(ForumThread.is_pinned.desc(), ForumThread.last_activity_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
        )
        .scalars()
        .all()
    )

    return {
        "threads": [
            {
                "id": str(t.id),
                "title": t.title,
                "author_id": str(t.author_id),
                "status": t.status,
                "is_pinned": t.is_pinned,
                "view_count": t.view_count,
                "reply_count": t.reply_count,
                "upvotes": t.upvotes,
                "has_solution": t.solution_post_id is not None,
                "last_activity_at": t.last_activity_at.isoformat(),
                "created_at": t.created_at.isoformat(),
            }
            for t in threads
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Get a thread with all its posts."""
    thread = (
        await session.execute(
            select(ForumThread).where(ForumThread.id == thread_id).options(selectinload(ForumThread.posts))
        )
    ).scalar_one_or_none()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Increment view count
    thread.view_count += 1
    await session.commit()

    return {
        "id": str(thread.id),
        "title": thread.title,
        "body": thread.body,
        "author_id": str(thread.author_id),
        "status": thread.status,
        "is_pinned": thread.is_pinned,
        "view_count": thread.view_count,
        "reply_count": thread.reply_count,
        "upvotes": thread.upvotes,
        "solution_post_id": str(thread.solution_post_id) if thread.solution_post_id else None,
        "created_at": thread.created_at.isoformat(),
        "posts": [
            {
                "id": str(p.id),
                "author_id": str(p.author_id),
                "body": p.body,
                "is_solution": p.is_solution,
                "upvotes": p.upvotes,
                "created_at": p.created_at.isoformat(),
            }
            for p in thread.posts
        ],
    }


@router.post("/threads", status_code=201)
async def create_thread(
    body: CreateThreadRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a new forum thread."""
    # Verify category exists
    category = await session.get(ForumCategory, body.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    thread = ForumThread(
        category_id=body.category_id,
        author_id=user.user_id,
        title=body.title,
        body=body.body,
    )
    session.add(thread)

    # Update category counts
    category.thread_count += 1

    await session.commit()
    await session.refresh(thread)
    return {"id": str(thread.id), "title": thread.title}


@router.post("/threads/{thread_id}/posts", status_code=201)
async def create_post(
    thread_id: UUID,
    body: CreatePostRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Reply to a forum thread."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if thread.status == ForumThreadStatus.locked:
        raise HTTPException(status_code=403, detail="Thread is locked")

    post = ForumPost(
        thread_id=thread.id,
        author_id=user.user_id,
        body=body.body,
    )
    session.add(post)

    thread.reply_count += 1
    thread.last_activity_at = datetime.now(UTC)

    # Update category post count
    category = await session.get(ForumCategory, thread.category_id)
    if category:
        category.post_count += 1

    await session.commit()
    await session.refresh(post)
    return {"id": str(post.id)}


@router.post("/threads/{thread_id}/upvote")
async def upvote_thread(
    thread_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Upvote a thread."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    thread.upvotes += 1
    await session.commit()
    return {"upvotes": thread.upvotes}


@router.post("/posts/{post_id}/upvote")
async def upvote_post(
    post_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Upvote a post."""
    post = await session.get(ForumPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.upvotes += 1
    await session.commit()
    return {"upvotes": post.upvotes}


# ─── Moderation (Admin) ──────────────────────────────────────────────────────


@router.post("/threads/{thread_id}/mark-solution", dependencies=[Depends(require_role("admin"))])
async def mark_solution(
    thread_id: UUID,
    post_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Mark a post as the solution for a thread."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    post = await session.get(ForumPost, post_id)
    if not post or post.thread_id != thread_id:
        raise HTTPException(status_code=404, detail="Post not found in thread")

    # Unmark previous solution
    if thread.solution_post_id:
        old_post = await session.get(ForumPost, thread.solution_post_id)
        if old_post:
            old_post.is_solution = False

    thread.solution_post_id = post_id
    thread.status = ForumThreadStatus.solved
    post.is_solution = True

    await session.commit()
    return {"status": "solution_marked"}


@router.post("/threads/{thread_id}/pin", dependencies=[Depends(require_role("admin"))])
async def toggle_pin(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Toggle pin status on a thread."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    thread.is_pinned = not thread.is_pinned
    await session.commit()
    return {"is_pinned": thread.is_pinned}


@router.post("/threads/{thread_id}/lock", dependencies=[Depends(require_role("admin"))])
async def toggle_lock(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Toggle lock status on a thread."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if thread.status == ForumThreadStatus.locked:
        thread.status = ForumThreadStatus.open
    else:
        thread.status = ForumThreadStatus.locked

    await session.commit()
    return {"status": thread.status}


@router.delete("/threads/{thread_id}", dependencies=[Depends(require_role("admin"))], status_code=204)
async def delete_thread(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a thread and all its posts (admin only)."""
    thread = await session.get(ForumThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    await session.delete(thread)
    await session.commit()
