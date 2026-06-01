from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

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


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Dependency: yield a plain session (no tenant context)."""
    async with async_session_factory() as session:
        yield session


@asynccontextmanager
async def tenant_session(tenant_id: UUID) -> AsyncGenerator[AsyncSession]:
    """Context manager that sets RLS tenant context for the session."""
    async with async_session_factory() as session:
        await set_rls_tenant(session, tenant_id)
        yield session


async def set_rls_tenant(session: AsyncSession, tenant_id: UUID) -> None:
    """Set the RLS tenant context using parameterized set_config()."""
    await session.execute(
        text("SELECT set_config('app.current_tenant', :tid, false)"),
        {"tid": str(tenant_id)},
    )


async def get_tenant_db(tenant_id: UUID) -> AsyncGenerator[AsyncSession]:
    """Dependency version of tenant_session (for use with Depends)."""
    async with tenant_session(tenant_id) as session:
        yield session
