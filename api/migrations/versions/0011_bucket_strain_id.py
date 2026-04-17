"""Add strain_id FK to buckets + harvest countdown support.

Revision ID: 0011
Create Date: 2026-04-17

Links buckets to the strains table for rich strain-aware automation.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add strain_id FK to buckets
    op.add_column("buckets", sa.Column("strain_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_buckets_strain_id",
        "buckets",
        "strains",
        ["strain_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Backfill strain_id from strain_name where names match
    op.execute("""
        UPDATE buckets b
        SET strain_id = s.id
        FROM strains s
        WHERE LOWER(b.strain_name) = LOWER(s.name)
          AND b.strain_id IS NULL
    """)


def downgrade() -> None:
    op.drop_constraint("fk_buckets_strain_id", "buckets", type_="foreignkey")
    op.drop_column("buckets", "strain_id")
