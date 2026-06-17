"""Knowledge Base — Public and Admin endpoints.

This module is HTTP-only. All persistence, slug generation, view-count
bookkeeping, and vote tallying live in ``app.support.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.database import async_session_factory
from app.support import service

router = APIRouter()
logger = logging.getLogger("tendril.support.kb")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ─── Schemas ──────────────────────────────────────────────────────────────────


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    sort_order: int = 0


class ArticleCreate(BaseModel):
    category_id: UUID
    title: str = Field(min_length=3, max_length=255)
    slug: str | None = None
    body_markdown: str = Field(min_length=10)
    tags: list[str] | None = None
    is_published: bool = True
    sort_order: int = 0


class ArticleUpdate(BaseModel):
    title: str | None = None
    body_markdown: str | None = None
    tags: list[str] | None = None
    is_published: bool | None = None
    sort_order: int | None = None
    category_id: UUID | None = None


# ─── Public Endpoints ─────────────────────────────────────────────────────────


@router.get("/categories")
async def list_categories(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List published KB categories with article counts."""
    rows = await service.list_kb_categories_with_counts(session)
    return [
        {
            "id": str(row.category.id),
            "name": row.category.name,
            "slug": row.category.slug,
            "description": row.category.description,
            "icon": row.category.icon,
            "article_count": row.article_count,
        }
        for row in rows
    ]


@router.get("/articles")
async def list_articles(
    session: Annotated[AsyncSession, Depends(_get_db)],
    category_slug: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List published KB articles, optionally filtered by category."""
    articles, total = await service.list_kb_articles_page(
        session, category_slug=category_slug, page=page, per_page=per_page
    )
    return {
        "articles": [
            {
                "id": str(a.id),
                "title": a.title,
                "slug": a.slug,
                "tags": a.tags,
                "views": a.views,
                "helpful_yes": a.helpful_yes,
                "helpful_no": a.helpful_no,
                "created_at": a.created_at.isoformat(),
            }
            for a in articles
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/articles/search")
async def search_articles(
    q: Annotated[str, Query(min_length=2)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """Full-text search across KB articles."""
    articles = await service.search_kb_articles(session, q)
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "slug": a.slug,
            "tags": a.tags,
        }
        for a in articles
    ]


@router.get("/articles/{slug}")
async def get_article(
    slug: str,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Get a single KB article by slug."""
    article = await service.get_published_kb_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await service.increment_kb_article_views(session, article)
    return {
        "id": str(article.id),
        "title": article.title,
        "slug": article.slug,
        "body_markdown": article.body_markdown,
        "tags": article.tags,
        "views": article.views,
        "helpful_yes": article.helpful_yes,
        "helpful_no": article.helpful_no,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat(),
    }


@router.post("/articles/{slug}/vote")
async def vote_article(
    slug: str,
    session: Annotated[AsyncSession, Depends(_get_db)],
    helpful: bool = True,
):
    """Vote on article helpfulness."""
    article = await service.get_kb_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await service.vote_kb_article(session, article, helpful=helpful)
    return {"helpful_yes": article.helpful_yes, "helpful_no": article.helpful_no}


# ─── Admin Endpoints ──────────────────────────────────────────────────────────


@router.post("/admin/categories", dependencies=[Depends(require_role("admin"))], status_code=201)
async def create_category(
    body: CategoryCreate,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a KB category."""
    cat = await service.create_kb_category(
        session,
        name=body.name,
        slug=body.slug,
        description=body.description,
        icon=body.icon,
        sort_order=body.sort_order,
    )
    return {"id": str(cat.id), "slug": cat.slug}


@router.delete(
    "/admin/categories/{category_id}",
    dependencies=[Depends(require_role("admin"))],
    status_code=204,
)
async def delete_category(
    category_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a KB category and all its articles."""
    cat = await service.get_kb_category(session, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await service.delete_kb_category(session, cat)


@router.post("/admin/articles", dependencies=[Depends(require_role("admin"))], status_code=201)
async def create_article(
    body: ArticleCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a KB article."""
    article = await service.create_kb_article(
        session,
        category_id=body.category_id,
        author_id=user.user_id,
        title=body.title,
        slug=body.slug,
        body_markdown=body.body_markdown,
        tags=body.tags,
        is_published=body.is_published,
        sort_order=body.sort_order,
    )
    return {"id": str(article.id), "slug": article.slug}


@router.patch("/admin/articles/{article_id}", dependencies=[Depends(require_role("admin"))])
async def update_article(
    article_id: UUID,
    body: ArticleUpdate,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Update a KB article."""
    article = await service.get_kb_article(session, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await service.update_kb_article(
        session,
        article,
        title=body.title,
        body_markdown=body.body_markdown,
        tags=body.tags,
        is_published=body.is_published,
        sort_order=body.sort_order,
        category_id=body.category_id,
    )
    return {"status": "updated"}


@router.delete(
    "/admin/articles/{article_id}",
    dependencies=[Depends(require_role("admin"))],
    status_code=204,
)
async def delete_article(
    article_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a KB article."""
    article = await service.get_kb_article(session, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    await service.delete_kb_article(session, article)
