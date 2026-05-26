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

    # Add CHECK constraint to validate role enum
    op.execute("""
        ALTER TABLE buckets
        ADD CONSTRAINT buckets_role_check
        CHECK (role IN ('site', 'header'));
    """)

    # Add partial unique index to enforce at most one header per grow_cycle
    # This prevents multiple headers in RDWC grows
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_buckets_one_header_per_grow
        ON buckets(grow_cycle_id)
        WHERE role = 'header';
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_buckets_one_header_per_grow")
    op.execute("ALTER TABLE buckets DROP CONSTRAINT IF EXISTS buckets_role_check")
    op.drop_column("buckets", "role")
