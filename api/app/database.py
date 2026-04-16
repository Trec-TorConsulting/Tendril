from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    pool_size=_settings.database_pool_size,
    max_overflow=5,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yield a plain session (no tenant context)."""
    async with async_session_factory() as session:
        yield session


@asynccontextmanager
async def tenant_session(tenant_id: UUID) -> AsyncGenerator[AsyncSession, None]:
    """Context manager that sets RLS tenant context for the session."""
    async with async_session_factory() as session:
        # SET doesn't support parameterized queries in asyncpg;
        # tenant_id is a validated UUID so safe to interpolate.
        tid = str(tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid}'"))
        yield session


async def get_tenant_db(tenant_id: UUID) -> AsyncGenerator[AsyncSession, None]:
    """Dependency version of tenant_session (for use with Depends)."""
    async with tenant_session(tenant_id) as session:
        yield session
