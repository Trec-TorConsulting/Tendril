"""Shared pagination utilities for list endpoints."""

from __future__ import annotations

from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class PaginationParams:
    """FastAPI dependency for pagination query parameters."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


class PaginatedResponse[T](BaseModel):
    """Standard paginated response envelope."""

    items: list[T]
    total: int
    page: int
    page_size: int

    model_config = {"from_attributes": True}


async def paginate(
    session: AsyncSession,
    query: Select,
    pagination: PaginationParams,
) -> tuple[list, int]:
    """Execute a query with pagination. Returns (items, total_count).

    Usage:
        items, total = await paginate(session, query, pagination)
        return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)
    """
    # Count total matching rows
    count_query = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_query)).scalar() or 0

    # Apply pagination
    paginated_query = query.offset(pagination.offset).limit(pagination.page_size)
    result = await session.execute(paginated_query)
    items = list(result.scalars().all())

    return items, total
