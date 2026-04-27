from __future__ import annotations

from typing import Annotated
from uuid import UUID

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
)
from app.auth.middleware import CurrentUser, get_current_user
from app.database import get_db
from app.tenants.models import Tenant, User

router = APIRouter()


# ---------- Schemas ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    tenant_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    role: str
    tenant_id: UUID
    email_verified: bool
    is_platform_admin: bool = False
    is_support: bool = False


class VerifyEmailRequest(BaseModel):
    token: str


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    email: EmailStr | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ---------- Helpers ----------

def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _validate_password_strength(password: str) -> None:
    """Enforce enterprise-grade password policy.

    Requirements: min 12 chars, uppercase, lowercase, digit, special character.
    Raises HTTPException on failure.
    """
    import re

    errors: list[str] = []
    if len(password) < 12:
        errors.append("at least 12 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"\d", password):
        errors.append("a digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password):
        errors.append("a special character")
    if errors:
        raise HTTPException(
            status_code=400,
            detail=f"Password must contain {', '.join(errors)}",
        )


def _make_slug(name: str) -> str:
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:100]


# ---------- Endpoints ----------

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    _validate_password_strength(body.password)
    # Check existing email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create tenant
    tenant = Tenant(
        name=body.tenant_name,
        slug=_make_slug(body.tenant_name),
    )
    db.add(tenant)
    await db.flush()

    # Create user
    user = User(
        tenant_id=tenant.id,
        email=body.email,
        password_hash=_hash_password(body.password),
        display_name=body.display_name,
        role="owner",
        auth_provider="local",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate email verification token
    verify_token = create_email_verification_token(user.id)
    # TODO: Send verification email with link containing verify_token
    # For now, log it (in production, send via email service)
    import logging
    logging.getLogger("tendril.auth").info(
        "Email verification token for %s: %s", user.email, verify_token
    )

    return TokenResponse(
        access_token=create_access_token(user.id, tenant.id, user.role),
        refresh_token=create_refresh_token(user.id, tenant.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(
            user.id, user.tenant_id, user.role,
            is_platform_admin=user.is_platform_admin,
            is_support=user.is_support,
        ),
        refresh_token=create_refresh_token(user.id, user.tenant_id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    from jose import JWTError

    try:
        payload = decode_token(body.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(
            user.id, user.tenant_id, user.role,
            is_platform_admin=user.is_platform_admin,
            is_support=user.is_support,
        ),
        refresh_token=create_refresh_token(user.id, user.tenant_id),
    )


@router.get("/me", response_model=UserResponse)
async def me(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.id == user.user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        display_name=db_user.display_name,
        role=db_user.role,
        tenant_id=db_user.tenant_id,
        email_verified=db_user.email_verified,
        is_platform_admin=db_user.is_platform_admin,
        is_support=db_user.is_support,
    )


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user's profile (display name, email)."""
    result = await db.execute(select(User).where(User.id == user.user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.display_name is not None:
        db_user.display_name = body.display_name

    if body.email is not None and body.email != db_user.email:
        # Check uniqueness
        existing = await db.execute(select(User).where(User.email == body.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already in use")
        db_user.email = body.email
        db_user.email_verified = False  # Re-verify new email

    await db.commit()
    await db.refresh(db_user)
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        display_name=db_user.display_name,
        role=db_user.role,
        tenant_id=db_user.tenant_id,
        email_verified=db_user.email_verified,
        is_platform_admin=db_user.is_platform_admin,
        is_support=db_user.is_support,
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change password for current user. Requires current password."""
    result = await db.execute(select(User).where(User.id == user.user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.auth_provider != "local":
        raise HTTPException(status_code=400, detail="Password change not available for OAuth accounts")

    if not db_user.password_hash or not _verify_password(body.current_password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    _validate_password_strength(body.new_password)

    db_user.password_hash = _hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Verify email address using the token sent during registration."""
    from jose import JWTError

    try:
        payload = decode_token(body.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    if payload.get("type") != "email_verify":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_verified:
        return {"message": "Email already verified"}

    user.email_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resend email verification token for the current user."""
    result = await db.execute(select(User).where(User.id == user.user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.email_verified:
        return {"message": "Email already verified"}

    verify_token = create_email_verification_token(db_user.id)
    # TODO: Send verification email
    import logging
    logging.getLogger("tendril.auth").info(
        "Resend verification token for %s: %s", db_user.email, verify_token
    )
    return {"message": "Verification email sent"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Send a password reset token. Always returns 200 to prevent email enumeration."""
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user and user.auth_provider == "local":
        reset_token = create_password_reset_token(user.id)
        # TODO: Send password reset email
        import logging
        logging.getLogger("tendril.auth").info(
            "Password reset token for %s: %s", user.email, reset_token
        )

    # Always return success to prevent email enumeration
    return {"message": "If an account exists with that email, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Reset password using a token from forgot-password."""
    from jose import JWTError

    try:
        payload = decode_token(body.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if payload.get("type") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    _validate_password_strength(body.new_password)
    user.password_hash = _hash_password(body.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}
