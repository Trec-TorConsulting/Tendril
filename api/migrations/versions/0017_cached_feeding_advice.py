"""add cached_feeding_advice and feeding_advice_cached_at to grow_cycles

Revision ID: 0017
Revises: 0016
Create Date: 2026-04-23
"""

from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("grow_cycles", sa.Column("cached_feeding_advice", sa.JSON, nullable=True))
    op.add_column(
        "grow_cycles",
        sa.Column("feeding_advice_cached_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("grow_cycles", "feeding_advice_cached_at")
    op.drop_column("grow_cycles", "cached_feeding_advice")
