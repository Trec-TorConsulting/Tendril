"""Billing domain models — plans, provider configs, usage metering."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ─── Enums ────────────────────────────────────────────────────────────────────


class BillingModel(enum.StrEnum):
    flat = "flat"
    tiered_usage = "tiered_usage"
    pay_as_you_go = "pay_as_you_go"


class PlanSlug(enum.StrEnum):
    free = "free"
    hobby = "hobby"
    pro = "pro"
    commercial = "commercial"
    enterprise = "enterprise"
    dedicated = "dedicated"


class SyncStatus(enum.StrEnum):
    pending = "pending"
    synced = "synced"
    error = "error"


class ProviderType(enum.StrEnum):
    stripe = "stripe"
    paypal = "paypal"
    square = "square"
    paddle = "paddle"


# ─── Payment Provider ─────────────────────────────────────────────────────────


class PaymentProvider(Base):
    __tablename__ = "payment_providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, name="provider_type", native_enum=True), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    config_encrypted: Mapped[bytes] = mapped_column(nullable=False)
    webhook_secret_encrypted: Mapped[bytes | None] = mapped_column(nullable=True)
    supported_methods: Mapped[list[str] | None] = mapped_column(ARRAY(String(50)), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    plan_prices: Mapped[list[BillingPlanPrice]] = relationship(back_populates="provider")


# ─── Billing Plan ─────────────────────────────────────────────────────────────


class BillingPlan(Base):
    __tablename__ = "billing_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    billing_model: Mapped[BillingModel] = mapped_column(
        Enum(BillingModel, name="billing_model_enum", native_enum=True), default=BillingModel.flat
    )
    base_price_cents: Mapped[int] = mapped_column(Integer, default=0)
    annual_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="usd")

    # Feature limits (None = unlimited)
    max_grows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_devices: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_team_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_ai_analyses_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_storage_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_automations: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_integrations: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_journal_entries_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    included_support_tier: Mapped[str] = mapped_column(String(20), default="community")

    # Flexible feature flags
    features_json: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    prices: Mapped[list[BillingPlanPrice]] = relationship(back_populates="plan", cascade="all, delete-orphan")
    overage_rates: Mapped[list[BillingOverageRate]] = relationship(back_populates="plan", cascade="all, delete-orphan")


# ─── Plan ↔ Provider Price Mapping ────────────────────────────────────────────


class BillingPlanPrice(Base):
    __tablename__ = "billing_plan_prices"
    __table_args__ = (UniqueConstraint("plan_id", "provider_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False
    )
    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payment_providers.id", ondelete="CASCADE"), nullable=False
    )
    external_product_id: Mapped[str | None] = mapped_column(String(255))
    external_price_id: Mapped[str | None] = mapped_column(String(255))
    external_annual_price_id: Mapped[str | None] = mapped_column(String(255))
    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus, name="sync_status_enum", native_enum=True), default=SyncStatus.pending
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sync_error: Mapped[str | None] = mapped_column(Text)

    plan: Mapped[BillingPlan] = relationship(back_populates="prices")
    provider: Mapped[PaymentProvider] = relationship(back_populates="plan_prices")


# ─── Overage & PAYG Rates ─────────────────────────────────────────────────────


class BillingOverageRate(Base):
    __tablename__ = "billing_overage_rates"
    __table_args__ = (UniqueConstraint("plan_id", "metric"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False
    )
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    plan: Mapped[BillingPlan] = relationship(back_populates="overage_rates")


class BillingPaygRate(Base):
    __tablename__ = "billing_payg_rates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))


# ─── Usage Tracking ───────────────────────────────────────────────────────────


class BillingUsageRecord(Base):
    __tablename__ = "billing_usage_records"
    __table_args__ = (UniqueConstraint("tenant_id", "metric", "period_start"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("billing_plans.id", ondelete="SET NULL")
    )
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    period_start: Mapped[datetime] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime] = mapped_column(Date, nullable=False)
    reported_to_provider: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
