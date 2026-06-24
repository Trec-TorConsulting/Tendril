"""Authentication API — registration, login, refresh, profile, password reset,
email verification, signed media URLs, tenant switching.

This module is HTTP-only. All cookie handling, password hashing,
slug generation, JWT-context resolution, and preference validation
live in ``app.auth.service``.
"""

from __future__ import annotations

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.jwt import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
)
from app.auth.middleware import CurrentUser, get_current_user
from app.auth.password import validate_password_strength
from app.database import get_db
from app.tenants.models import (
    Account,
    AccountMember,
    AccountRole,
    PlatformRole,
    Tenant,
    TenantMembership,
    TenantRole,
    User,
)

router = APIRouter()
logger = logging.getLogger("tendril.auth")


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
    token_type: str = "bearer"  # noqa: S105


class RefreshRequest(BaseModel):
    refresh_token: str = ""


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str | None
    role: str
    tenant_id: UUID | None
    email_verified: bool
    is_platform_admin: bool = False
    is_support: bool = False
    platform_role: str = "user"
    tenant_role: str | None = None
    account_id: UUID | None = None
    layout_mode: str = "standard"
    preferences: dict = {}


class VerifyEmailRequest(BaseModel):
    token: str


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    email: EmailStr | None = None
    layout_mode: str | None = None
    preferences: dict | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class SwitchTenantRequest(BaseModel):
    tenant_id: UUID


# ---------- Helpers ----------


def _user_response_from(db_user: User, *, ctx: CurrentUser) -> UserResponse:
    """Build the standard UserResponse from a fetched ORM row + the JWT ctx."""
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        display_name=db_user.display_name,
        role=ctx.role,
        tenant_id=ctx.tenant_id,
        email_verified=db_user.email_verified,
        is_platform_admin=ctx.is_platform_admin,
        is_support=ctx.is_support,
        platform_role=db_user.platform_role.value,
        tenant_role=ctx.tenant_role.value if ctx.tenant_role else None,
        account_id=ctx.account_id,
        layout_mode=db_user.layout_mode,
        preferences=db_user.preferences or {},
    )


def _mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    masked_local = (local[:1] + "***") if local else "***"
    return f"{masked_local}@{domain}"


def _client_ip(request: Request | None) -> str:
    if request is None:
        return "-"
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "-"


