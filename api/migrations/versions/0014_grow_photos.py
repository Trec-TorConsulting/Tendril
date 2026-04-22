"""grow photos — grow-level photo storage with S3 keys

Revision ID: 0014
Revises: 0013
Create Date: 2026-04-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "grow_photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="upload"),
        sa.Column("storage_key", sa.String(1024), nullable=False),
        sa.Column("caption", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_grow_photos_grow_cycle_id", "grow_photos", ["grow_cycle_id"])
    op.create_index("ix_grow_photos_created_at", "grow_photos", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_grow_photos_created_at", table_name="grow_photos")
    op.drop_index("ix_grow_photos_grow_cycle_id", table_name="grow_photos")
    op.drop_table("grow_photos")
