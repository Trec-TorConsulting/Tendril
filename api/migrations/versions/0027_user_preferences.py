"""Add preferences JSONB column to users table.

Stores user-level preferences: temp_unit, timezone, date_format,
dashboard_default_grow_id, theme, widget_layout, etc.

Revision ID: 0027
Revises: 0026
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("preferences", JSONB, nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("users", "preferences")