# ---------- Endpoints ----------


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, db: Annotated[AsyncSession, Depends(get_db)]):
    """Register a new user and create their account, tenant, and memberships."""
    validate_password_strength(body.password)

    if await service.get_user_by_email(db, body.email) is not None:
        logger.warning(
            "Registration rejected: email already registered",
            extra={"action": "auth_register", "outcome": "conflict", "email": _mask_email(body.email)},
        )
        raise HTTPException(status_code=409, detail="Email already registered")

    # Account → tenant → user → memberships, all atomic.
    account = Account(name=body.tenant_name, billing_email=body.email)
    db.add(account)
    await db.flush()

    tenant = Tenant(
        name=body.tenant_name,
        slug=service.make_tenant_slug(body.tenant_name),
        account_id=account.id,
    )
    db.add(tenant)
    await db.flush()

    user = User(
        email=body.email,
        password_hash=service.hash_password(body.password),
        display_name=body.display_name,
        platform_role=PlatformRole.user,
        auth_provider="local",
    )
    db.add(user)
    await db.flush()

    db.add(AccountMember(account_id=account.id, user_id=user.id, role=AccountRole.owner))
    db.add(TenantMembership(tenant_id=tenant.id, user_id=user.id, role=TenantRole.admin))
    await db.commit()
    await db.refresh(user)

    # Seed system-default critical alert rules (NFT pump-failure, DWC
    # pythium-risk, coco runoff-EC, …) for every grow type. Tenants can
    # later disable or retune these via the standard rule CRUD endpoints.
    from app.automation.service import seed_system_alert_rules

    await seed_system_alert_rules(db, tenant.id)

    verify_token = create_email_verification_token(user.id)
    from app.auth.email import send_verification_email

    await send_verification_email(user.email, verify_token)

    access = create_access_token(
        user.id,
        platform_role=user.platform_role.value,
        tenant_id=tenant.id,
        tenant_role=TenantRole.admin.value,
        account_id=account.id,
    )
    refresh = create_refresh_token(user.id)
    service.set_auth_cookies(response, access, refresh)

    logger.info(
        "User registered",
        extra={
            "action": "auth_register",
            "outcome": "success",
            "tenant_id": str(tenant.id),
            "user_id": str(user.id),
        },
    )

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: Annotated[AsyncSession, Depends(get_db)]):
    """Authenticate with email and password, returning JWT tokens."""
    user = await service.get_user_by_email(db, body.email)
    if user is None or not user.password_hash or not service.verify_password(body.password, user.password_hash):
        logger.warning(
            "Login failed: invalid credentials",
            extra={
                "action": "auth_login",
                "outcome": "denied",
                "email": _mask_email(body.email),
            },
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    ctx = await service.build_user_token_context(db, user.id)

    access = create_access_token(
        user.id,
        platform_role=user.platform_role.value,
        tenant_id=ctx.membership.tenant_id if ctx.membership else None,
        tenant_role=ctx.membership.role.value if ctx.membership else None,
        grow_scope=ctx.grow_scope,
        account_id=ctx.account_id,
    )
    refresh = create_refresh_token(user.id)
    service.set_auth_cookies(response, access, refresh)

    logger.info(
        "Login succeeded",
        extra={
            "action": "auth_login",
            "outcome": "success",
            "user_id": str(user.id),
            "tenant_id": str(ctx.membership.tenant_id) if ctx.membership else "-",
        },
    )

    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    body: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Refresh an expired access token using a valid refresh token."""
    raw_token = body.refresh_token or request.cookies.get("refresh_token", "")
    if not raw_token:
        logger.warning(
            "Refresh failed: token missing",
            extra={"action": "auth_refresh", "outcome": "denied", "client_ip": _client_ip(request)},
        )
        raise HTTPException(status_code=401, detail="Refresh token required")

    try:
        payload = decode_token(raw_token)
    except JWTError as exc:
        logger.warning(
            "Refresh failed: invalid token",
            extra={"action": "auth_refresh", "outcome": "denied", "client_ip": _client_ip(request)},
        )
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    if payload.get("type") != "refresh":
        logger.warning(
            "Refresh failed: invalid token type",
            extra={"action": "auth_refresh", "outcome": "denied", "client_ip": _client_ip(request)},
        )
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    user = await service.get_user(db, user_id)
    if user is None:
        logger.warning(
            "Refresh failed: user not found",
            extra={"action": "auth_refresh", "outcome": "denied", "user_id": str(user_id)},
        )
        raise HTTPException(status_code=401, detail="User not found")

    # Prefer the tenant the user was already on (carried in the prior
    # access-token cookie) so refresh doesn't accidentally drop them
    # back to their first tenant.
    prev_tid: UUID | None = None
    prev_access = request.cookies.get("access_token")
    if prev_access:
        try:
            prev_payload = decode_token(prev_access)
            if prev_payload.get("tid"):
                prev_tid = UUID(prev_payload["tid"])
        except (JWTError, ValueError, KeyError):
            pass

    ctx = await service.build_user_token_context(db, user.id, preferred_tenant_id=prev_tid)

    access = create_access_token(
        user.id,
        platform_role=user.platform_role.value,
        tenant_id=ctx.membership.tenant_id if ctx.membership else None,
        tenant_role=ctx.membership.role.value if ctx.membership else None,
        grow_scope=ctx.grow_scope,
        account_id=ctx.account_id,
    )
    new_refresh = create_refresh_token(user.id)
    service.set_auth_cookies(response, access, new_refresh)

    logger.info(
        "Refresh succeeded",
        extra={
            "action": "auth_refresh",
            "outcome": "success",
            "user_id": str(user.id),
            "tenant_id": str(ctx.membership.tenant_id) if ctx.membership else "-",
        },
    )

    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
async def logout(response: Response):
    """Clear auth cookies to log out."""
    service.clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def me(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the current authenticated user's profile."""
    db_user = await service.get_user(db, user.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_response_from(db_user, ctx=user)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update current user's profile (display name, email, layout mode, preferences)."""
    db_user = await service.get_user(db, user.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if body.display_name is not None:
        db_user.display_name = body.display_name

    if body.email is not None and body.email != db_user.email:
        if await service.get_user_by_email(db, body.email) is not None:
            raise HTTPException(status_code=409, detail="Email already in use")
        db_user.email = body.email
        db_user.email_verified = False  # Re-verify the new email

    if body.layout_mode is not None:
        try:
            service.validate_layout_mode(body.layout_mode)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        db_user.layout_mode = body.layout_mode

    if body.preferences is not None:
        try:
            service.validate_preference_keys(body.preferences)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        db_user.preferences = service.merge_preferences(db_user.preferences, body.preferences)

    await db.commit()
    await db.refresh(db_user)
    return _user_response_from(db_user, ctx=user)


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change password for current user. Requires current password."""
    db_user = await service.get_user(db, user.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.auth_provider != "local":
        raise HTTPException(status_code=400, detail="Password change not available for OAuth accounts")

    if not db_user.password_hash or not service.verify_password(body.current_password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    validate_password_strength(body.new_password)
    db_user.password_hash = service.hash_password(body.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.post("/verify-email")
async def verify_email(body: VerifyEmailRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Verify email address using the token sent during registration."""
    try:
        payload = decode_token(body.token)
    except JWTError as exc:
        logger.warning(
            "Email verification failed: invalid token",
            extra={"action": "auth_verify_email", "outcome": "denied"},
        )
        raise HTTPException(status_code=400, detail="Invalid or expired verification token") from exc

    if payload.get("type") != "email_verify":
        logger.warning(
            "Email verification failed: invalid token type",
            extra={"action": "auth_verify_email", "outcome": "denied"},
        )
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    user = await service.get_user(db, user_id)
    if user is None:
        logger.warning(
            "Email verification failed: user not found",
            extra={"action": "auth_verify_email", "outcome": "denied", "user_id": str(user_id)},
        )
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_verified:
        return {"message": "Email already verified"}

    user.email_verified = True
    await db.commit()
    logger.info(
        "Email verified",
        extra={"action": "auth_verify_email", "outcome": "success", "user_id": str(user.id)},
    )
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resend email verification token for the current user."""
    db_user = await service.get_user(db, user.user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.email_verified:
        return {"message": "Email already verified"}

    verify_token = create_email_verification_token(db_user.id)
    from app.auth.email import send_verification_email

    await send_verification_email(db_user.email, verify_token)
    return {"message": "Verification email sent"}


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Send a password reset token. Always returns 200 to prevent email enumeration."""
    user = await service.get_user_by_email(db, body.email)

    if user is not None and user.auth_provider == "local":
        reset_token = create_password_reset_token(user.id)
        from app.auth.email import send_password_reset_email

        await send_password_reset_email(user.email, reset_token)

    logger.info(
        "Password reset requested",
        extra={"action": "auth_forgot_password", "outcome": "accepted", "email": _mask_email(body.email)},
    )

    # Always return success — must not leak whether the email exists.
    return {"message": "If an account exists with that email, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """Reset password using a token from forgot-password."""
    try:
        payload = decode_token(body.token)
    except JWTError as exc:
        logger.warning(
            "Password reset failed: invalid token",
            extra={"action": "auth_reset_password", "outcome": "denied"},
        )
        raise HTTPException(status_code=400, detail="Invalid or expired reset token") from exc

    if payload.get("type") != "password_reset":
        logger.warning(
            "Password reset failed: invalid token type",
            extra={"action": "auth_reset_password", "outcome": "denied"},
        )
        raise HTTPException(status_code=400, detail="Invalid token type")

    user_id = UUID(payload["sub"])
    user = await service.get_user(db, user_id)
    if user is None:
        logger.warning(
            "Password reset failed: user not found",
            extra={"action": "auth_reset_password", "outcome": "denied", "user_id": str(user_id)},
        )
        raise HTTPException(status_code=404, detail="User not found")

    validate_password_strength(body.new_password)
    user.password_hash = service.hash_password(body.new_password)
    await db.commit()
    logger.info(
        "Password reset succeeded",
        extra={"action": "auth_reset_password", "outcome": "success", "user_id": str(user.id)},
    )
    return {"message": "Password reset successfully"}


# ---------- Signed Media URLs ----------


class SignUrlRequest(BaseModel):
    url: str


class SignUrlResponse(BaseModel):
    signed_url: str


@router.post("/sign-url", response_model=SignUrlResponse)
async def create_signed_url(
    body: SignUrlRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Generate a short-lived HMAC-signed URL for media endpoints (camera, QR, photos)."""
    from app.auth.signed_url import sign_url

    return SignUrlResponse(signed_url=sign_url(body.url, str(user.tenant_id)))


@router.post("/switch-tenant", response_model=TokenResponse)
async def switch_tenant(
    body: SwitchTenantRequest,
    response: Response,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Switch the active tenant context. Issues a new access token scoped to the target tenant."""
    target_tid = body.tenant_id

    if user.platform_role == PlatformRole.super_admin:
        # Platform super_admins can switch to any tenant
        from sqlalchemy import select

        tenant_exists = (await db.execute(select(Tenant).where(Tenant.id == target_tid))).scalar_one_or_none()
        if tenant_exists is None:
            raise HTTPException(status_code=404, detail="Tenant not found")

        membership = await service.get_membership_for_tenant(db, user_id=user.user_id, tenant_id=target_tid)
        tenant_role = membership.role.value if membership else TenantRole.admin.value
        grow_scope: list[UUID] | None = None
    else:
        # Regular user: must have membership
        membership = await service.get_membership_for_tenant(db, user_id=user.user_id, tenant_id=target_tid)
        if membership is None:
            logger.warning(
                "Tenant switch denied: no membership",
                extra={
                    "action": "auth_switch_tenant",
                    "outcome": "denied",
                    "user_id": str(user.user_id),
                    "tenant_id": str(target_tid),
                },
            )
            raise HTTPException(status_code=403, detail="No membership in target tenant")
        tenant_role = membership.role.value
        grow_scope = await service.get_grow_scope_for_membership(db, membership.id)

    account_id = await service.get_account_id_for_user(db, user.user_id)
    db_user = await service.get_user(db, user.user_id)
    assert db_user is not None  # caller already authenticated via get_current_user

    access = create_access_token(
        user.user_id,
        platform_role=db_user.platform_role.value,
        tenant_id=target_tid,
        tenant_role=tenant_role,
        grow_scope=grow_scope,
        account_id=account_id,
    )
    refresh = create_refresh_token(user.user_id)
    service.set_auth_cookies(response, access, refresh)

    logger.info(
        "Tenant switched",
        extra={
            "action": "auth_switch_tenant",
            "outcome": "success",
            "user_id": str(user.user_id),
            "tenant_id": str(target_tid),
        },
    )

    return TokenResponse(access_token=access, refresh_token=refresh)
