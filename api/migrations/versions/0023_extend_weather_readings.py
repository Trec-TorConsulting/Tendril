"""Extend weather_readings with dew_point, pressure, soil_temp, source.

Revision ID: 0023
Revises: 0022
"""
from alembic import op
import sqlalchemy as sa

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("weather_readings", sa.Column("dew_point_c", sa.Float(), nullable=True))
    op.add_column("weather_readings", sa.Column("pressure_hpa", sa.Float(), nullable=True))
    op.add_column("weather_readings", sa.Column("soil_temp_c", sa.Float(), nullable=True))
    op.add_column("weather_readings", sa.Column("source", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("weather_readings", "source")
    op.drop_column("weather_readings", "soil_temp_c")
    op.drop_column("weather_readings", "pressure_hpa")
    op.drop_column("weather_readings", "dew_point_c")
