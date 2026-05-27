"""add deleted_at to tenants and users for soft-delete

Revision ID: 0036
Revises: 0035
Create Date: 2026-05-27
"""

from alembic import op

revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE tenants
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tenants_deleted_at ON tenants (deleted_at);
    """)
    op.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_users_deleted_at ON users (deleted_at);
    """)


def downgrade() -> None:
    op.drop_index("ix_users_deleted_at", table_name="users")
    op.drop_column("users", "deleted_at")
    op.drop_index("ix_tenants_deleted_at", table_name="tenants")
    op.drop_column("tenants", "deleted_at")
