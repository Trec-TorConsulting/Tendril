"""Authentication domain service.

Holds the business operations for password hashing, slug generation,
cookie configuration, token-context resolution (membership + account +
grow scope), and the security-side flows (registration, login,
password change/reset, email verification, tenant switching, signed
URLs). Route handlers in ``app.auth.routes`` are HTTP-only and
delegate to this module.

⚠️ **Security-sensitive.** Every cookie attribute (httponly, secure,
samesite, max_age, domain, path), every constant-time compare, every
\"no email enumeration\" branch, and every token-type check is
load-bearing. The service preserves all of these byte-for-byte from
the previous route-level implementation.

Conventions match the project standard (PR #192 / #208-#219):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM models, dataclasses, or primitives; they never
  raise ``HTTPException`` — lookup misses return ``None`` and domain
  validation failures raise typed errors.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

import bcrypt
from fastapi import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.csrf import generate_csrf_token
from app.tenants.models import (
    AccountMember,
    MembershipGrowAccess,
    TenantMembership,
    User,
)

# Allowed values for the ``layout_mode`` user preference. Single source of
# truth — the route validates against this.
VALID_LAYOUT_MODES: frozenset[str] = frozenset({"beginner", "home", "standard", "pro", "commercial"})

# Allowed top-level user preference keys. The frontend only ever writes
# these; anything else is rejected.
VALID_PREFERENCE_KEYS: frozenset[str] = frozenset(
    {
        "temp_unit",
        "date_format",
        "time_format",
        "timezone",
        "default_grow_id",
        "theme",
        "widget_layout",
        "measurement_system",
        "wind_unit",
        "pressure_unit",
        "week_start",
        "compact_numbers",
        "show_onboarding",
    }
)

# Cookie lifetimes — single source of truth shared with the auth tests
# and any future refresh / rotation code. Kept here so changing one
# value updates every cookie in the same flow.
ACCESS_COOKIE_MAX_AGE_S: int = 15 * 60  # 15 minutes
REFRESH_COOKIE_MAX_AGE_S: int = 7 * 24 * 60 * 60  # 7 days
CSRF_COOKIE_MAX_AGE_S: int = 7 * 24 * 60 * 60  # 7 days (matches refresh)


# ─────────────────────────────────────────────────────────────────────────────
# Typed errors (route layer maps each to a specific HTTP status)
# ─────────────────────────────────────────────────────────────────────────────


class EmailAlreadyRegisteredError(Exception):
    """Raised when registration or profile update hits a duplicate email.

    Route → 409.
    """


class InvalidCredentialsError(Exception):
    """Raised when login or password-change auth fails. Route → 401."""


class InvalidTokenError(Exception):
    """Raised when a JWT is malformed, expired, or the wrong ``type`` for
    its endpoint. Route → 400 (verify-email / reset-password) or 401
    (refresh).
    """


class OAuthAccountError(Exception):
    """Raised when local-only ops (change-password) are attempted on an
    OAuth-provisioned account. Route → 400.
    """


class TenantMembershipMissingError(Exception):
    """Raised by switch-tenant when the caller has no membership in the
    target tenant. Route → 403.
    """


# ─────────────────────────────────────────────────────────────────────────────
# Password + slug helpers
# ─────────────────────────────────────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Bcrypt-hash ``password`` with a fresh salt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time bcrypt verify."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def make_tenant_slug(name: str) -> str:
    """Generate a 100-char-capped slug from ``name``.

    Lowercases, replaces non-[a-z0-9] runs with a single hyphen, trims
    leading/trailing hyphens. Matches the previous route helper
    byte-for-byte so existing tenant slugs stay stable.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug[:100]


# ─────────────────────────────────────────────────────────────────────────────
# Cookie configuration (security-load-bearing)
# ─────────────────────────────────────────────────────────────────────────────


def is_secure() -> bool:
    """Return True when the deployment uses HTTPS (so ``Secure`` cookies
    should be set). ``DOMAIN`` env var being empty or ``localhost``
    means local dev → ``False``.
    """
    return os.environ.get("DOMAIN", "").strip() not in ("", "localhost")


def cookie_domain() -> str | None:
    """Return the parent domain for cross-subdomain cookie sharing, or
    ``None`` for local dev.

    For ``foo.bar.tendrilgrow.com`` the cookie is anchored to
    ``.tendrilgrow.com`` so ``api.`` and ``app.`` can share auth state.
    For a 2-part domain ``tendrilgrow.com`` we still prepend the dot
    (``.tendrilgrow.com``).
    """
    domain = os.environ.get("DOMAIN", "").strip()
    if not domain or domain == "localhost":
        return None
    parts = domain.split(".")
    if len(parts) >= 3:
        return "." + ".".join(parts[-2:])
    if len(parts) == 2:
        return "." + domain
    return None


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> str:
    """Set httpOnly auth cookies and a JS-readable CSRF cookie.

    Returns the CSRF token that was also emitted as ``X-CSRF-Token``
    header. The caller doesn't usually need it but tests assert on it.

    * ``access_token``  — httpOnly, 15 min, scope ``/``
    * ``refresh_token`` — httpOnly, 7 days, scope ``/v1/auth`` (kept
      out of every other request)
    * ``csrf_token``    — JS-readable, 7 days, scope ``/`` (double-
      submit pattern); also mirrored into the ``X-CSRF-Token``
      response header for the immediate response
    """
    secure = is_secure()
    same_site: Literal["lax", "strict", "none"] = "lax"
    domain = cookie_domain()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=ACCESS_COOKIE_MAX_AGE_S,
        path="/",
        domain=domain,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite=same_site,
        max_age=REFRESH_COOKIE_MAX_AGE_S,
        path="/v1/auth",  # never leaked to other endpoints
        domain=domain,
    )
    csrf = generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=csrf,
        httponly=False,  # JS reads this for the double-submit header
        secure=secure,
        samesite=same_site,
        max_age=CSRF_COOKIE_MAX_AGE_S,
        path="/",
        domain=domain,
    )
    response.headers["X-CSRF-Token"] = csrf
    return csrf


