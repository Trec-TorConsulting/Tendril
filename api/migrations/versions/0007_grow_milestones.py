"""Add milestones JSON column to grow_cycles table.

Revision ID: 0007
Revises: 0006
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    op.add_column("grow_cycles", sa.Column("milestones", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("grow_cycles", "milestones")
