"""Nutrition system tables — brands, lines, products, feed charts, additives, recipes.

Revision ID: 0046
Revises: 0045
Create Date: 2026-06-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID

revision = "0046"
down_revision = "0045"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Nutrient Brands ---
    op.create_table(
        "nutrient_brands",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("website", sa.String(500)),
        sa.Column("logo_url", sa.String(1024)),
        sa.Column("country", sa.String(100)),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_nutrient_brands_slug", "nutrient_brands", ["slug"])

    # --- Nutrient Lines ---
    op.create_table(
        "nutrient_lines",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "brand_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_brands.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("line_type", sa.String(50), nullable=False),  # synthetic | organic | hybrid
        sa.Column("part_count", sa.Integer, nullable=False, server_default="3"),
        sa.Column("format", sa.String(50), nullable=False, server_default="'liquid'"),
        sa.Column("difficulty", sa.String(20), nullable=False, server_default="'intermediate'"),
        sa.Column("ph_buffered", sa.Boolean, server_default=sa.text("false")),
        sa.Column("grow_type_slugs", ARRAY(sa.String(100)), nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("brand_id", "slug", name="uq_nutrient_line_brand_slug"),
    )
    op.create_index("ix_nutrient_lines_brand_id", "nutrient_lines", ["brand_id"])

    # --- Nutrient Line Products ---
    op.create_table(
        "nutrient_line_products",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "line_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_lines.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("product_type", sa.String(50), nullable=False),  # base | supplement | booster | flush
        sa.Column("npk", sa.String(30)),
        sa.Column("description", sa.Text),
        sa.Column("usage_notes", sa.Text),
        sa.Column("is_required", sa.Boolean, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("line_id", "slug", name="uq_nutrient_line_product_slug"),
    )
    op.create_index("ix_nutrient_line_products_line_id", "nutrient_line_products", ["line_id"])

    # --- Feed Charts ---
    op.create_table(
        "nutrient_feed_charts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "line_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_lines.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("week_number", sa.Integer, nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("phase_name", sa.String(100), nullable=False),
        sa.Column("doses", JSON, nullable=False),
        sa.Column("target_ec_min", sa.Float),
        sa.Column("target_ec_max", sa.Float),
        sa.Column("target_ph_min", sa.Float),
        sa.Column("target_ph_max", sa.Float),
        sa.Column("target_ppm_500", sa.Float),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("line_id", "week_number", name="uq_feed_chart_line_week"),
    )
    op.create_index("ix_nutrient_feed_charts_line_id", "nutrient_feed_charts", ["line_id"])

    # --- Standalone Additives ---
    op.create_table(
        "nutrient_additives",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "brand_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_brands.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("dose_ml_per_gallon", sa.Float),
        sa.Column("dose_grams_per_gallon", sa.Float),
        sa.Column("when_to_use", sa.Text),
        sa.Column("grow_type_slugs", ARRAY(sa.String(100)), nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("brand_id", "slug", name="uq_nutrient_additive_brand_slug"),
    )
    op.create_index("ix_nutrient_additives_brand_id", "nutrient_additives", ["brand_id"])

    # --- Nutrient Conflicts ---
    op.create_table(
        "nutrient_conflicts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("item_a_type", sa.String(50), nullable=False),
        sa.Column("item_a_slug", sa.String(200), nullable=False),
        sa.Column("item_b_type", sa.String(50), nullable=False),
        sa.Column("item_b_slug", sa.String(200), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("recommendation", sa.Text),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # --- Organic Recipes ---
    op.create_table(
        "organic_recipes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("ingredients", JSON, nullable=False),
        sa.Column("instructions", sa.Text, nullable=False),
        sa.Column("brew_time_hours", sa.Float),
        sa.Column("application_rate", sa.String(200)),
        sa.Column("frequency", sa.String(200)),
        sa.Column("best_for_stages", ARRAY(sa.String(50))),
        sa.Column("grow_type_slugs", ARRAY(sa.String(100)), nullable=False),
        sa.Column("warnings", sa.Text),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_organic_recipes_slug", "organic_recipes", ["slug"])

    # --- Custom Nutrients (tenant-scoped) ---
    op.create_table(
        "custom_nutrients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("nutrient_type", sa.String(50), nullable=False),
        sa.Column("npk", sa.String(30)),
        sa.Column("dose_ml_per_gallon", sa.Float),
        sa.Column("dose_grams_per_gallon", sa.Float),
        sa.Column("ingredients", JSON),
        sa.Column("instructions", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_custom_nutrients_tenant_id", "custom_nutrients", ["tenant_id"])

    # --- Grow Nutrient Profile (user's selection per grow) ---
    op.create_table(
        "grow_nutrient_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "grow_cycle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("primary_line_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_lines.id", ondelete="SET NULL")),
        sa.Column("secondary_line_id", UUID(as_uuid=True), sa.ForeignKey("nutrient_lines.id", ondelete="SET NULL")),
        sa.Column("selected_products", ARRAY(sa.String(100))),
        sa.Column("selected_additives", ARRAY(sa.String(100))),
        sa.Column("selected_recipes", ARRAY(sa.String(100))),
        sa.Column("custom_nutrient_ids", ARRAY(UUID(as_uuid=True))),
        sa.Column("strength_pct", sa.Integer, server_default="100"),
        sa.Column("approach", sa.String(50), server_default="'week_by_week'"),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("grow_cycle_id", name="uq_grow_nutrient_profile_grow"),
    )
    op.create_index("ix_grow_nutrient_profiles_tenant_id", "grow_nutrient_profiles", ["tenant_id"])
    op.create_index("ix_grow_nutrient_profiles_grow_cycle_id", "grow_nutrient_profiles", ["grow_cycle_id"])


def downgrade() -> None:
    op.drop_table("grow_nutrient_profiles")
    op.drop_table("custom_nutrients")
    op.drop_table("organic_recipes")
    op.drop_table("nutrient_conflicts")
    op.drop_table("nutrient_additives")
    op.drop_table("nutrient_feed_charts")
    op.drop_table("nutrient_line_products")
    op.drop_table("nutrient_lines")
    op.drop_table("nutrient_brands")
