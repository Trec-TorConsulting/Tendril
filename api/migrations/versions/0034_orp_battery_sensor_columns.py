"""add orp, salinity, specific_gravity, battery_pct to bucket_sensor_readings

Revision ID: 0034
Revises: 0033
Create Date: 2026-05-22
"""

from alembic import op

revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE bucket_sensor_readings
        ADD COLUMN IF NOT EXISTS orp FLOAT,
        ADD COLUMN IF NOT EXISTS salinity FLOAT,
        ADD COLUMN IF NOT EXISTS specific_gravity FLOAT,
        ADD COLUMN IF NOT EXISTS battery_pct FLOAT;
    """)


def downgrade() -> None:
    op.drop_column("bucket_sensor_readings", "battery_pct")
    op.drop_column("bucket_sensor_readings", "specific_gravity")
    op.drop_column("bucket_sensor_readings", "salinity")
    op.drop_column("bucket_sensor_readings", "orp")
