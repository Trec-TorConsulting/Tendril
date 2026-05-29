"""Phase 2: reference tables for stage transitions, automation, companions, feed charts

Revision ID: 0041
Revises: 0040
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID

revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Stage transition tasks — tasks auto-generated on stage change
    op.create_table(
        "stage_transition_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("stage", sa.String(50), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("brief", sa.Text, nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("routine", sa.String(30), nullable=False, server_default="on_demand"),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="10"),
        sa.Column("grow_type_slugs", ARRAY(sa.String), nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Automation suppressions — which automations suppress which task categories
    op.create_table(
        "automation_suppressions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("automation_key", sa.String(100), nullable=False, unique=True),
        sa.Column("suppressed_categories", ARRAY(sa.String), nullable=False),
        sa.Column("verify_task", JSON, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Companion plants reference
    op.create_table(
        "companion_plants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("benefits", ARRAY(sa.String), nullable=False),
        sa.Column("companions", ARRAY(sa.String), nullable=True),
        sa.Column("antagonists", ARRAY(sa.String), nullable=True),
        sa.Column("spacing_inches", sa.Integer, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Feed charts — brand nutrient schedules
    op.create_table(
        "feed_charts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("line", sa.String(100), nullable=False),
        sa.Column("medium", ARRAY(sa.String), nullable=False),
        sa.Column("products", ARRAY(sa.String), nullable=False),
        sa.Column("schedule", JSON, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("brand", "line", name="uq_feed_chart_brand_line"),
    )


def downgrade() -> None:
    op.drop_table("feed_charts")
    op.drop_table("companion_plants")
    op.drop_table("automation_suppressions")
    op.drop_table("stage_transition_tasks")