def clear_auth_cookies(response: Response) -> None:
    """Clear all auth cookies (logout)."""
    domain = cookie_domain()
    for key in ("access_token", "refresh_token", "csrf_token"):
        response.delete_cookie(key=key, path="/", domain=domain)
    # refresh_token also has a narrower path; delete that too.
    response.delete_cookie(key="refresh_token", path="/v1/auth")


# ─────────────────────────────────────────────────────────────────────────────
# Token-context resolution (membership + account + grow scope)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class UserTokenContext:
    """The aggregated context the JWT issuer needs.

    Returned by :func:`build_user_token_context`. Carries the
    membership row (or ``None`` for users with no tenants yet), the
    parent account id, and the optional grow scope.
    """

    membership: TenantMembership | None
    account_id: UUID | None
    grow_scope: list[UUID] | None


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    return (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()


async def get_first_membership(session: AsyncSession, user_id: UUID) -> TenantMembership | None:
    """Oldest membership for ``user_id`` — the default tenant at login."""
    return (
        await session.execute(
            select(TenantMembership)
            .where(TenantMembership.user_id == user_id)
            .order_by(TenantMembership.created_at)
            .limit(1)
        )
    ).scalar_one_or_none()


async def get_membership_for_tenant(
    session: AsyncSession, *, user_id: UUID, tenant_id: UUID
) -> TenantMembership | None:
    """Membership that pairs ``user_id`` with ``tenant_id``, if any."""
    return (
        await session.execute(
            select(TenantMembership).where(
                TenantMembership.user_id == user_id,
                TenantMembership.tenant_id == tenant_id,
            )
        )
    ).scalar_one_or_none()


async def get_account_id_for_user(session: AsyncSession, user_id: UUID) -> UUID | None:
    """The first account this user belongs to. Returned in JWT ``acct``."""
    return (
        await session.execute(select(AccountMember.account_id).where(AccountMember.user_id == user_id).limit(1))
    ).scalar_one_or_none()


async def get_grow_scope_for_membership(session: AsyncSession, membership_id: UUID) -> list[UUID] | None:
    """The list of grow-cycle ids this membership is restricted to, or
    ``None`` when the membership has unrestricted scope."""
    rows = (
        (
            await session.execute(
                select(MembershipGrowAccess.grow_cycle_id).where(MembershipGrowAccess.membership_id == membership_id)
            )
        )
        .scalars()
        .all()
    )
    return list(rows) if rows else None


async def build_user_token_context(
    session: AsyncSession,
    user_id: UUID,
    *,
    preferred_tenant_id: UUID | None = None,
) -> UserTokenContext:
    """Resolve everything the JWT issuer needs in one place.

    * If ``preferred_tenant_id`` is given, try that tenant's membership
      first; fall back to the oldest membership.
    * Account id is the first ``AccountMember`` for the user.
    * Grow scope is loaded from the chosen membership when it has any
      restricted-access rows.
    """
    membership: TenantMembership | None = None
    if preferred_tenant_id is not None:
        membership = await get_membership_for_tenant(session, user_id=user_id, tenant_id=preferred_tenant_id)
    if membership is None:
        membership = await get_first_membership(session, user_id)

    account_id = await get_account_id_for_user(session, user_id)

    grow_scope: list[UUID] | None = None
    if membership is not None:
        grow_scope = await get_grow_scope_for_membership(session, membership.id)

    return UserTokenContext(membership=membership, account_id=account_id, grow_scope=grow_scope)


# ─────────────────────────────────────────────────────────────────────────────
# Preferences validation (used by /profile)
# ─────────────────────────────────────────────────────────────────────────────


def validate_layout_mode(value: str) -> None:
    """Assert ``value`` is one of :data:`VALID_LAYOUT_MODES`.

    Raises ``ValueError`` with the canonical message the route surfaces
    as a 422 detail.
    """
    if value not in VALID_LAYOUT_MODES:
        raise ValueError(f"Invalid layout_mode. Must be one of: {VALID_LAYOUT_MODES}")


def validate_preference_keys(prefs: dict) -> None:
    """Assert every key in ``prefs`` is in :data:`VALID_PREFERENCE_KEYS`.

    Raises ``ValueError`` listing the invalid keys; route → 422.
    """
    invalid = set(prefs.keys()) - VALID_PREFERENCE_KEYS
    if invalid:
        raise ValueError(f"Invalid preference keys: {invalid}")


def merge_preferences(current: dict | None, updates: dict) -> dict:
    """Shallow-merge ``updates`` into ``current`` (no-None semantics).

    Keys in ``updates`` with value ``None`` are *removed* from the
    merged result (user wants to reset that preference to default).
    Matches previous route behaviour byte-for-byte.
    """
    merged = {**(current or {}), **updates}
    return {k: v for k, v in merged.items() if v is not None}
