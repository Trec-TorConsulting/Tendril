"""Add deleted_at columns for soft-delete on tents, grow_cycles, devices.

Revision ID: 0021
Revises: 0020
Create Date: 2025-07-22
"""

import sqlalchemy as sa
from alembic import op

revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tents", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_tents_deleted_at", "tents", ["deleted_at"])

    op.add_column("grow_cycles", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_grow_cycles_deleted_at", "grow_cycles", ["deleted_at"])

    op.add_column("devices", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_devices_deleted_at", "devices", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_devices_deleted_at", "devices")
    op.drop_column("devices", "deleted_at")

    op.drop_index("ix_grow_cycles_deleted_at", "grow_cycles")
    op.drop_column("grow_cycles", "deleted_at")

    op.drop_index("ix_tents_deleted_at", "tents")
    op.drop_column("tents", "deleted_at")
