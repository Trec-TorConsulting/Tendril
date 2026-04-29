from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.auth.permissions import has_permission
from app.database import async_session_factory
from app.tenants.models import PlatformRole, TenantRole

_bearer = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    user_id: UUID
    tenant_id: UUID | None = None
    tenant_role: TenantRole | None = None
    platform_role: PlatformRole = PlatformRole.user
    grow_scope: list[UUID] | None = None  # None = unrestricted
    account_id: UUID | None = None

    model_config = {"frozen": True}

    # ─── Backward-compat shims (used during migration of route guards) ────
    @property
    def role(self) -> str:
        """Legacy: maps tenant_role to old string values."""
        if self.tenant_role == TenantRole.admin:
            return "owner"
        if self.tenant_role == TenantRole.member:
            return "member"
        if self.tenant_role == TenantRole.viewer:
            return "viewer"
        return "member"

    @property
    def is_platform_admin(self) -> bool:
        return self.platform_role == PlatformRole.super_admin

    @property
    def is_support(self) -> bool:
        return self.platform_role == PlatformRole.support


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> CurrentUser:
    """Extract and validate JWT from httpOnly cookie (preferred) or Authorization header (fallback)."""
    token: str | None = None

    # 1. Try httpOnly cookie first
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        token = cookie_token
    # 2. Fallback to Authorization header (for API keys, mobile clients, etc.)
    elif credentials:
        token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    # Parse platform role
    pr_raw = payload.get("pr", "user")
    try:
        platform_role = PlatformRole(pr_raw)
    except ValueError:
        platform_role = PlatformRole.user

    # Parse tenant role
    tr_raw = payload.get("tr")
    tenant_role: TenantRole | None = None
    if tr_raw:
        try:
            tenant_role = TenantRole(tr_raw)
        except ValueError:
            tenant_role = None

    # Parse grow scope
    gs_raw = payload.get("gs")
    grow_scope: list[UUID] | None = None
    if gs_raw is not None:
        grow_scope = [UUID(g) for g in gs_raw]

    # Parse tenant and account IDs
    tid_raw = payload.get("tid")
    aid_raw = payload.get("aid")

    return CurrentUser(
        user_id=UUID(payload["sub"]),
        tenant_id=UUID(tid_raw) if tid_raw else None,
        tenant_role=tenant_role,
        platform_role=platform_role,
        grow_scope=grow_scope,
        account_id=UUID(aid_raw) if aid_raw else None,
    )


# ─── Permission-based guards ──────────────────────────────────────────────────


def require_permission(*required_permissions: str):
    """Dependency factory: requires ALL specified permissions.

    Usage: Depends(require_permission("grow:read", "grow:update"))
    """

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        for perm in required_permissions:
            if not has_permission(user.platform_role, user.tenant_role, perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm}",
                )
        return user

    return _check


def require_platform_role(*allowed_roles: PlatformRole):
    """Dependency factory: requires one of the specified platform roles."""

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if user.platform_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient platform role",
            )
        return user

    return _check


def require_grow_access(grow_id_param: str = "grow_id"):
    """Dependency factory: verifies the user has access to the specific grow.

    Checks the grow_scope claim in the JWT. If grow_scope is None (unrestricted),
    access is always granted. Otherwise, the grow_id must be in the scope.
    Platform super_admins bypass.
    """

    async def _check(
        request: Request,
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if user.platform_role == PlatformRole.super_admin:
            return user
        if user.grow_scope is None:
            return user  # Unrestricted

        # Extract grow_id from path params
        grow_id_str = request.path_params.get(grow_id_param)
        if grow_id_str:
            try:
                grow_id = UUID(grow_id_str)
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid grow ID",
                )
            if grow_id not in user.grow_scope:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this grow",
                )
        return user

    return _check


# ─── Legacy guards (backward-compat, delegate to permission system) ───────────


def require_role(*allowed_roles: str):
    """Legacy dependency — maps old role strings to permission checks.

    Maintained for backward compatibility during migration.
    """
    # Map old role sets to appropriate permission level
    _ROLE_MAP = {
        "owner": TenantRole.admin,
        "member": TenantRole.member,
        "viewer": TenantRole.viewer,
    }

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        # Platform super_admins bypass
        if user.platform_role == PlatformRole.super_admin:
            return user

        # Map user's tenant_role to old role string
        if user.tenant_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenant context",
            )

        user_old_role = user.role  # Uses the compat property
        if user_old_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user_old_role}' is not authorized for this action",
            )
        return user

    return _check


async def require_platform_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Legacy: requires super_admin platform role."""
    if user.platform_role != PlatformRole.super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required",
        )
    return user


async def require_support_or_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Legacy: requires support or super_admin platform role."""
    if user.platform_role not in (PlatformRole.super_admin, PlatformRole.support, PlatformRole.readonly_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Support or platform admin access required",
        )
    return user


# ─── Tenant-scoped DB session ─────────────────────────────────────────────────


async def get_tenant_session(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> AsyncSession:
    """Dependency: returns a DB session with RLS tenant context set."""
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active tenant context",
        )
    session = async_session_factory()
    try:
        # SET doesn't support parameterized queries in asyncpg;
        # user.tenant_id is a validated UUID so safe to interpolate.
        tid = str(user.tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid}'"))
        yield session  # type: ignore[misc]
    finally:
        await session.close()
