"""Add extended_config JSONB column to grow_type_profiles

Stores scale_tiers, strain_adjustments, monitoring_thresholds, and other
rich configuration data that was previously only in hardcoded config files.

Revision ID: 0040
Revises: 0039
Create Date: 2026-05-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSON

revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "grow_type_profiles",
        sa.Column("extended_config", JSON, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("grow_type_profiles", "extended_config")
