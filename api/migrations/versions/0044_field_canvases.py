"""Add field_canvases table

Revision ID: 0044
Revises: 0043
Create Date: 2026-06-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "field_canvases",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(255), server_default="Main Field"),
        sa.Column("canvas_data", JSONB, server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("thumbnail_key", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("grow_cycle_id"),
    )
    op.create_index("ix_field_canvases_tenant_id", "field_canvases", ["tenant_id"])

    # RLS policy
    op.execute("ALTER TABLE field_canvases ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY field_canvases_tenant ON field_canvases "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS field_canvases_tenant ON field_canvases")
    op.execute("ALTER TABLE field_canvases DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_field_canvases_tenant_id")
    op.drop_table("field_canvases")
