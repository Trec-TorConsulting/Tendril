"""Nutrition module — brands, lines, products, feed charts, additives, organic recipes, and user profiles."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ─── Nutrient Brands ───────────────────────────────────────────────────────────


class NutrientBrand(Base):
    """A nutrient manufacturer (e.g., General Hydroponics, Fox Farm, Canna)."""

    __tablename__ = "nutrient_brands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(500))
    logo_url: Mapped[str | None] = mapped_column(String(1024))
    country: Mapped[str | None] = mapped_column(String(100))
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    lines: Mapped[list[NutrientLine]] = relationship(back_populates="brand", cascade="all, delete-orphan")
    additives: Mapped[list[NutrientAdditive]] = relationship(back_populates="brand", cascade="all, delete-orphan")


# ─── Nutrient Lines ────────────────────────────────────────────────────────────


class NutrientLine(Base):
    """A product line within a brand (e.g., Flora Series, Trio, Coco A+B)."""

    __tablename__ = "nutrient_lines"
    __table_args__ = (UniqueConstraint("brand_id", "slug", name="uq_nutrient_line_brand_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_brands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    line_type: Mapped[str] = mapped_column(String(50), nullable=False)  # synthetic | organic | hybrid
    part_count: Mapped[int] = mapped_column(Integer, nullable=False, default=3)  # 1-part, 2-part, 3-part
    format: Mapped[str] = mapped_column(String(50), nullable=False, default="liquid")  # liquid | powder | dry_amendment
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="intermediate")  # beginner | intermediate | advanced
    ph_buffered: Mapped[bool] = mapped_column(Boolean, default=False)  # e.g., AN pH Perfect
    grow_type_slugs: Mapped[list] = mapped_column(ARRAY(String(100)), nullable=False)  # compatible grow types
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    brand: Mapped[NutrientBrand] = relationship(back_populates="lines")
    products: Mapped[list[NutrientProduct]] = relationship(back_populates="line", cascade="all, delete-orphan")
    feed_charts: Mapped[list[NutrientFeedChart]] = relationship(back_populates="line", cascade="all, delete-orphan")


# ─── Nutrient Products ─────────────────────────────────────────────────────────


class NutrientProduct(Base):
    """An individual product within a line (e.g., FloraMicro, FloraGro)."""

    __tablename__ = "nutrient_products"
    __table_args__ = (UniqueConstraint("line_id", "slug", name="uq_nutrient_product_line_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_lines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)  # base | supplement | booster | flush
    npk: Mapped[str | None] = mapped_column(String(30))  # e.g., "5-0-1"
    description: Mapped[str | None] = mapped_column(Text)
    usage_notes: Mapped[str | None] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)  # required vs optional in the line
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    line: Mapped[NutrientLine] = relationship(back_populates="products")


# ─── Feed Charts (Week-by-Week Dosing) ────────────────────────────────────────


class NutrientFeedChart(Base):
    """Week-by-week dosing for a nutrient line, organized by stage."""

    __tablename__ = "nutrient_feed_charts"
    __table_args__ = (
        UniqueConstraint("line_id", "week_number", name="uq_feed_chart_line_week"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_lines.id", ondelete="CASCADE"), nullable=False, index=True
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-based
    stage: Mapped[str] = mapped_column(String(50), nullable=False)  # seedling | vegetative | flowering | flush
    phase_name: Mapped[str] = mapped_column(String(100), nullable=False)  # "Early Veg", "Peak Bloom", etc.
    # Dosing per product: [{product_slug, ml_per_gallon OR grams_per_gallon, strength_pct}]
    doses: Mapped[list] = mapped_column(JSON, nullable=False)
    target_ec_min: Mapped[float | None] = mapped_column(Float)
    target_ec_max: Mapped[float | None] = mapped_column(Float)
    target_ph_min: Mapped[float | None] = mapped_column(Float)
    target_ph_max: Mapped[float | None] = mapped_column(Float)
    target_ppm_500: Mapped[float | None] = mapped_column(Float)  # PPM on 500 scale
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    line: Mapped[NutrientLine] = relationship(back_populates="feed_charts")


# ─── Standalone Additives ──────────────────────────────────────────────────────


class NutrientAdditive(Base):
    """Standalone additives that work alongside any nutrient brand (CalMag, Hydroguard, etc.)."""

    __tablename__ = "nutrient_additives"
    __table_args__ = (UniqueConstraint("brand_id", "slug", name="uq_nutrient_additive_brand_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_brands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # calmag | silica | enzyme | microbe | pk_booster | root_enhancer | flush
    description: Mapped[str | None] = mapped_column(Text)
    dose_ml_per_gallon: Mapped[float | None] = mapped_column(Float)
    dose_grams_per_gallon: Mapped[float | None] = mapped_column(Float)
    when_to_use: Mapped[str | None] = mapped_column(Text)
    grow_type_slugs: Mapped[list] = mapped_column(ARRAY(String(100)), nullable=False)  # compatible grow types
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    brand: Mapped[NutrientBrand] = relationship(back_populates="additives")


# ─── Nutrient Conflicts ────────────────────────────────────────────────────────


class NutrientConflict(Base):
    """Known conflicts between products/additives (e.g., Hydroguard + H2O2)."""

    __tablename__ = "nutrient_conflicts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    item_a_type: Mapped[str] = mapped_column(String(50), nullable=False)  # product | additive | recipe
    item_a_slug: Mapped[str] = mapped_column(String(200), nullable=False)
    item_b_type: Mapped[str] = mapped_column(String(50), nullable=False)
    item_b_slug: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # warning | critical
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ─── Organic Recipes ───────────────────────────────────────────────────────────


class OrganicRecipe(Base):
    """Homemade/organic recipes (compost teas, amendments, KNF, etc.)."""

    __tablename__ = "organic_recipes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # compost_tea | dry_amendment | knf | foliar | top_dress | ferment
    description: Mapped[str | None] = mapped_column(Text)
    ingredients: Mapped[list] = mapped_column(JSON, nullable=False)  # [{name, amount, unit, notes}]
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    brew_time_hours: Mapped[float | None] = mapped_column(Float)
    application_rate: Mapped[str | None] = mapped_column(String(200))  # e.g., "1 cup per gallon"
    frequency: Mapped[str | None] = mapped_column(String(200))  # e.g., "Every 2 weeks in veg"
    best_for_stages: Mapped[list | None] = mapped_column(ARRAY(String(50)))  # seedling, vegetative, flowering
    grow_type_slugs: Mapped[list] = mapped_column(ARRAY(String(100)), nullable=False)
    warnings: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ─── User / Tenant Custom Nutrients ───────────────────────────────────────────


class CustomNutrient(Base):
    """User-defined custom nutrients or homemade recipes (tenant-scoped)."""

    __tablename__ = "custom_nutrients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    nutrient_type: Mapped[str] = mapped_column(String(50), nullable=False)  # liquid | powder | dry_amendment | tea | custom
    npk: Mapped[str | None] = mapped_column(String(30))
    dose_ml_per_gallon: Mapped[float | None] = mapped_column(Float)
    dose_grams_per_gallon: Mapped[float | None] = mapped_column(Float)
    ingredients: Mapped[list | None] = mapped_column(JSON)  # for homemade: [{name, amount, unit}]
    instructions: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


# ─── Grow Nutrient Profile (User's selection per grow) ─────────────────────────


class GrowNutrientProfile(Base):
    """Links a grow cycle to the user's chosen nutrient line(s), additives, and custom nutrients."""

    __tablename__ = "grow_nutrient_profiles"
    __table_args__ = (UniqueConstraint("grow_cycle_id", name="uq_grow_nutrient_profile_grow"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    grow_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Primary nutrient line
    primary_line_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_lines.id", ondelete="SET NULL")
    )
    # Secondary line (for mix-and-match, e.g., base from one brand + bloom booster from another)
    secondary_line_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nutrient_lines.id", ondelete="SET NULL")
    )
    # Selected products from the line (user may not own all) — slugs
    selected_products: Mapped[list | None] = mapped_column(ARRAY(String(100)))
    # Selected standalone additives — slugs
    selected_additives: Mapped[list | None] = mapped_column(ARRAY(String(100)))
    # Selected organic recipes — slugs
    selected_recipes: Mapped[list | None] = mapped_column(ARRAY(String(100)))
    # Custom nutrient IDs
    custom_nutrient_ids: Mapped[list | None] = mapped_column(ARRAY(UUID(as_uuid=True)))
    # Strength override (percentage, e.g., 75 = 75% of chart values)
    strength_pct: Mapped[int] = mapped_column(Integer, default=100)
    # Feeding approach preference
    approach: Mapped[str] = mapped_column(String(50), default="week_by_week")  # week_by_week | stage_based
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
