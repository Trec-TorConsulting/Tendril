"""add event type to notification log

Revision ID: 0049
Revises: 0048
Create Date: 2026-06-25
"""

import sqlalchemy as sa
from alembic import op

revision = "0049"
down_revision = "0048"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "notification_log",
        sa.Column("event_type", sa.String(length=100), nullable=False, server_default="all"),
    )
    op.alter_column("notification_log", "event_type", server_default=None)


def downgrade() -> None:
    op.drop_column("notification_log", "event_type")