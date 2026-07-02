"""Tenants domain service.

Holds the business operations for tenant lookups, tenant-membership
management, member CRUD, and the legacy ↔ ``TenantRole`` role mapping
used by the public API for backward compatibility.

Route handlers in ``app.tenants.routes`` are HTTP-only — request parsing,
response shaping, ``HTTPException`` raising — and delegate to this module.

Conventions match the project standard (PR #192 / #208 / #209):

* The first positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances, dataclasses, or primitives;
  they never raise ``HTTPException`` — lookup misses return ``None`` and
  domain validation failures raise typed errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenants.models import PlatformRole, Tenant, TenantMembership, TenantRole, User

DEFAULT_COACHING_SETTINGS = {
    "enabled": True,
    "cadence_hours": 24,
    "minimum_severity": "info",
}

# ─────────────────────────────────────────────────────────────────────────────
# Role mapping
# ─────────────────────────────────────────────────────────────────────────────

# The public API exposes legacy role names (``owner``/``member``/``viewer``)
# while the database column is the ``TenantRole`` enum
# (``admin``/``member``/``viewer``). Keep the two helpers below as the *only*
# place that mapping lives.

_LEGACY_TO_DB: dict[str, TenantRole] = {
    "owner": TenantRole.admin,
    "member": TenantRole.member,
    "viewer": TenantRole.viewer,
}


def tenant_role_to_legacy(tr: TenantRole) -> str:
    """Convert a ``TenantRole`` enum to the legacy role string."""
    if tr == TenantRole.admin:
        return "owner"
    return tr.value


def legacy_to_tenant_role(role: str) -> TenantRole:
    """Convert a legacy role string to ``TenantRole``.

    Raises ``ValueError`` for unknown roles; the route layer maps this
    to HTTP 400 via its own role-set validation.
    """
    try:
        return _LEGACY_TO_DB[role]
    except KeyError as exc:
        raise ValueError(f"Invalid role: {role}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Tenant lookups
# ─────────────────────────────────────────────────────────────────────────────


async def get_tenant(session: AsyncSession, tenant_id: UUID) -> Tenant | None:
    """Fetch a tenant by id; route layer maps ``None`` to HTTP 404."""
    result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def update_tenant(
    session: AsyncSession,
    tenant: Tenant,
    *,
    name: str | None = None,
) -> Tenant:
    """Apply tenant updates and commit."""
    if name is not None:
        tenant.name = name
    await session.commit()
    await session.refresh(tenant)
    return tenant


def get_tenant_coaching_settings(tenant: Tenant) -> dict[str, bool | int | str]:
    """Return normalized tenant coaching settings with defaults."""
    raw = tenant.coaching_settings if isinstance(tenant.coaching_settings, dict) else {}
    cadence = raw.get("cadence_hours", DEFAULT_COACHING_SETTINGS["cadence_hours"])
    minimum = raw.get("minimum_severity", DEFAULT_COACHING_SETTINGS["minimum_severity"])
    enabled = raw.get("enabled", DEFAULT_COACHING_SETTINGS["enabled"])

    cadence_hours = cadence if isinstance(cadence, int) and 1 <= cadence <= 168 else 24
    minimum_severity = minimum if minimum in {"info", "warning", "critical"} else "info"
    is_enabled = bool(enabled)

    return {
        "enabled": is_enabled,
        "cadence_hours": cadence_hours,
        "minimum_severity": minimum_severity,
    }


async def update_tenant_coaching_settings(
    session: AsyncSession,
    tenant: Tenant,
    *,
    enabled: bool | None = None,
    cadence_hours: int | None = None,
    minimum_severity: str | None = None,
) -> dict[str, bool | int | str]:
    """Apply partial updates to tenant coaching settings and persist."""
    current = get_tenant_coaching_settings(tenant)
    if enabled is not None:
        current["enabled"] = enabled
    if cadence_hours is not None:
        current["cadence_hours"] = cadence_hours
    if minimum_severity is not None:
        current["minimum_severity"] = minimum_severity

    tenant.coaching_settings = {
        "enabled": bool(current["enabled"]),
        "cadence_hours": int(current["cadence_hours"]),
        "minimum_severity": str(current["minimum_severity"]),
    }
    await session.commit()
    await session.refresh(tenant)
    return get_tenant_coaching_settings(tenant)


# ─────────────────────────────────────────────────────────────────────────────
# Members
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class MemberRow:
    """A tenant member joined with their ``TenantRole``."""

    user: User
    role: TenantRole


async def list_members_page(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    offset: int,
    limit: int,
) -> tuple[list[MemberRow], int]:
    """Return ``(rows, total)`` for a paginated members listing.

    The route layer can't reuse the generic ``paginate`` helper because
    the listing is a join over ``User`` + ``TenantMembership.role``;
    this helper isolates the manual pagination + count in the service.
    """
    count_stmt = select(func.count(TenantMembership.id)).where(TenantMembership.tenant_id == tenant_id)
    total = (await session.execute(count_stmt)).scalar() or 0

    stmt = (
        select(User, TenantMembership.role)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(User.created_at)
        .offset(offset)
        .limit(limit)
    )
    raw = (await session.execute(stmt)).all()
    rows = [MemberRow(user=u, role=tr) for u, tr in raw]
    return rows, int(total)


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_membership(session: AsyncSession, *, tenant_id: UUID, user_id: UUID) -> TenantMembership | None:
    """Fetch the membership row joining a user to a tenant; ``None`` if absent."""
    result = await session.execute(
        select(TenantMembership).where(
            TenantMembership.user_id == user_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


def hash_password(plaintext: str) -> str:
    """Hash a password with bcrypt (default cost)."""
    return bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()


async def create_member(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    email: str,
    password: str,
    display_name: str | None,
    role: TenantRole,
) -> User:
    """Create a User + TenantMembership pair and commit.

    Caller is responsible for password-strength validation and any audit
    record write (which usually wants the request context).
    """
    new_user = User(
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        platform_role=PlatformRole.user,
        auth_provider="local",
    )
    session.add(new_user)
    await session.flush()

    session.add(
        TenantMembership(
            tenant_id=tenant_id,
            user_id=new_user.id,
            role=role,
        )
    )
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def update_membership_role(
    session: AsyncSession,
    membership: TenantMembership,
    role: TenantRole,
) -> TenantMembership:
    membership.role = role
    await session.commit()
    return membership


async def delete_membership(session: AsyncSession, membership: TenantMembership) -> None:
    await session.delete(membership)
    await session.commit()
