"""add role column to buckets

Revision ID: 0033
Revises: 0032
Create Date: 2026-05-22
"""

from alembic import op

revision = "0033"
down_revision = "0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE buckets
        ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'site';
    """)


def downgrade() -> None:
    op.drop_column("buckets", "role")
