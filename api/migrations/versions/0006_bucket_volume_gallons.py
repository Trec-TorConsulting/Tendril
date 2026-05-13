"""Add volume_gallons column to buckets table.

Revision ID: 0006
Revises: 0005
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"


def upgrade() -> None:
    op.add_column("buckets", sa.Column("volume_gallons", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("buckets", "volume_gallons")
