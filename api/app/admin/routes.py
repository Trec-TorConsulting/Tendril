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
from app.tenants.models import Account, PlatformRole, Tenant, TenantMembership, TenantRole, User

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
    platform_role: str
    tenant_id: UUID | None = None
    tenant_name: str | None = None
    tenant_role: str | None = None
    email_verified: bool
    created_at: str
    # Backward compat
    role: str | None = None
    is_platform_admin: bool = False
    is_support: bool = False


class UpdateUserFlags(BaseModel):
    platform_role: str | None = None


class UpdateTenantPlan(BaseModel):
    plan: str


class CreateTenantRequest(BaseModel):
    name: str
    slug: str
    plan: str = "free"
    owner_user_id: UUID | None = None


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
            Tenant.id,
            Tenant.name,
            Tenant.slug,
            Tenant.plan,
            Tenant.created_at,
            func.count(TenantMembership.id).label("user_count"),
        )
        .outerjoin(TenantMembership, TenantMembership.tenant_id == Tenant.id)
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
            id=r.id,
            name=r.name,
            slug=r.slug,
            plan=r.plan,
            user_count=r.user_count,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.post("/tenants", response_model=TenantSummary, status_code=201)
async def create_tenant(
    body: CreateTenantRequest,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Create a new organization/tenant (admin only)."""
    # Check slug uniqueness
    existing = await db.execute(select(Tenant.id).where(Tenant.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A tenant with this slug already exists")

    # Create an account for the tenant
    account = Account(name=body.name)
    db.add(account)
    await db.flush()

    tenant = Tenant(name=body.name, slug=body.slug, plan=body.plan, account_id=account.id)
    db.add(tenant)
    await db.flush()

    # If an owner user is specified, add them as admin member
    if body.owner_user_id:
        owner = await db.execute(select(User).where(User.id == body.owner_user_id))
        owner_user = owner.scalar_one_or_none()
        if not owner_user:
            raise HTTPException(status_code=404, detail="Owner user not found")
        membership = TenantMembership(tenant_id=tenant.id, user_id=owner_user.id, role=TenantRole.admin)
        db.add(membership)

    await db.commit()
    await db.refresh(tenant)

    user_count_result = await db.execute(
        select(func.count(TenantMembership.id)).where(TenantMembership.tenant_id == tenant.id)
    )
    user_count = user_count_result.scalar() or 0

    return TenantSummary(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        plan=tenant.plan,
        user_count=user_count,
        created_at=tenant.created_at.isoformat(),
    )


@router.get("/tenants/{tenant_id}/users", response_model=list[UserSummary])
async def list_tenant_users(
    tenant_id: UUID,
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """List all users in a specific tenant."""
    stmt = (
        select(User, TenantMembership.role, Tenant.name.label("tenant_name"))
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(User.created_at)
    )
    rows = (await db.execute(stmt)).all()
    return [
        UserSummary(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            platform_role=u.platform_role.value,
            tenant_id=tenant_id,
            tenant_name=tn,
            tenant_role=tr.value,
            email_verified=u.email_verified,
            created_at=u.created_at.isoformat(),
            role=tr.value,
            is_platform_admin=u.platform_role == PlatformRole.super_admin,
            is_support=u.platform_role == PlatformRole.support,
        )
        for u, tr, tn in rows
    ]


@router.patch("/tenants/{tenant_id}", response_model=TenantSummary)
async def update_tenant_plan(
    tenant_id: UUID,
    body: UpdateTenantPlan,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Override a tenant's plan without billing (admin only)."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant.plan = body.plan
    await db.commit()
    await db.refresh(tenant)

    user_count_result = await db.execute(
        select(func.count(TenantMembership.id)).where(TenantMembership.tenant_id == tenant_id)
    )
    user_count = user_count_result.scalar() or 0

    return TenantSummary(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        plan=tenant.plan,
        user_count=user_count,
        created_at=tenant.created_at.isoformat(),
    )


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
    stmt = select(User).order_by(User.created_at.desc()).offset(pagination.offset).limit(pagination.page_size)
    users = (await db.execute(stmt)).scalars().all()
    items = [
        UserSummary(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            platform_role=u.platform_role.value,
            email_verified=u.email_verified,
            created_at=u.created_at.isoformat(),
            is_platform_admin=u.platform_role == PlatformRole.super_admin,
            is_support=u.platform_role == PlatformRole.support,
        )
        for u in users
    ]
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.patch("/users/{user_id}", response_model=UserSummary)
async def update_user_flags(
    user_id: UUID,
    body: UpdateUserFlags,
    admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Update user platform role (admin only). Cannot demote yourself."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.platform_role is not None:
        # Validate enum value
        try:
            new_role = PlatformRole(body.platform_role)
        except ValueError as err:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform_role. Must be one of: {[r.value for r in PlatformRole]}",
            ) from err

        # Prevent self-demotion from super_admin
        if user.id == admin.user_id and new_role != PlatformRole.super_admin:
            raise HTTPException(status_code=400, detail="Cannot remove your own admin access")

        user.platform_role = new_role

    await db.commit()
    await db.refresh(user)

    return UserSummary(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        platform_role=user.platform_role.value,
        email_verified=user.email_verified,
        created_at=user.created_at.isoformat(),
        is_platform_admin=user.platform_role == PlatformRole.super_admin,
        is_support=user.platform_role == PlatformRole.support,
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
    plan_counts = (await db.execute(select(Tenant.plan, func.count(Tenant.id)).group_by(Tenant.plan))).all()

    return {
        "total_tenants": tenant_count,
        "total_users": user_count,
        "plans": dict(plan_counts),
    }
