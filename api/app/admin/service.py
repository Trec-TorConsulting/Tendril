"""Platform admin domain service.

Holds the business operations for cross-tenant management used by
super-admins and support staff: tenant lookup/create/update/delete,
user lookup/update/delete, and the platform stats KPI snapshot.

Route handlers in ``app.admin.routes`` are HTTP-only and delegate to
this module.

Conventions match the project standard (PR #192 / #208-#217):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM, dataclasses, or primitives; they never raise
  ``HTTPException`` — lookup misses return ``None`` and validation
  failures raise typed errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tenants.models import Account, PlatformRole, Tenant, TenantMembership, TenantRole, User

# ─────────────────────────────────────────────────────────────────────────────
# Custom errors
# ─────────────────────────────────────────────────────────────────────────────


class TenantSlugTakenError(Exception):
    """Raised when create_tenant gets a slug that's already in use. Route → 409."""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Slug already in use: {slug!r}")


class InvalidPlatformRoleError(Exception):
    """Raised when update_user_role gets a non-enum role string. Route → 400."""

    def __init__(self, value: str) -> None:
        self.value = value
        super().__init__(f"Invalid platform_role: {value!r}")


class SelfDemotionError(Exception):
    """Raised when a super-admin tries to demote themselves. Route → 400."""


class SelfDeleteError(Exception):
    """Raised when an admin tries to delete their own user account. Route → 400."""


# ─────────────────────────────────────────────────────────────────────────────
# Tenants
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TenantRow:
    """Tenant + joined user_count for the admin listing."""

    id: UUID
    name: str
    slug: str
    plan: str
    user_count: int
    created_at: str  # already-formatted ISO string for direct response use


def list_tenants_query() -> Select:
    """Build the (tenant + user_count) listing query; route layer paginates."""
    return (
        select(
            Tenant.id,
            Tenant.name,
            Tenant.slug,
            Tenant.plan,
            Tenant.created_at,
            func.count(TenantMembership.id).label("user_count"),
        )
        .outerjoin(TenantMembership, TenantMembership.tenant_id == Tenant.id)
        .group_by(Tenant.id)
        .order_by(Tenant.created_at.desc())
    )


async def count_tenants(session: AsyncSession) -> int:
    count = (await session.execute(select(func.count(Tenant.id)))).scalar()
    return int(count or 0)


async def list_tenants_page(session: AsyncSession, *, offset: int, limit: int) -> tuple[list[TenantRow], int]:
    """Return ``(rows, total)`` for the admin /tenants listing."""
    total = await count_tenants(session)
    stmt = list_tenants_query().offset(offset).limit(limit)
    raw = (await session.execute(stmt)).all()
    rows = [
        TenantRow(
            id=r.id,
            name=r.name,
            slug=r.slug,
            plan=r.plan,
            user_count=int(r.user_count),
            created_at=r.created_at.isoformat(),
        )
        for r in raw
    ]
    return rows, total


