"""Phase 5 — notifications, push subscriptions, notification log.

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision = "0004_notifications"
down_revision = "0003_automation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Notification channels
    op.create_table(
        "notification_channels",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("channel_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("config", JSON, nullable=False),
        sa.Column("enabled", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Notification preferences
    op.create_table(
        "notification_preferences",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("channel_id", UUID(as_uuid=True), sa.ForeignKey("notification_channels.id"), nullable=False),
        sa.Column("severity_filter", sa.String(100), default="warning,critical"),
        sa.Column("event_types", sa.String(500), default="all"),
        sa.Column("enabled", sa.Boolean, default=True),
    )

    # Push subscriptions
    op.create_table(
        "push_subscriptions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("endpoint", sa.Text, nullable=False),
        sa.Column("p256dh", sa.String(255), nullable=False),
        sa.Column("auth", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Notification log
    op.create_table(
        "notification_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("channel_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text),
        sa.Column("status", sa.String(20), default="sent"),
        sa.Column("error", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # RLS policies
    for table in ["notification_channels", "notification_preferences", "push_subscriptions", "notification_log"]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.current_tenant')::UUID)
        """)

    # Indexes for notification log cleanup
    op.create_index("ix_notification_log_created_at", "notification_log", ["created_at"])


def downgrade() -> None:
    for table in ["notification_log", "push_subscriptions", "notification_preferences", "notification_channels"]:
        op.drop_table(table)
