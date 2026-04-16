"""Add camera_url column to tents table.

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tents", sa.Column("camera_url", sa.String(1024), nullable=True))


def downgrade() -> None:
    op.drop_column("tents", "camera_url")