async def get_tenant(session: AsyncSession, tenant_id: UUID) -> Tenant | None:
    return (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()


async def get_tenant_by_slug(session: AsyncSession, slug: str) -> Tenant | None:
    return (await session.execute(select(Tenant).where(Tenant.slug == slug))).scalar_one_or_none()


async def count_tenant_users(session: AsyncSession, tenant_id: UUID) -> int:
    count = (
        await session.execute(select(func.count(TenantMembership.id)).where(TenantMembership.tenant_id == tenant_id))
    ).scalar()
    return int(count or 0)


async def create_tenant(
    session: AsyncSession,
    *,
    name: str,
    slug: str,
    plan: str,
    owner_user_id: UUID | None,
) -> Tenant:
    """Create a tenant (and its account, and optional admin membership).

    Raises :class:`TenantSlugTakenError` when ``slug`` is already in use.
    Returns the new ``Tenant`` row. If ``owner_user_id`` is provided but
    that user doesn't exist, the caller is expected to look it up first
    via :func:`get_user` and 404 — keeping that branch in the route
    means the service can stay declarative.
    """
    if await get_tenant_by_slug(session, slug) is not None:
        raise TenantSlugTakenError(slug)

    account = Account(name=name)
    session.add(account)
    await session.flush()

    tenant = Tenant(name=name, slug=slug, plan=plan, account_id=account.id)
    session.add(tenant)
    await session.flush()

    if owner_user_id is not None:
        session.add(TenantMembership(tenant_id=tenant.id, user_id=owner_user_id, role=TenantRole.admin))

    await session.commit()
    await session.refresh(tenant)
    return tenant


async def update_tenant_plan(session: AsyncSession, tenant: Tenant, *, plan: str) -> Tenant:
    tenant.plan = plan
    await session.commit()
    await session.refresh(tenant)
    return tenant


async def delete_tenant_cascade(session: AsyncSession, tenant: Tenant) -> str:
    """Delete a tenant + its memberships; also delete the parent account
    when no other tenant references it.

    Returns the tenant name for the caller's audit log message.
    """
    tenant_name = tenant.name
    account = await session.get(Account, tenant.account_id) if tenant.account_id else None

    await session.execute(delete(TenantMembership).where(TenantMembership.tenant_id == tenant.id))
    await session.delete(tenant)

    if account is not None:
        other_tenants = (
            await session.execute(
                select(func.count(Tenant.id)).where(Tenant.account_id == account.id, Tenant.id != tenant.id)
            )
        ).scalar()
        if not other_tenants:
            await session.delete(account)

    await session.commit()
    return tenant_name


# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class TenantUserRow:
    """A tenant member + their role + tenant name, for /tenants/{id}/users."""

    user: User
    tenant_role: TenantRole
    tenant_name: str


async def list_tenant_users(session: AsyncSession, tenant_id: UUID) -> list[TenantUserRow]:
    """Members of a single tenant, oldest-first."""
    stmt = (
        select(User, TenantMembership.role, Tenant.name.label("tenant_name"))
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .join(Tenant, Tenant.id == TenantMembership.tenant_id)
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(User.created_at)
    )
    raw = (await session.execute(stmt)).all()
    return [TenantUserRow(user=u, tenant_role=tr, tenant_name=tn) for u, tr, tn in raw]


async def count_users(session: AsyncSession) -> int:
    count = (await session.execute(select(func.count(User.id)))).scalar()
    return int(count or 0)


async def list_users_page(session: AsyncSession, *, offset: int, limit: int) -> tuple[list[User], int]:
    total = await count_users(session)
    stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    users = list((await session.execute(stmt)).scalars().all())
    return users, total


async def get_user(session: AsyncSession, user_id: UUID) -> User | None:
    return (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()


def coerce_platform_role(value: str) -> PlatformRole:
    """Convert a public-API role string to ``PlatformRole``.

    Raises :class:`InvalidPlatformRoleError` for unknown values (route → 400).
    """
    try:
        return PlatformRole(value)
    except ValueError as exc:
        raise InvalidPlatformRoleError(value) from exc


async def update_user_platform_role(
    session: AsyncSession,
    user: User,
    *,
    new_role: PlatformRole,
    actor_user_id: UUID,
) -> User:
    """Set ``user.platform_role`` with the self-demotion safety check.

    Raises :class:`SelfDemotionError` when the actor tries to demote
    themselves out of ``super_admin``.
    """
    if user.id == actor_user_id and new_role != PlatformRole.super_admin:
        raise SelfDemotionError("Cannot remove your own admin access")
    user.platform_role = new_role
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user_cascade(
    session: AsyncSession,
    user: User,
    *,
    actor_user_id: UUID,
) -> str:
    """Delete ``user`` and all their tenant memberships.

    Raises :class:`SelfDeleteError` if the actor targets themselves.
    Returns the deleted email for the caller's audit log message.
    """
    if user.id == actor_user_id:
        raise SelfDeleteError("Cannot delete yourself")
    email = user.email
    await session.execute(delete(TenantMembership).where(TenantMembership.user_id == user.id))
    await session.delete(user)
    await session.commit()
    return email


# ─────────────────────────────────────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class PlatformStats:
    total_tenants: int
    total_users: int
    plans: dict[str, int]


async def compute_platform_stats(session: AsyncSession) -> PlatformStats:
    """Cross-tenant KPI snapshot."""
    total_tenants = await count_tenants(session)
    total_users = await count_users(session)
    plan_counts = (await session.execute(select(Tenant.plan, func.count(Tenant.id)).group_by(Tenant.plan))).all()
    return PlatformStats(
        total_tenants=total_tenants,
        total_users=total_users,
        plans={row[0]: int(row[1]) for row in plan_counts},
    )
