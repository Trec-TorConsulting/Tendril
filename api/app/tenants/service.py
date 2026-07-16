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
    "vision_auto_scan": {
        "enabled": True,
        "cadence_minutes": 60,
        "confidence_task_threshold": 0.9,
        "task_cooldown_hours": 12,
    },
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


def get_tenant_coaching_settings(tenant: Tenant) -> dict[str, object]:
    """Return normalized tenant coaching settings with defaults."""
    raw = tenant.coaching_settings if isinstance(tenant.coaching_settings, dict) else {}
    cadence = raw.get("cadence_hours", DEFAULT_COACHING_SETTINGS["cadence_hours"])
    minimum = raw.get("minimum_severity", DEFAULT_COACHING_SETTINGS["minimum_severity"])
    enabled = raw.get("enabled", DEFAULT_COACHING_SETTINGS["enabled"])

    cadence_hours = cadence if isinstance(cadence, int) and 1 <= cadence <= 168 else 24
    minimum_severity = minimum if minimum in {"info", "warning", "critical"} else "info"
    is_enabled = bool(enabled)

    raw_vision = raw.get("vision_auto_scan") if isinstance(raw, dict) else {}
    vision_data = raw_vision if isinstance(raw_vision, dict) else {}

    vision_enabled = bool(vision_data.get("enabled", True))
    cadence_minutes_raw = vision_data.get("cadence_minutes", 60)
    cadence_minutes = (
        cadence_minutes_raw if isinstance(cadence_minutes_raw, int) and 15 <= cadence_minutes_raw <= 1440 else 60
    )

    threshold_raw = vision_data.get("confidence_task_threshold", 0.9)
    if isinstance(threshold_raw, int | float) and 0.5 <= float(threshold_raw) <= 1.0:
        confidence_task_threshold = float(threshold_raw)
    else:
        confidence_task_threshold = 0.9

    cooldown_raw = vision_data.get("task_cooldown_hours", 12)
    task_cooldown_hours = cooldown_raw if isinstance(cooldown_raw, int) and 1 <= cooldown_raw <= 168 else 12

    return {
        "enabled": is_enabled,
        "cadence_hours": cadence_hours,
        "minimum_severity": minimum_severity,
        "vision_auto_scan": {
            "enabled": vision_enabled,
            "cadence_minutes": cadence_minutes,
            "confidence_task_threshold": confidence_task_threshold,
            "task_cooldown_hours": task_cooldown_hours,
        },
    }


async def update_tenant_coaching_settings(
    session: AsyncSession,
    tenant: Tenant,
    *,
    enabled: bool | None = None,
    cadence_hours: int | None = None,
    minimum_severity: str | None = None,
    vision_enabled: bool | None = None,
    vision_cadence_minutes: int | None = None,
    vision_confidence_task_threshold: float | None = None,
    vision_task_cooldown_hours: int | None = None,
) -> dict[str, object]:
    """Apply partial updates to tenant coaching settings and persist."""
    current = get_tenant_coaching_settings(tenant)
    if enabled is not None:
        current["enabled"] = enabled
    if cadence_hours is not None:
        current["cadence_hours"] = cadence_hours
    if minimum_severity is not None:
        current["minimum_severity"] = minimum_severity

    vision_settings = current.get("vision_auto_scan")
    if not isinstance(vision_settings, dict):
        default_vision = DEFAULT_COACHING_SETTINGS["vision_auto_scan"]
        if isinstance(default_vision, dict):
            vision_settings = {
                "enabled": bool(default_vision.get("enabled", True)),
                "cadence_minutes": int(default_vision.get("cadence_minutes", 60)),
                "confidence_task_threshold": float(default_vision.get("confidence_task_threshold", 0.9)),
                "task_cooldown_hours": int(default_vision.get("task_cooldown_hours", 12)),
            }
        else:
            vision_settings = {
                "enabled": True,
                "cadence_minutes": 60,
                "confidence_task_threshold": 0.9,
                "task_cooldown_hours": 12,
            }
    else:
        vision_settings = {
            "enabled": bool(vision_settings.get("enabled", True)),
            "cadence_minutes": int(vision_settings.get("cadence_minutes", 60)),
            "confidence_task_threshold": float(vision_settings.get("confidence_task_threshold", 0.9)),
            "task_cooldown_hours": int(vision_settings.get("task_cooldown_hours", 12)),
        }

    if vision_enabled is not None:
        vision_settings["enabled"] = bool(vision_enabled)
    if vision_cadence_minutes is not None:
        vision_settings["cadence_minutes"] = vision_cadence_minutes
    if vision_confidence_task_threshold is not None:
        vision_settings["confidence_task_threshold"] = float(vision_confidence_task_threshold)
    if vision_task_cooldown_hours is not None:
        vision_settings["task_cooldown_hours"] = vision_task_cooldown_hours

    cadence_value = current.get("cadence_hours", DEFAULT_COACHING_SETTINGS["cadence_hours"])
    normalized_cadence_hours = cadence_value if isinstance(cadence_value, int) else 24

    minimum_value = current.get("minimum_severity", DEFAULT_COACHING_SETTINGS["minimum_severity"])
    normalized_minimum_severity = str(minimum_value)

    tenant.coaching_settings = {
        "enabled": bool(current["enabled"]),
        "cadence_hours": normalized_cadence_hours,
        "minimum_severity": normalized_minimum_severity,
        "vision_auto_scan": vision_settings,
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
