"""Add platform admin and support flags to users.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_platform_admin", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("is_support", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_support")
    op.drop_column("users", "is_platform_admin")
