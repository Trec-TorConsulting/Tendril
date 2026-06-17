"""Tenants API — tenant lookup/update + tenant-membership CRUD.

This module is HTTP-only. All persistence and role mapping live in
``app.tenants.service``.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import record_audit
from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.auth.password import validate_password_strength
from app.database import get_db
from app.pagination import PaginatedResponse, PaginationParams
from app.tenants import service

router = APIRouter()


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str


class TenantMemberResponse(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    role: str
    email_verified: bool
    created_at: str


class UpdateTenantRequest(BaseModel):
    name: str | None = None


class InviteMemberRequest(BaseModel):
    email: EmailStr
    display_name: str | None = None
    password: str
    role: str = "member"


class UpdateMemberRoleRequest(BaseModel):
    role: str


@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the current user's tenant details."""
    assert user.tenant_id is not None  # guaranteed by get_current_user issuing a tenant ctx
    tenant = await service.get_tenant(db, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantResponse(id=tenant.id, name=tenant.name, slug=tenant.slug, plan=tenant.plan)


@router.patch("/me", response_model=TenantResponse)
async def update_my_tenant(
    body: UpdateTenantRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update tenant name. Owner only."""
    assert user.tenant_id is not None  # guaranteed by require_role
    tenant = await service.get_tenant(db, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant = await service.update_tenant(db, tenant, name=body.name)
    return TenantResponse(id=tenant.id, name=tenant.name, slug=tenant.slug, plan=tenant.plan)


@router.get("/members", response_model=PaginatedResponse[TenantMemberResponse])
async def list_members(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    """List all members of the current tenant."""
    assert user.tenant_id is not None
    rows, total = await service.list_members_page(
        db,
        tenant_id=user.tenant_id,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    return PaginatedResponse(
        items=[
            TenantMemberResponse(
                id=row.user.id,
                email=row.user.email,
                display_name=row.user.display_name,
                role=service.tenant_role_to_legacy(row.role),
                email_verified=row.user.email_verified,
                created_at=row.user.created_at.isoformat(),
            )
            for row in rows
        ],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("/members", response_model=TenantMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    body: InviteMemberRequest,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a new member to the tenant. Owner only."""
    if body.role not in ("member", "viewer"):
        raise HTTPException(status_code=400, detail="Can only add members or viewers")

    validate_password_strength(body.password)

    if await service.get_user_by_email(db, body.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    assert user.tenant_id is not None
    new_user = await service.create_member(
        db,
        tenant_id=user.tenant_id,
        email=body.email,
        password=body.password,
        display_name=body.display_name,
        role=service.legacy_to_tenant_role(body.role),
    )
    await record_audit(db, user.tenant_id, user.user_id, "create", "member", str(new_user.id), request=request)
    await db.commit()
    return TenantMemberResponse(
        id=new_user.id,
        email=new_user.email,
        display_name=new_user.display_name,
        role=body.role,
        email_verified=new_user.email_verified,
        created_at=new_user.created_at.isoformat(),
    )


@router.patch("/members/{member_id}", response_model=TenantMemberResponse)
async def update_member_role(
    member_id: UUID,
    body: UpdateMemberRoleRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a member's role. Owner only. Cannot change own role."""
    if body.role not in ("owner", "member", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")

    assert user.tenant_id is not None
    membership = await service.get_membership(db, tenant_id=user.tenant_id, user_id=member_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if membership.user_id == user.user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    await service.update_membership_role(db, membership, service.legacy_to_tenant_role(body.role))

    member = await service.get_user(db, member_id)
    assert member is not None  # membership exists ⇒ user exists
    return TenantMemberResponse(
        id=member.id,
        email=member.email,
        display_name=member.display_name,
        role=body.role,
        email_verified=member.email_verified,
        created_at=member.created_at.isoformat(),
    )


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    member_id: UUID,
    request: Request,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a member from the tenant. Owner only. Cannot remove yourself."""
    assert user.tenant_id is not None
    membership = await service.get_membership(db, tenant_id=user.tenant_id, user_id=member_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if membership.user_id == user.user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")

    await record_audit(db, user.tenant_id, user.user_id, "delete", "member", str(member_id), request=request)
    await service.delete_membership(db, membership)
