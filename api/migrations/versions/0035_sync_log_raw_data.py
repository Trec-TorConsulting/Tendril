"""add raw_data to integration_sync_logs

Revision ID: 0035
Revises: 0034
Create Date: 2026-05-22
"""

from alembic import op

revision = "0035"
down_revision = "0034"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE integration_sync_logs
        ADD COLUMN IF NOT EXISTS raw_data JSONB;
    """)


def downgrade() -> None:
    op.drop_column("integration_sync_logs", "raw_data")
