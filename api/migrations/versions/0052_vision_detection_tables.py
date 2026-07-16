"""Add vision detection persistence tables

Revision ID: 0052
Revises: 0051_tenant_coaching_settings
Create Date: 2026-07-16
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0052"
down_revision = "0051_tenant_coaching_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vision_detections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "grow_cycle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_cycles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="manual"),
        sa.Column("source_ref", sa.String(length=255), nullable=True),
        sa.Column("image_storage_key", sa.String(length=1024), nullable=True),
        sa.Column("class_name", sa.String(length=100), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("bbox", JSONB, nullable=False, server_default="[]"),
        sa.Column("model_version", sa.String(length=120), nullable=False),
        sa.Column("accelerator_tier", sa.String(length=20), nullable=False, server_default="unavailable"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_vision_detections_tenant_id", "vision_detections", ["tenant_id"])
    op.create_index("ix_vision_detections_grow_cycle_id", "vision_detections", ["grow_cycle_id"])
    op.create_index("ix_vision_detections_source", "vision_detections", ["source"])
    op.create_index("ix_vision_detections_class_name", "vision_detections", ["class_name"])
    op.create_index("ix_vision_detections_created_at", "vision_detections", ["created_at"])

    op.execute("ALTER TABLE vision_detections ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY vision_detections_tenant ON vision_detections "
        "USING (tenant_id = current_setting('app.current_tenant')::uuid)"
    )

    op.create_table(
        "vision_model_registry",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.String(length=120), nullable=False),
        sa.Column("edge_tpu_storage_key", sa.String(length=1024), nullable=True),
        sa.Column("fallback_storage_key", sa.String(length=1024), nullable=True),
        sa.Column("class_map", JSONB, nullable=False, server_default="{}"),
        sa.Column("input_width", sa.Integer(), nullable=False, server_default="640"),
        sa.Column("input_height", sa.Integer(), nullable=False, server_default="640"),
        sa.Column("metrics", JSONB, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "version", name="uq_vision_model_registry_tenant_version"),
    )
    op.create_index("ix_vision_model_registry_tenant_id", "vision_model_registry", ["tenant_id"])
    op.create_index("ix_vision_model_registry_version", "vision_model_registry", ["version"])
    op.create_index("ix_vision_model_registry_is_active", "vision_model_registry", ["is_active"])

    op.execute("ALTER TABLE vision_model_registry ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY vision_model_registry_tenant ON vision_model_registry "
        "USING (tenant_id = current_setting('app.current_tenant')::uuid)"
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS vision_model_registry_tenant ON vision_model_registry")
    op.execute("ALTER TABLE vision_model_registry DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_vision_model_registry_is_active", table_name="vision_model_registry")
    op.drop_index("ix_vision_model_registry_version", table_name="vision_model_registry")
    op.drop_index("ix_vision_model_registry_tenant_id", table_name="vision_model_registry")
    op.drop_table("vision_model_registry")

    op.execute("DROP POLICY IF EXISTS vision_detections_tenant ON vision_detections")
    op.execute("ALTER TABLE vision_detections DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_vision_detections_created_at", table_name="vision_detections")
    op.drop_index("ix_vision_detections_class_name", table_name="vision_detections")
    op.drop_index("ix_vision_detections_source", table_name="vision_detections")
    op.drop_index("ix_vision_detections_grow_cycle_id", table_name="vision_detections")
    op.drop_index("ix_vision_detections_tenant_id", table_name="vision_detections")
    op.drop_table("vision_detections")
