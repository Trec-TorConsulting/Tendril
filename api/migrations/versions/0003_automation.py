"""Phase 4 automation tables.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Automation rules
    op.create_table(
        "automation_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sensor", sa.String(50), nullable=False),
        sa.Column("condition", sa.String(10), nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("action_params", JSON),
        sa.Column("cooldown_minutes", sa.Integer, default=30),
        sa.Column("severity", sa.String(20), default="warning"),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("last_triggered", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Alert history
    op.create_table(
        "alert_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("rule_id", UUID(as_uuid=True), sa.ForeignKey("automation_rules.id")),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id")),
        sa.Column("alert_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("sensor_value", sa.Float),
        sa.Column("acknowledged", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Environment schedules
    op.create_table(
        "environment_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("schedule_type", sa.String(50), nullable=False),
        sa.Column("stage", sa.String(50)),
        sa.Column("on_time", sa.String(5), nullable=False),
        sa.Column("off_time", sa.String(5), nullable=False),
        sa.Column("settings", JSON),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # RLS policies
    for table in ("automation_rules", "alert_history", "environment_schedules"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.current_tenant')::UUID)
        """)

    # Indexes
    op.create_index("ix_alert_history_created_at", "alert_history", ["created_at"])
    op.create_index("ix_automation_rules_grow_cycle_id", "automation_rules", ["grow_cycle_id"])
    op.create_index("ix_environment_schedules_tent_id", "environment_schedules", ["tent_id"])


def downgrade() -> None:
    op.drop_table("environment_schedules")
    op.drop_table("alert_history")
    op.drop_table("automation_rules")
