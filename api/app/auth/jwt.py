from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.config import get_settings


def create_access_token(
    user_id: UUID,
    *,
    platform_role: str = "user",
    tenant_id: UUID | None = None,
    tenant_role: str | None = None,
    grow_scope: list[UUID] | None = None,
    account_id: UUID | None = None,
) -> str:
    """Create a new-format access token with enterprise RBAC claims.

    Claims:
      sub  - user ID
      pr   - platform role (super_admin|support|readonly_admin|user)
      tid  - active tenant ID (optional)
      tr   - tenant role for active tenant (admin|member|viewer)
      gs   - grow scope (list of grow UUIDs, or null for unrestricted)
      aid  - account ID owning active tenant
      type - "access"
      exp  - expiration
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict = {
        "sub": str(user_id),
        "pr": platform_role,
        "type": "access",
        "exp": expire,
    }
    if tenant_id is not None:
        payload["tid"] = str(tenant_id)
    if tenant_role is not None:
        payload["tr"] = tenant_role
    if grow_scope is not None:
        payload["gs"] = [str(g) for g in grow_scope]
    if account_id is not None:
        payload["aid"] = str(account_id)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID) -> str:
    """Create a refresh token (tenant-agnostic)."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_email_verification_token(user_id: UUID) -> str:
    """Create a short-lived token for email verification (24h)."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "email_verify",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_password_reset_token(user_id: UUID) -> str:
    """Create a short-lived token for password reset (1h)."""
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "password_reset",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
