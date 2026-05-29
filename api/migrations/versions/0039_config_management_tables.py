"""config management tables — grow types, task templates, tenant overrides

Revision ID: 0039
Revises: 0038
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID

revision = "0039"
down_revision = "0038"
branch_labels = None
depends_on = None

postgresql = sa.dialects.postgresql


def upgrade() -> None:
    # Drop legacy grow_type_profiles table (created in 0002 with String PK / JSON columns)
    op.drop_table("grow_type_profiles")

    # ─── Grow Type Profiles (new normalized schema) ────────────────────────
    op.create_table(
        "grow_type_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sensor_kit", sa.String(100), nullable=True),
        sa.Column("ai_context_prompt", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ─── Grow Type Stages ──────────────────────────────────────────────────
    op.create_table(
        "grow_type_stages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("duration_days_min", sa.Integer, nullable=True),
        sa.Column("duration_days_max", sa.Integer, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tips", sa.Text, nullable=True),
        sa.UniqueConstraint("profile_id", "slug", name="uq_grow_type_stage_profile_slug"),
    )

    # ─── Grow Type Environment ─────────────────────────────────────────────
    op.create_table(
        "grow_type_environment",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stage_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_stages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("temp_min", sa.Float, nullable=True),
        sa.Column("temp_max", sa.Float, nullable=True),
        sa.Column("temp_ideal", sa.Float, nullable=True),
        sa.Column("humidity_min", sa.Float, nullable=True),
        sa.Column("humidity_max", sa.Float, nullable=True),
        sa.Column("humidity_ideal", sa.Float, nullable=True),
        sa.Column("vpd_min", sa.Float, nullable=True),
        sa.Column("vpd_max", sa.Float, nullable=True),
        sa.Column("light_hours", sa.Float, nullable=True),
        sa.Column("light_ppfd_min", sa.Float, nullable=True),
        sa.Column("light_ppfd_max", sa.Float, nullable=True),
        sa.Column("co2_min", sa.Float, nullable=True),
        sa.Column("co2_max", sa.Float, nullable=True),
        sa.Column("water_temp_min", sa.Float, nullable=True),
        sa.Column("water_temp_max", sa.Float, nullable=True),
        sa.UniqueConstraint("stage_id", name="uq_grow_type_environment_stage"),
    )

    # ─── Grow Type Nutrients ───────────────────────────────────────────────
    op.create_table(
        "grow_type_nutrients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stage_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_stages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("week", sa.Integer, nullable=False, server_default="1"),
        sa.Column("ec_min", sa.Float, nullable=True),
        sa.Column("ec_max", sa.Float, nullable=True),
        sa.Column("ec_target", sa.Float, nullable=True),
        sa.Column("ph_min", sa.Float, nullable=True),
        sa.Column("ph_max", sa.Float, nullable=True),
        sa.Column("ph_target", sa.Float, nullable=True),
        sa.Column("base_nutrients", JSON, nullable=True),
        sa.Column("supplements", JSON, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )

    # ─── Grow Type Watering ────────────────────────────────────────────────
    op.create_table(
        "grow_type_watering",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stage_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_stages.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("method", sa.String(100), nullable=True),
        sa.Column("frequency_hours", sa.Float, nullable=True),
        sa.Column("volume_ml", sa.Float, nullable=True),
        sa.Column("runoff_target_pct", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.UniqueConstraint("stage_id", name="uq_grow_type_watering_stage"),
    )

    # ─── Grow Type Equipment ───────────────────────────────────────────────
    op.create_table(
        "grow_type_equipment",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("item_name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("required", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("purchase_url", sa.String(1024), nullable=True),
    )

    # ─── Grow Type Troubleshooting ─────────────────────────────────────────
    op.create_table(
        "grow_type_troubleshooting",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "profile_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_type_profiles.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "stage_id", UUID(as_uuid=True), sa.ForeignKey("grow_type_stages.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column("symptom", sa.Text, nullable=False),
        sa.Column("cause", sa.Text, nullable=True),
        sa.Column("solution", sa.Text, nullable=True),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("image_url", sa.String(1024), nullable=True),
    )

    # ─── Task Templates ────────────────────────────────────────────────────
    op.create_table(
        "task_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(100), nullable=False, index=True),
        sa.Column("grow_type_slugs", ARRAY(sa.String(100)), nullable=True),
        sa.Column("frequency_hours", sa.Float, nullable=False, server_default="0"),
        sa.Column("stage_slug", sa.String(100), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="'medium'"),
        sa.Column("routine", sa.String(50), nullable=True),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="5"),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ─── Task Template Steps ───────────────────────────────────────────────
    op.create_table(
        "task_template_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "template_id",
            UUID(as_uuid=True),
            sa.ForeignKey("task_templates.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("instruction", sa.Text, nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("optional", sa.Boolean, nullable=False, server_default="false"),
    )

    # ─── Tenant Config Overrides ───────────────────────────────────────────
    op.create_table(
        "tenant_config_overrides",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("config_type", sa.String(50), nullable=False),
        sa.Column("config_key", sa.String(500), nullable=False),
        sa.Column("override_json", JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "config_type", "config_key", name="uq_tenant_config_override"),
    )


def downgrade() -> None:
    op.drop_table("tenant_config_overrides")
    op.drop_table("task_template_steps")
    op.drop_table("task_templates")
    op.drop_table("grow_type_troubleshooting")
    op.drop_table("grow_type_equipment")
    op.drop_table("grow_type_watering")
    op.drop_table("grow_type_nutrients")
    op.drop_table("grow_type_environment")
    op.drop_table("grow_type_stages")
    op.drop_table("grow_type_profiles")

    # Recreate legacy grow_type_profiles table (from 0002)
    op.create_table(
        "grow_type_profiles",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("terminology", JSON, nullable=False),
        sa.Column("sensor_kit", sa.String(100), nullable=False),
        sa.Column("relevant_sensors", JSON, nullable=False),
        sa.Column("primary_sensors", JSON, nullable=False),
        sa.Column("irrelevant_sensors", JSON, nullable=False),
        sa.Column("unique_fields", JSON, nullable=False),
        sa.Column("ph_range", JSON, nullable=False),
        sa.Column("ec_range", JSON, nullable=False),
        sa.Column("health_check_questions", JSON, nullable=False),
        sa.Column("automations", JSON, nullable=False),
        sa.Column("feeding_approach", sa.Text, nullable=False),
        sa.Column("nutrient_strength", sa.String(50), nullable=False),
        sa.Column("common_problems", JSON, nullable=False),
        sa.Column("ai_prompt_context", sa.Text, nullable=False),
    )
