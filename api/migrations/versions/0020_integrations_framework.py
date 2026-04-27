"""add integrations framework — config, device maps, sync logs

Revision ID: 0020
Revises: 0019
Create Date: 2026-04-27
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Integration Configs --
    op.create_table(
        "integration_configs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("config", sa.Text, nullable=False),  # Fernet-encrypted JSON
        sa.Column("webhook_secret", sa.String(255), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("poll_interval_s", sa.Integer, nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_integration_configs_tenant_id", "integration_configs", ["tenant_id"])
    op.create_index("ix_integration_configs_type", "integration_configs", ["type"])

    # -- Integration Device Maps --
    op.create_table(
        "integration_device_maps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "integration_id",
            UUID(as_uuid=True),
            sa.ForeignKey("integration_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_name", sa.String(255), nullable=True),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sensor_mapping", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_integration_device_maps_integration_id", "integration_device_maps", ["integration_id"])
    op.create_index(
        "ix_integration_device_maps_external",
        "integration_device_maps",
        ["integration_id", "external_id"],
        unique=True,
    )

    # -- Integration Sync Logs --
    op.create_table(
        "integration_sync_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "integration_id",
            UUID(as_uuid=True),
            sa.ForeignKey("integration_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),  # success | error | partial
        sa.Column("readings_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_integration_sync_logs_integration_id", "integration_sync_logs", ["integration_id"])
    op.create_index("ix_integration_sync_logs_synced_at", "integration_sync_logs", ["synced_at"])

    # -- RLS policies --
    for table in ("integration_configs", "integration_device_maps", "integration_sync_logs"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant')::uuid)"
        )


def downgrade() -> None:
    for table in ("integration_sync_logs", "integration_device_maps", "integration_configs"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")

    op.drop_index("ix_integration_sync_logs_synced_at", table_name="integration_sync_logs")
    op.drop_index("ix_integration_sync_logs_integration_id", table_name="integration_sync_logs")
    op.drop_table("integration_sync_logs")

    op.drop_index("ix_integration_device_maps_external", table_name="integration_device_maps")
    op.drop_index("ix_integration_device_maps_integration_id", table_name="integration_device_maps")
    op.drop_table("integration_device_maps")

    op.drop_index("ix_integration_configs_type", table_name="integration_configs")
    op.drop_index("ix_integration_configs_tenant_id", table_name="integration_configs")
    op.drop_table("integration_configs")
