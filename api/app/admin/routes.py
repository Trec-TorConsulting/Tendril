"""Platform admin routes — cross-tenant management for super admins and support.

This module is HTTP-only. All persistence, role coercion, and the
self-modification safety checks live in ``app.admin.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin import service
from app.auth.middleware import CurrentUser, require_platform_admin, require_support_or_admin
from app.database import async_session_factory
from app.pagination import PaginatedResponse, PaginationParams
from app.tenants.models import PlatformRole

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
):
    """List all tenants across the platform (paginated)."""
    rows, total = await service.list_tenants_page(db, offset=pagination.offset, limit=pagination.page_size)
    items = [
        TenantSummary(
            id=r.id,
            name=r.name,
            slug=r.slug,
            plan=r.plan,
            user_count=r.user_count,
            created_at=r.created_at,
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
    # 404 owner verification stays in routes — it's a request-input check.
    if body.owner_user_id is not None:
        owner = await service.get_user(db, body.owner_user_id)
        if owner is None:
            raise HTTPException(status_code=404, detail="Owner user not found")

    try:
        tenant = await service.create_tenant(
            db,
            name=body.name,
            slug=body.slug,
            plan=body.plan,
            owner_user_id=body.owner_user_id,
        )
    except service.TenantSlugTakenError as exc:
        raise HTTPException(status_code=409, detail="A tenant with this slug already exists") from exc

    user_count = await service.count_tenant_users(db, tenant.id)
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
    rows = await service.list_tenant_users(db, tenant_id)
    return [
        UserSummary(
            id=r.user.id,
            email=r.user.email,
            display_name=r.user.display_name,
            platform_role=r.user.platform_role.value,
            tenant_id=tenant_id,
            tenant_name=r.tenant_name,
            tenant_role=r.tenant_role.value,
            email_verified=r.user.email_verified,
            created_at=r.user.created_at.isoformat(),
            role=r.tenant_role.value,
            is_platform_admin=r.user.platform_role == PlatformRole.super_admin,
            is_support=r.user.platform_role == PlatformRole.support,
        )
        for r in rows
    ]


@router.patch("/tenants/{tenant_id}", response_model=TenantSummary)
async def update_tenant_plan(
    tenant_id: UUID,
    body: UpdateTenantPlan,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Override a tenant's plan without billing (admin only)."""
    tenant = await service.get_tenant(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = await service.update_tenant_plan(db, tenant, plan=body.plan)
    user_count = await service.count_tenant_users(db, tenant_id)
    return TenantSummary(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        plan=tenant.plan,
        user_count=user_count,
        created_at=tenant.created_at.isoformat(),
    )


# ---------- User management ----------


@router.get("/users", response_model=PaginatedResponse[UserSummary])
async def list_all_users(
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all users across the platform (paginated)."""
    users, total = await service.list_users_page(db, offset=pagination.offset, limit=pagination.page_size)
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
    user = await service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if body.platform_role is not None:
        try:
            new_role = service.coerce_platform_role(body.platform_role)
        except service.InvalidPlatformRoleError as err:
            raise HTTPException(
                status_code=400,
                detail=(f"Invalid platform_role. Must be one of: {[r.value for r in PlatformRole]}"),
            ) from err

        try:
            await service.update_user_platform_role(db, user, new_role=new_role, actor_user_id=admin.user_id)
        except service.SelfDemotionError as err:
            raise HTTPException(status_code=400, detail="Cannot remove your own admin access") from err

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
    """Permanently delete a user and all their memberships (admin only)."""
    # We surface the self-delete check before the lookup so the error
    # matches the previous behaviour exactly (400 even when the target
    # user does not exist — the actor's intent is clear from the id).
    if user_id == admin.user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = await service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    email = await service.delete_user_cascade(db, user, actor_user_id=admin.user_id)
    logger.warning("Admin deleted user %s (%s)", user_id, email)
    return {"status": "deleted", "message": f"User '{email}' has been permanently deleted."}


# ---------- Stats ----------


@router.get("/stats", response_model=PlatformStatsResponse)
async def platform_stats(
    _user: Annotated[CurrentUser, Depends(require_support_or_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Platform-wide statistics."""
    stats = await service.compute_platform_stats(db)
    return PlatformStatsResponse(
        total_tenants=stats.total_tenants,
        total_users=stats.total_users,
        plans=stats.plans,
    )


# ---------- Tenant deletion (admin only) ----------


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: UUID,
    _admin: Annotated[CurrentUser, Depends(require_platform_admin)],
    db: Annotated[AsyncSession, Depends(_get_db)],
):
    """Permanently delete an organization, its memberships, and its account (admin only)."""
    tenant = await service.get_tenant(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    tenant_name = await service.delete_tenant_cascade(db, tenant)
    logger.warning("Admin deleted tenant %s (%s)", tenant_id, tenant_name)
    return {
        "status": "deleted",
        "message": f"Organization '{tenant_name}' has been permanently deleted.",
    }
