"""Add routine and estimated_minutes columns to tasks table.

Supports routine-based task grouping (morning, evening, weekly, monthly)
and estimated task duration for user planning.

Revision ID: 0028
Revises: 0027
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("routine", sa.String(20), nullable=True))
    op.add_column("tasks", sa.Column("estimated_minutes", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "estimated_minutes")
    op.drop_column("tasks", "routine")
