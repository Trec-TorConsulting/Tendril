"""Extend tent_sensor_readings with VPD, CO2, lux, dew point, PAR, pressure, VOC.

Revision ID: 0022
Revises: 0021
Create Date: 2026-04-28
"""

import sqlalchemy as sa
from alembic import op

revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tent_sensor_readings", sa.Column("vpd", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("co2", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("lux", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("dew_point_f", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("par_ppfd", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("air_pressure", sa.Float(), nullable=True))
    op.add_column("tent_sensor_readings", sa.Column("voc", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("tent_sensor_readings", "voc")
    op.drop_column("tent_sensor_readings", "air_pressure")
    op.drop_column("tent_sensor_readings", "par_ppfd")
    op.drop_column("tent_sensor_readings", "dew_point_f")
    op.drop_column("tent_sensor_readings", "lux")
    op.drop_column("tent_sensor_readings", "co2")
    op.drop_column("tent_sensor_readings", "vpd")
