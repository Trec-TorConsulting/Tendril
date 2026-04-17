"""Add category, source, bucket_id to tasks for auto-generation.

Revision ID: 0012
Create Date: 2026-04-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the tasks table (it never existed before)
    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("priority", sa.String(20), server_default="medium", nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("source", sa.String(50), server_default="manual", nullable=False),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id"), nullable=True),
        sa.Column("tent_id", UUID(as_uuid=True), sa.ForeignKey("tents.id"), nullable=True),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("recurring", sa.String(50), nullable=True),
        sa.Column("recurring_parent_id", UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # RLS
    op.execute("ALTER TABLE tasks ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY tenant_isolation_tasks ON tasks
            USING (tenant_id = current_setting('app.current_tenant')::UUID)
    """)

    # Indexes
    op.create_index("ix_tasks_grow_cycle_id", "tasks", ["grow_cycle_id"])
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index("ix_tasks_category", "tasks", ["category"])


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_tasks ON tasks")
    op.drop_table("tasks")
