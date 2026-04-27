from __future__ import annotations

from typing import Annotated
from uuid import UUID

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit import record_audit
from app.auth.middleware import CurrentUser, get_current_user, require_role
from app.auth.password import validate_password_strength
from app.database import get_db
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.tenants.models import Tenant, User

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
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantResponse(id=tenant.id, name=tenant.name, slug=tenant.slug, plan=tenant.plan)


@router.patch("/me", response_model=TenantResponse)
async def update_my_tenant(
    body: UpdateTenantRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update tenant name. Owner only."""
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if body.name is not None:
        tenant.name = body.name
    await db.commit()
    await db.refresh(tenant)
    return TenantResponse(id=tenant.id, name=tenant.name, slug=tenant.slug, plan=tenant.plan)


@router.get("/members")
async def list_members(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
):
    q = select(User).where(User.tenant_id == user.tenant_id).order_by(User.created_at)
    items, total = await paginate(db, q, pagination)
    return PaginatedResponse(
        items=[
            TenantMemberResponse(
                id=u.id, email=u.email, display_name=u.display_name, role=u.role,
                email_verified=u.email_verified, created_at=u.created_at.isoformat(),
            )
            for u in items
        ],
        total=total, page=pagination.page, page_size=pagination.page_size,
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

    # Check email isn't already in use
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = User(
        tenant_id=user.tenant_id,
        email=body.email,
        password_hash=bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode(),
        display_name=body.display_name,
        role=body.role,
        auth_provider="local",
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await record_audit(db, user.tenant_id, user.user_id, "create", "member", str(new_user.id), request=request)
    await db.commit()
    return TenantMemberResponse(
        id=new_user.id, email=new_user.email, display_name=new_user.display_name,
        role=new_user.role, email_verified=new_user.email_verified,
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

    result = await db.execute(
        select(User).where(User.id == member_id, User.tenant_id == user.tenant_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.id == user.user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    member.role = body.role
    await db.commit()
    await db.refresh(member)
    return TenantMemberResponse(
        id=member.id, email=member.email, display_name=member.display_name,
        role=member.role, email_verified=member.email_verified,
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
    result = await db.execute(
        select(User).where(User.id == member_id, User.tenant_id == user.tenant_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if member.id == user.user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")

    await record_audit(db, user.tenant_id, user.user_id, "delete", "member", str(member_id), request=request)
    await db.delete(member)
    await db.commit()
