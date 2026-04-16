"""0005 commercial tier tables

Revision ID: 0005
Revises: 0004
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Custom grow types
    op.create_table(
        "custom_grow_types",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("profile", JSON, nullable=False),
        sa.Column("base_type", sa.String(100)),
        sa.Column("submitted_for_review", sa.Boolean, server_default="false"),
        sa.Column("approved", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_custom_grow_types_tenant_id", "custom_grow_types", ["tenant_id"])

    # Tasks
    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("priority", sa.String(20), server_default="medium"),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id")),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id")),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("recurring", sa.String(50)),
        sa.Column("recurring_parent_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tasks_tenant_id", "tasks", ["tenant_id"])

    # Audit log
    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=False),
        sa.Column("before_value", JSON),
        sa.Column("after_value", JSON),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_tenant_id", "audit_log", ["tenant_id"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    # API keys
    op.create_table(
        "api_keys",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("key_prefix", sa.String(12), nullable=False),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("scopes", sa.String(500), server_default="read"),
        sa.Column("last_used", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("revoked", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"])

    # RLS policies for all new tables
    for table in ("custom_grow_types", "tasks", "audit_log", "api_keys"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING (tenant_id::text = current_setting('app.current_tenant', true))"
        )


def downgrade() -> None:
    for table in ("api_keys", "audit_log", "tasks", "custom_grow_types"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.drop_table(table)
