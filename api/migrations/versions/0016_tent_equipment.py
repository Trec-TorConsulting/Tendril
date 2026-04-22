"""add equipment and size to tents

Revision ID: 0016
Revises: 0015
Create Date: 2026-04-22
"""

from alembic import op
import sqlalchemy as sa

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tents", sa.Column("size", sa.String(50), nullable=True))
    op.add_column("tents", sa.Column("equipment", sa.JSON, nullable=True, server_default="[]"))


def downgrade() -> None:
    op.drop_column("tents", "equipment")
    op.drop_column("tents", "size")
