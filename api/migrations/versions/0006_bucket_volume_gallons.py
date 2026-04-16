"""Add volume_gallons column to buckets table.

Revision ID: 0006
Revises: 0005
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"


def upgrade() -> None:
    op.add_column("buckets", sa.Column("volume_gallons", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("buckets", "volume_gallons")
