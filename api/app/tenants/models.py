from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ─── Enums ────────────────────────────────────────────────────────────────────


class PlatformRole(enum.StrEnum):
    """Platform-level roles for cross-tenant access."""

    super_admin = "super_admin"
    support = "support"
    readonly_admin = "readonly_admin"
    user = "user"


class TenantRole(enum.StrEnum):
    """Tenant-level roles assigned per membership."""

    admin = "admin"
    member = "member"
    viewer = "viewer"


class AccountRole(enum.StrEnum):
    """Account-level roles for billing/ownership."""

    owner = "owner"
    billing_admin = "billing_admin"


# ─── Account (billing/ownership umbrella) ─────────────────────────────────────


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_email: Mapped[str | None] = mapped_column(String(255))
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255))
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    # Dunning / grace period
    dunning_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dunning_attempts: Mapped[int | None] = mapped_column(Integer)

    # Account deletion (GDPR)
    deletion_scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    deletion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    members: Mapped[list[AccountMember]] = relationship(back_populates="account", cascade="all, delete-orphan")
    tenants: Mapped[list[Tenant]] = relationship(back_populates="account")


class AccountMember(Base):
    __tablename__ = "account_members"
    __table_args__ = (UniqueConstraint("account_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[AccountRole] = mapped_column(
        Enum(AccountRole, name="account_role", native_enum=True),
        default=AccountRole.owner,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    account: Mapped[Account] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="account_memberships")


# ─── Tenant ────────────────────────────────────────────────────────────────────


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    account: Mapped[Account | None] = relationship(back_populates="tenants")
    memberships: Mapped[list[TenantMembership]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    devices: Mapped[list[Device]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


# ─── Tenant Membership (pivot: user ↔ tenant with role) ───────────────────────


class TenantMembership(Base):
    __tablename__ = "tenant_memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[TenantRole] = mapped_column(
        Enum(TenantRole, name="tenant_role", native_enum=True),
        default=TenantRole.member,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    tenant: Mapped[Tenant] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="tenant_memberships")
    grow_access: Mapped[list[MembershipGrowAccess]] = relationship(
        back_populates="membership", cascade="all, delete-orphan"
    )


# ─── Grow-Level Scoping ───────────────────────────────────────────────────────


class MembershipGrowAccess(Base):
    __tablename__ = "membership_grow_access"
    __table_args__ = (UniqueConstraint("membership_id", "grow_cycle_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant_memberships.id", ondelete="CASCADE"),
        nullable=False,
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    membership: Mapped[TenantMembership] = relationship(back_populates="grow_access")


# ─── User ──────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(255))
    platform_role: Mapped[PlatformRole] = mapped_column(
        Enum(PlatformRole, name="platform_role", native_enum=True),
        default=PlatformRole.user,
        nullable=False,
    )
    auth_provider: Mapped[str] = mapped_column(String(50), default="local")
    auth_provider_id: Mapped[str | None] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    layout_mode: Mapped[str] = mapped_column(String(20), default="standard", nullable=False)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, server_default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    tenant_memberships: Mapped[list[TenantMembership]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    account_memberships: Mapped[list[AccountMember]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    psk_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str | None] = mapped_column(String(255))
    tent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(50), default="paired")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    firmware_version: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    tenant: Mapped[Tenant] = relationship(back_populates="devices")
