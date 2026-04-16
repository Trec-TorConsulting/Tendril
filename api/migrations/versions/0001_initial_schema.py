"""Initial schema — tenants, users, devices with RLS

Revision ID: 0001
Revises: None
Create Date: 2026-04-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("plan", sa.String(50), server_default="free"),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("stripe_subscription_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255)),
        sa.Column("display_name", sa.String(255)),
        sa.Column("role", sa.String(50), server_default="owner"),
        sa.Column("auth_provider", sa.String(50), server_default="local"),
        sa.Column("auth_provider_id", sa.String(255)),
        sa.Column("email_verified", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # Devices
    op.create_table(
        "devices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("device_id", sa.String(100), unique=True, nullable=False),
        sa.Column("psk_hash", sa.String(255), nullable=False),
        sa.Column("label", sa.String(255)),
        sa.Column("tent_id", UUID(as_uuid=True)),
        sa.Column("status", sa.String(50), server_default="paired"),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("firmware_version", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # RLS policies — enforce tenant isolation
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_users ON users
            USING (tenant_id = current_setting('app.current_tenant')::UUID)
    """)

    op.execute("ALTER TABLE devices ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_devices ON devices
            USING (tenant_id = current_setting('app.current_tenant')::UUID)
    """)

    # Indexes
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_devices_tenant_id", "devices", ["tenant_id"])
    op.create_index("ix_devices_device_id", "devices", ["device_id"])


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_devices ON devices")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_users ON users")
    op.drop_table("devices")
    op.drop_table("users")
    op.drop_table("tenants")
