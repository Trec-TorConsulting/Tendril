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
from app.database import async_session_factory

_bearer = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str  # owner | member | viewer
    is_platform_admin: bool = False
    is_support: bool = False

    model_config = {"frozen": True}


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
    return CurrentUser(
        user_id=UUID(payload["sub"]),
        tenant_id=UUID(payload["tid"]),
        role=payload["role"],
        is_platform_admin=payload.get("pa", False),
        is_support=payload.get("sup", False),
    )


def require_role(*allowed_roles: str):
    """Dependency that enforces RBAC. Usage: Depends(require_role("owner", "member"))"""

    async def _check(
        user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        # Platform admins bypass tenant role checks
        if user.is_platform_admin:
            return user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user.role}' is not authorized for this action",
            )
        return user

    return _check


async def require_platform_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Dependency: requires platform admin flag."""
    if not user.is_platform_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required",
        )
    return user


async def require_support_or_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Dependency: requires support or platform admin flag."""
    if not user.is_platform_admin and not user.is_support:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Support or platform admin access required",
        )
    return user


async def get_tenant_session(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> AsyncSession:
    """Dependency: returns a DB session with RLS tenant context set."""
    session = async_session_factory()
    try:
        # SET doesn't support parameterized queries in asyncpg;
        # user.tenant_id is a validated UUID so safe to interpolate.
        tid = str(user.tenant_id)
        await session.execute(text(f"SET app.current_tenant = '{tid}'"))
        yield session  # type: ignore[misc]
    finally:
        await session.close()
