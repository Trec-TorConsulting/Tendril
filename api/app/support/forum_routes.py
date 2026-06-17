"""Community Forum — threads, posts, voting, moderation.

This module is HTTP-only. All persistence, view-count bookkeeping,
solution marking, and pin/lock toggles live in
``app.support.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.database import async_session_factory
from app.support import service

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
    categories = await service.list_forum_categories(session)
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
    """List forum threads, optionally filtered by category. Pinned first."""
    threads, total = await service.list_forum_threads_page(
        session, category_slug=category_slug, page=page, per_page=per_page
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
    thread = await service.get_forum_thread_with_posts(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    await service.increment_forum_thread_views(session, thread)

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
    category = await service.get_forum_category(session, body.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    thread = await service.create_forum_thread(
        session,
        category=category,
        author_id=user.user_id,
        title=body.title,
        body=body.body,
    )
    return {"id": str(thread.id), "title": thread.title}


@router.post("/threads/{thread_id}/posts", status_code=201)
async def create_post(
    thread_id: UUID,
    body: CreatePostRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Reply to a forum thread."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    if service.is_forum_thread_locked(thread):
        raise HTTPException(status_code=403, detail="Thread is locked")

    post = await service.create_forum_post(session, thread, author_id=user.user_id, body=body.body)
    return {"id": str(post.id)}


@router.post("/threads/{thread_id}/upvote")
async def upvote_thread(
    thread_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Upvote a thread."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    await service.upvote_forum_thread(session, thread)
    return {"upvotes": thread.upvotes}


@router.post("/posts/{post_id}/upvote")
async def upvote_post(
    post_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Upvote a post."""
    post = await service.get_forum_post(session, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await service.upvote_forum_post(session, post)
    return {"upvotes": post.upvotes}


# ─── Moderation (Admin) ──────────────────────────────────────────────────────


@router.post("/threads/{thread_id}/mark-solution", dependencies=[Depends(require_role("admin"))])
async def mark_solution(
    thread_id: UUID,
    post_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Mark a post as the solution for a thread."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    post = await service.get_forum_post(session, post_id)
    if post is None or post.thread_id != thread_id:
        raise HTTPException(status_code=404, detail="Post not found in thread")

    await service.mark_forum_solution(session, thread, post)
    return {"status": "solution_marked"}


@router.post("/threads/{thread_id}/pin", dependencies=[Depends(require_role("admin"))])
async def toggle_pin(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Toggle pin status on a thread."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    await service.toggle_forum_pin(session, thread)
    return {"is_pinned": thread.is_pinned}


@router.post("/threads/{thread_id}/lock", dependencies=[Depends(require_role("admin"))])
async def toggle_lock(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Toggle lock status on a thread."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    await service.toggle_forum_lock(session, thread)
    return {"status": thread.status}


@router.delete("/threads/{thread_id}", dependencies=[Depends(require_role("admin"))], status_code=204)
async def delete_thread(
    thread_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a thread and all its posts (admin only)."""
    thread = await service.get_forum_thread(session, thread_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    await service.delete_forum_thread(session, thread)
