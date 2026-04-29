"""Add tent_cameras table, layout_mode to users, migrate camera_url data.

Revision ID: 0025
Revises: 0024
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tent_cameras table
    op.create_table(
        "tent_cameras",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(100), nullable=False, server_default="Camera"),
        sa.Column("camera_type", sa.String(20), nullable=False, server_default="http_snapshot"),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )
    op.create_index("idx_tent_cameras_tent_id", "tent_cameras", ["tent_id"])

    # Add layout_mode to users
    op.add_column("users", sa.Column("layout_mode", sa.String(20), nullable=False, server_default="standard"))

    # Migrate existing camera_url data to tent_cameras
    op.execute("""
        INSERT INTO tent_cameras (tent_id, label, camera_type, url, sort_order, is_primary)
        SELECT id, 'Camera', 'http_snapshot', camera_url, 0, TRUE
        FROM tents
        WHERE camera_url IS NOT NULL AND camera_url != ''
    """)

    # Drop camera_url column from tents
    op.drop_column("tents", "camera_url")


def downgrade() -> None:
    # Re-add camera_url column
    op.add_column("tents", sa.Column("camera_url", sa.String(1024), nullable=True))

    # Migrate primary cameras back to tents.camera_url
    op.execute("""
        UPDATE tents SET camera_url = tc.url
        FROM tent_cameras tc
        WHERE tc.tent_id = tents.id AND tc.is_primary = TRUE
    """)

    # Drop layout_mode from users
    op.drop_column("users", "layout_mode")

    # Drop tent_cameras table
    op.drop_index("idx_tent_cameras_tent_id", table_name="tent_cameras")
    op.drop_table("tent_cameras")
