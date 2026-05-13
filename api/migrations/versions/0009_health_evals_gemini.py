"""Add auto_health_check to grow_cycles and health_evals table.

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add auto_health_check toggle to grow_cycles
    op.add_column(
        "grow_cycles",
        sa.Column("auto_health_check", sa.Boolean(), server_default="false", nullable=False),
    )

    # Create health_evals table
    op.create_table(
        "health_evals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "grow_cycle_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("issues", postgresql.JSON(), nullable=True),
        sa.Column("actions", postgresql.JSON(), nullable=True),
        sa.Column("raw_analysis", sa.Text(), nullable=False, server_default=""),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_health_evals_grow_cycle_id", "health_evals", ["grow_cycle_id"])
    op.create_index("ix_health_evals_tenant_id", "health_evals", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("health_evals")
    op.drop_column("grow_cycles", "auto_health_check")
