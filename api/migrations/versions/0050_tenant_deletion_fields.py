"""tenant_deletion_fields

Revision ID: 0050
Revises: 0049
Create Date: 2026-06-25
"""

from alembic import op

revision = "0050"
down_revision = "0049"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Keep idempotent to handle environments where columns may already exist.
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE tenants ADD COLUMN IF NOT EXISTS deletion_scheduled_at TIMESTAMPTZ;
            ALTER TABLE tenants ADD COLUMN IF NOT EXISTS deletion_date TIMESTAMPTZ;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column("tenants", "deletion_date")
    op.drop_column("tenants", "deletion_scheduled_at")
