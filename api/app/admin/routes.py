"""Platform admin routes — cross-tenant management for super admins and support."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, require_platform_admin, require_support_or_admin
from app.config import get_settings
from app.database import async_session_factory
from app.pagination import PaginatedResponse, PaginationParams
from app.tenants.models import Account, PlatformRole, Tenant, TenantMembership, TenantRole, User

router = APIRouter()
logger = logging.getLogger("tendril.admin")


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
    deleted_at: str | None = None


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
    deleted_at: str | None = None
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
    include_deleted: bool = Query(default=True, description="Include soft-deleted tenants"),
):
    """List all tenants across the platform (paginated)."""
    stmt = (
        select(
            Tenant.id,
            Tenant.name,
            Tenant.slug,
            Tenant.plan,
            Tenant.created_at,
            Tenant.deleted_at,
            func.count(TenantMembership.id).label("user_count"),
        )
        .outerjoin(TenantMembership, TenantMembership.tenant_id == Tenant.id)
        .group_by(Tenant.id)
        .order_by(Tenant.deleted_at.asc().nulls_first(), Tenant.created_at.desc())
    )
    if not include_deleted:
        stmt = stmt.where(Tenant.deleted_at.is_(None))
    # Manual pagination for grouped query
    count_stmt = select(func.count()).select_from(select(Tenant.id).subquery())
    if not include_deleted:
        count_stmt = select(func.count()).select_from(select(Tenant.id).where(Tenant.deleted_at.is_(None)).subquery())
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
            deleted_at=r.deleted_at.isoformat() if r.deleted_at else None,
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
    include_deleted: bool = Query(default=True, description="Include soft-deleted users"),
):
    """List all users across the platform (paginated)."""
    count_stmt = select(func.count(User.id))
    base_filter = select(User)
    if not include_deleted:
        count_stmt = count_stmt.where(User.deleted_at.is_(None))
        base_filter = base_filter.where(User.deleted_at.is_(None))
    total = (await db.execute(count_stmt)).scalar() or 0
    stmt = (
        base_filter.order_by(User.deleted_at.asc().nulls_first(), User.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    )
    users = (await db.execute(stmt)).scalars().all()
    items = [
        UserSummary(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            platform_role=u.platform_role.value,
            email_verified=u.email_verified,
            created_at=u.created_at.isoformat(),
            deleted_at=u.deleted_at.isoformat() if u.deleted_at else None,
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


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Soft-delete a user (admin only). Marks user for deletion after 30 days."""
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.deleted_at:
        raise HTTPException(status_code=400, detail="User is already scheduled for deletion")

    settings = get_settings()
    user.deleted_at = datetime.now(UTC)
    purge_date = user.deleted_at + timedelta(days=settings.data_retention_days)
    await db.commit()

    logger.info("Admin soft-deleted user %s (%s), purge date %s", user_id, user.email, purge_date)
    return {
        "status": "scheduled",
        "deletion_date": purge_date.isoformat(),
        "message": f"User '{user.email}' scheduled for deletion on {purge_date.strftime('%B %d, %Y')}.",
    }


@router.post("/users/{user_id}/restore")
async def restore_user(
    user_id: UUID,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Restore a soft-deleted user (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.deleted_at:
        raise HTTPException(status_code=400, detail="User is not deleted")

    user.deleted_at = None
    await db.commit()
    logger.info("Admin restored user %s (%s)", user_id, user.email)
    return {"status": "restored", "message": f"User '{user.email}' has been restored."}


@router.post("/tenants/{tenant_id}/restore")
async def restore_tenant(
    tenant_id: UUID,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Restore a soft-deleted tenant (admin only)."""
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not tenant.deleted_at:
        raise HTTPException(status_code=400, detail="Organization is not deleted")

    tenant.deleted_at = None
    await db.commit()
    logger.info("Admin restored tenant %s (%s)", tenant_id, tenant.name)
    return {"status": "restored", "message": f"Organization '{tenant.name}' has been restored."}


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


# ---------- Tenant deletion (admin only) ----------


class TenantDeletionResponse(BaseModel):
    status: str  # scheduled | deleted
    deletion_date: str | None = None
    message: str


@router.delete("/tenants/{tenant_id}", response_model=TenantDeletionResponse)
async def delete_tenant(
    tenant_id: UUID,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
    force: bool = Query(default=False, description="Immediately hard-delete (API only)"),
):
    """Delete an organization. Schedules 30-day grace period by default.

    Use ?force=true for immediate hard deletion (API-only, not exposed in UI).
    """
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not force and tenant.deleted_at:
        raise HTTPException(status_code=400, detail="Organization is already scheduled for deletion")

    if force:
        # Immediate hard delete — remove memberships, tenant, and account
        tenant_name = tenant.name
        account = await db.get(Account, tenant.account_id) if tenant.account_id else None

        await db.execute(delete(TenantMembership).where(TenantMembership.tenant_id == tenant.id))
        await db.delete(tenant)
        if account:
            # Only delete account if no other tenants reference it
            other_tenants = (
                await db.execute(
                    select(func.count(Tenant.id)).where(Tenant.account_id == account.id, Tenant.id != tenant_id)
                )
            ).scalar()
            if not other_tenants:
                await db.delete(account)

        await db.commit()
        logger.warning("Admin force-deleted tenant %s (%s)", tenant_id, tenant_name)
        return TenantDeletionResponse(
            status="deleted",
            message=f"Organization '{tenant_name}' and all its data have been permanently deleted.",
        )

    # Default: schedule 30-day grace period via soft-delete
    settings = get_settings()
    tenant.deleted_at = datetime.now(UTC)
    deletion_date = tenant.deleted_at + timedelta(days=settings.data_retention_days)

    await db.commit()
    logger.info("Admin scheduled deletion of tenant %s (%s) for %s", tenant_id, tenant.name, deletion_date)

    return TenantDeletionResponse(
        status="scheduled",
        deletion_date=deletion_date.isoformat(),
        message=(
            f"Organization '{tenant.name}' scheduled for deletion on"
            f" {deletion_date.strftime('%B %d, %Y')}. Data will be purged after this date."
        ),
    )
