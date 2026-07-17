"""Add recurring_interval_days to tasks table.

Revision ID: 0053
Revises: 0052_vision_detection_tables
Create Date: 2026-07-17
"""

import sqlalchemy as sa
from alembic import op

revision = "0053"
down_revision = "0052_vision_detection_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tasks", sa.Column("recurring_interval_days", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("tasks", "recurring_interval_days")
