"""Add target_ppm and target_ec columns to feeding_schedules.

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"


def upgrade() -> None:
    op.add_column("feeding_schedules", sa.Column("target_ppm", sa.Float(), nullable=True))
    op.add_column("feeding_schedules", sa.Column("target_ec", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("feeding_schedules", "target_ec")
    op.drop_column("feeding_schedules", "target_ppm")
