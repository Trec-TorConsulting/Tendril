"""Phase 3: nutrient knowledge + ESPHome templates to DB

Revision ID: 0042
Revises: 0041
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSON, UUID

revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Nutrient knowledge entries (DIY recipes, emergency subs, pH guides, methodology)
    op.create_table(
        "nutrient_knowledge",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entry_id", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("data", JSON, nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ESPHome config templates
    op.create_table(
        "esphome_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("template_id", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("sensors", ARRAY(sa.String), nullable=False),
        sa.Column("board", sa.String(50), nullable=False, server_default="esp32dev"),
        sa.Column("yaml_body", sa.Text, nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("esphome_templates")
    op.drop_table("nutrient_knowledge")
