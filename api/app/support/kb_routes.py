"""Knowledge Base — Public and Admin endpoints."""

from __future__ import annotations

import logging
import re
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.database import async_session_factory
from app.support.models import KBArticle, KBCategory

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


def _slugify(text: str) -> str:
    """Generate a URL-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


# ─── Public Endpoints ─────────────────────────────────────────────────────────


@router.get("/categories")
async def list_categories(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[dict]:
    """List published KB categories with article counts."""
    categories = (
        (
            await session.execute(
                select(KBCategory).where(KBCategory.is_published.is_(True)).order_by(KBCategory.sort_order)
            )
        )
        .scalars()
        .all()
    )

    result = []
    for cat in categories:
        article_count = (
            await session.execute(
                select(func.count(KBArticle.id)).where(
                    KBArticle.category_id == cat.id, KBArticle.is_published.is_(True)
                )
            )
        ).scalar() or 0
        result.append(
            {
                "id": str(cat.id),
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "icon": cat.icon,
                "article_count": article_count,
            }
        )
    return result


@router.get("/articles")
async def list_articles(
    session: Annotated[AsyncSession, Depends(_get_db)],
    category_slug: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """List published KB articles, optionally filtered by category."""
    query = select(KBArticle).where(KBArticle.is_published.is_(True))

    if category_slug:
        cat = (await session.execute(select(KBCategory).where(KBCategory.slug == category_slug))).scalar_one_or_none()
        if cat:
            query = query.where(KBArticle.category_id == cat.id)

    total = (await session.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

    articles = (
        (await session.execute(query.order_by(KBArticle.sort_order).offset((page - 1) * per_page).limit(per_page)))
        .scalars()
        .all()
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
    # Simple ILIKE search (can upgrade to tsvector later)
    pattern = f"%{q}%"
    articles = (
        (
            await session.execute(
                select(KBArticle)
                .where(
                    KBArticle.is_published.is_(True),
                    or_(
                        KBArticle.title.ilike(pattern),
                        KBArticle.body_markdown.ilike(pattern),
                    ),
                )
                .limit(20)
            )
        )
        .scalars()
        .all()
    )

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
    article = (
        await session.execute(select(KBArticle).where(KBArticle.slug == slug, KBArticle.is_published.is_(True)))
    ).scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment view count
    article.views += 1
    await session.commit()

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
    article = (await session.execute(select(KBArticle).where(KBArticle.slug == slug))).scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if helpful:
        article.helpful_yes += 1
    else:
        article.helpful_no += 1

    await session.commit()
    return {"helpful_yes": article.helpful_yes, "helpful_no": article.helpful_no}


# ─── Admin Endpoints ──────────────────────────────────────────────────────────


@router.post("/admin/categories", dependencies=[Depends(require_role("admin"))], status_code=201)
async def create_category(
    body: CategoryCreate,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a KB category."""
    slug = body.slug or _slugify(body.name)
    cat = KBCategory(
        name=body.name,
        slug=slug,
        description=body.description,
        icon=body.icon,
        sort_order=body.sort_order,
    )
    session.add(cat)
    await session.commit()
    await session.refresh(cat)
    return {"id": str(cat.id), "slug": cat.slug}


@router.delete("/admin/categories/{category_id}", dependencies=[Depends(require_role("admin"))], status_code=204)
async def delete_category(
    category_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a KB category and all its articles."""
    cat = await session.get(KBCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(cat)
    await session.commit()


@router.post("/admin/articles", dependencies=[Depends(require_role("admin"))], status_code=201)
async def create_article(
    body: ArticleCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Create a KB article."""
    slug = body.slug or _slugify(body.title)
    article = KBArticle(
        category_id=body.category_id,
        title=body.title,
        slug=slug,
        body_markdown=body.body_markdown,
        tags=body.tags or [],
        is_published=body.is_published,
        sort_order=body.sort_order,
        author_id=user.id,
    )
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return {"id": str(article.id), "slug": article.slug}


@router.patch("/admin/articles/{article_id}", dependencies=[Depends(require_role("admin"))])
async def update_article(
    article_id: UUID,
    body: ArticleUpdate,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> dict:
    """Update a KB article."""
    article = await session.get(KBArticle, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if body.title is not None:
        article.title = body.title
    if body.body_markdown is not None:
        article.body_markdown = body.body_markdown
    if body.tags is not None:
        article.tags = body.tags
    if body.is_published is not None:
        article.is_published = body.is_published
    if body.sort_order is not None:
        article.sort_order = body.sort_order
    if body.category_id is not None:
        article.category_id = body.category_id

    await session.commit()
    return {"status": "updated"}


@router.delete("/admin/articles/{article_id}", dependencies=[Depends(require_role("admin"))], status_code=204)
async def delete_article(
    article_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Delete a KB article."""
    article = await session.get(KBArticle, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await session.delete(article)
    await session.commit()
