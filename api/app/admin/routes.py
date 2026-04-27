"""Platform admin routes — cross-tenant management for super admins and support."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, require_platform_admin, require_support_or_admin
from app.database import async_session_factory
from app.pagination import PaginatedResponse, PaginationParams
from app.tenants.models import Tenant, User

router = APIRouter()


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ---------- Response models ----------

class TenantSummary(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    user_count: int
    created_at: str


class UserSummary(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    role: str
    tenant_id: UUID
    tenant_name: str
    is_platform_admin: bool
    is_support: bool
    email_verified: bool
    created_at: str


class UpdateUserFlags(BaseModel):
    is_platform_admin: bool | None = None
    is_support: bool | None = None
    role: str | None = None


class PlatformStatsResponse(BaseModel):
    total_tenants: int
    total_users: int
    plans: dict[str, int]


# ---------- Tenant endpoints (support + admin) ----------

@router.get("/tenants", response_model=PaginatedResponse[TenantSummary])
async def list_all_tenants(
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all tenants across the platform (paginated)."""
    stmt = (
        select(
            Tenant.id, Tenant.name, Tenant.slug, Tenant.plan, Tenant.created_at,
            func.count(User.id).label("user_count"),
        )
        .outerjoin(User, User.tenant_id == Tenant.id)
        .group_by(Tenant.id)
        .order_by(Tenant.created_at.desc())
    )
    # Manual pagination for grouped query
    count_stmt = select(func.count()).select_from(select(Tenant.id).subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = stmt.offset(pagination.offset).limit(pagination.page_size)
    rows = (await db.execute(stmt)).all()
    items = [
        TenantSummary(
            id=r.id, name=r.name, slug=r.slug, plan=r.plan,
            user_count=r.user_count, created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/tenants/{tenant_id}/users", response_model=list[UserSummary])
async def list_tenant_users(
    tenant_id: UUID,
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """List all users in a specific tenant."""
    stmt = (
        select(User, Tenant.name.label("tenant_name"))
        .join(Tenant, Tenant.id == User.tenant_id)
        .where(User.tenant_id == tenant_id)
        .order_by(User.created_at)
    )
    rows = (await db.execute(stmt)).all()
    return [
        UserSummary(
            id=u.id, email=u.email, display_name=u.display_name,
            role=u.role, tenant_id=u.tenant_id, tenant_name=tn,
            is_platform_admin=u.is_platform_admin, is_support=u.is_support,
            email_verified=u.email_verified, created_at=u.created_at.isoformat(),
        )
        for u, tn in rows
    ]


# ---------- User management (admin only) ----------

@router.get("/users", response_model=PaginatedResponse[UserSummary])
async def list_all_users(
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all users across the platform (paginated)."""
    count_stmt = select(func.count(User.id))
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = (
        select(User, Tenant.name.label("tenant_name"))
        .join(Tenant, Tenant.id == User.tenant_id)
        .order_by(User.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    rows = (await db.execute(stmt)).all()
    items = [
        UserSummary(
            id=u.id, email=u.email, display_name=u.display_name,
            role=u.role, tenant_id=u.tenant_id, tenant_name=tn,
            is_platform_admin=u.is_platform_admin, is_support=u.is_support,
            email_verified=u.email_verified, created_at=u.created_at.isoformat(),
        )
        for u, tn in rows
    ]
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.patch("/users/{user_id}", response_model=UserSummary)
async def update_user_flags(
    user_id: UUID,
    body: UpdateUserFlags,
    admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Update user platform flags (admin only). Cannot demote yourself."""
    stmt = (
        select(User, Tenant.name.label("tenant_name"))
        .join(Tenant, Tenant.id == User.tenant_id)
        .where(User.id == user_id)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    user, tenant_name = row

    # Prevent self-demotion
    if user.id == admin.user_id and body.is_platform_admin is False:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin access")

    if body.is_platform_admin is not None:
        user.is_platform_admin = body.is_platform_admin
    if body.is_support is not None:
        user.is_support = body.is_support
    if body.role is not None:
        if body.role not in ("owner", "member", "viewer"):
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role = body.role

    await db.commit()
    await db.refresh(user)

    return UserSummary(
        id=user.id, email=user.email, display_name=user.display_name,
        role=user.role, tenant_id=user.tenant_id, tenant_name=tenant_name,
        is_platform_admin=user.is_platform_admin, is_support=user.is_support,
        email_verified=user.email_verified, created_at=user.created_at.isoformat(),
    )


# ---------- Stats (support + admin) ----------

@router.get("/stats", response_model=PlatformStatsResponse)
async def platform_stats(
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Platform-wide statistics."""
    tenant_count = (await db.execute(select(func.count(Tenant.id)))).scalar() or 0
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    plan_counts = (
        await db.execute(
            select(Tenant.plan, func.count(Tenant.id))
            .group_by(Tenant.plan)
        )
    ).all()

    return {
        "total_tenants": tenant_count,
        "total_users": user_count,
        "plans": dict(plan_counts),
    }
