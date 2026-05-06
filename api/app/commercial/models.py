"""Commercial tier models — custom grow types, tasks, audit trail, API keys."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

# ---------- Custom Grow Types (6.1-6.2) ----------


class CustomGrowType(Base):
    """Tenant-defined grow type profile (Pro/Commercial only)."""

    __tablename__ = "custom_grow_types"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[dict] = mapped_column(JSON, nullable=False)  # full profile dict matching GROW_TYPE_PROFILES shape
    base_type: Mapped[str | None] = mapped_column(String(100))  # seed template slug (e.g. "dwc")
    submitted_for_review: Mapped[bool] = mapped_column(Boolean, default=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


# ---------- Task Management (6.4) ----------


class Task(Base):
    """Task management — manual or auto-generated grow tasks."""

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high, urgent
    category: Mapped[str | None] = mapped_column(
        String(100)
    )  # water_change, ph_check, ec_check, feeding, defoliation, pest_check, trichome_check, flush, etc.
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, auto, ai
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    grow_cycle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE")
    )
    tent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tents.id"))
    bucket_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buckets.id", ondelete="SET NULL")
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    recurring: Mapped[str | None] = mapped_column(String(50))  # daily, weekly, biweekly, monthly, or null
    recurring_parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    routine: Mapped[str | None] = mapped_column(String(20))  # morning, evening, weekly, biweekly, monthly, on_demand
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- Audit Trail (6.5-6.6) ----------


class AuditLog(Base):
    """Audit trail for user actions with before/after values."""

    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # create, update, delete
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)  # tent, grow, bucket, rule, etc.
    resource_id: Mapped[str] = mapped_column(String(100), nullable=False)
    before_value: Mapped[dict | None] = mapped_column(JSON)
    after_value: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(50))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ---------- API Keys (6.7) ----------


class ApiKey(Base):
    """Tenant-scoped API keys for external integrations."""

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # first 8 chars shown to user
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # bcrypt hash of full key
    scopes: Mapped[str] = mapped_column(String(500), default="read")  # comma-separated: read, write, admin
    last_used: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    @staticmethod
    def generate_key() -> tuple[str, str]:
        """Generate an API key and return (full_key, prefix)."""
        key = f"tnd_{secrets.token_urlsafe(32)}"
        return key, key[:12]
