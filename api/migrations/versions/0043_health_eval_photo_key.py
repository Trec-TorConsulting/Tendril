"""Add photo_storage_key to health_evals

Revision ID: 0043
Revises: 0042
Create Date: 2026-06-01
"""

import sqlalchemy as sa
from alembic import op

revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("health_evals", sa.Column("photo_storage_key", sa.String(1024), nullable=True))


def downgrade() -> None:
    op.drop_column("health_evals", "photo_storage_key")
