"""account_dunning_deletion_fields

Revision ID: 0032
Revises: 0031
Create Date: 2026-05-06
"""

from alembic import op

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Dunning columns on accounts (idempotent for asyncpg)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE accounts ADD COLUMN IF NOT EXISTS dunning_started_at TIMESTAMPTZ;
            ALTER TABLE accounts ADD COLUMN IF NOT EXISTS dunning_attempts INTEGER;
            ALTER TABLE accounts ADD COLUMN IF NOT EXISTS deletion_scheduled_at TIMESTAMPTZ;
            ALTER TABLE accounts ADD COLUMN IF NOT EXISTS deletion_date TIMESTAMPTZ;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column("accounts", "deletion_date")
    op.drop_column("accounts", "deletion_scheduled_at")
    op.drop_column("accounts", "dunning_attempts")
    op.drop_column("accounts", "dunning_started_at")
