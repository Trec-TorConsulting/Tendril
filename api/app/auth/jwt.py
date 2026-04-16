from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from app.config import get_settings


def create_access_token(
    user_id: UUID,
    tenant_id: UUID,
    role: str,
    *,
    is_platform_admin: bool = False,
    is_support: bool = False,
) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "role": role,
        "pa": is_platform_admin,
        "sup": is_support,
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID, tenant_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "tid": str(tenant_id),
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
