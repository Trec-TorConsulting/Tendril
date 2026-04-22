"""tent_sensor_readings — ambient temp & humidity at the tent level

Revision ID: 0015
Revises: 0014
Create Date: 2026-04-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tent_sensor_readings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.String(100), nullable=True),
        sa.Column("ambient_temp_f", sa.Float, nullable=True),
        sa.Column("ambient_humidity", sa.Float, nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_tent_sensor_readings_tent_id", "tent_sensor_readings", ["tent_id"])
    op.create_index("ix_tent_sensor_readings_recorded_at", "tent_sensor_readings", ["recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_tent_sensor_readings_recorded_at", table_name="tent_sensor_readings")
    op.drop_index("ix_tent_sensor_readings_tent_id", table_name="tent_sensor_readings")
    op.drop_table("tent_sensor_readings")
