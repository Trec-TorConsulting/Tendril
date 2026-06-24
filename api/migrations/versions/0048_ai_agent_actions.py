"""add ai agent action lifecycle tables

Revision ID: 0048
Revises: 0047
Create Date: 2026-06-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0048"
down_revision = "0047"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_agent_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "conversation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_conversations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "grow_cycle_id",
            UUID(as_uuid=True),
            sa.ForeignKey("grow_cycles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_by_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="proposed"),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="low"),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("auto_approved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("evidence_json", JSONB, nullable=True),
        sa.Column("execution_json", JSONB, nullable=True),
        sa.Column("verification_json", JSONB, nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_agent_actions_tenant_id", "ai_agent_actions", ["tenant_id"])
    op.create_index("ix_ai_agent_actions_conversation_id", "ai_agent_actions", ["conversation_id"])
    op.create_index("ix_ai_agent_actions_status", "ai_agent_actions", ["status"])
    op.create_index("ix_ai_agent_actions_idempotency_key", "ai_agent_actions", ["idempotency_key"], unique=True)

    op.create_table(
        "ai_agent_action_approvals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "action_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ai_agent_actions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "requested_by_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by_user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_agent_action_approvals_tenant_id", "ai_agent_action_approvals", ["tenant_id"])
    op.create_index("ix_ai_agent_action_approvals_action_id", "ai_agent_action_approvals", ["action_id"])
    op.create_index("ix_ai_agent_action_approvals_status", "ai_agent_action_approvals", ["status"])


def downgrade() -> None:
    op.drop_index("ix_ai_agent_action_approvals_status", table_name="ai_agent_action_approvals")
    op.drop_index("ix_ai_agent_action_approvals_action_id", table_name="ai_agent_action_approvals")
    op.drop_index("ix_ai_agent_action_approvals_tenant_id", table_name="ai_agent_action_approvals")
    op.drop_table("ai_agent_action_approvals")

    op.drop_index("ix_ai_agent_actions_idempotency_key", table_name="ai_agent_actions")
    op.drop_index("ix_ai_agent_actions_status", table_name="ai_agent_actions")
    op.drop_index("ix_ai_agent_actions_conversation_id", table_name="ai_agent_actions")
    op.drop_index("ix_ai_agent_actions_tenant_id", table_name="ai_agent_actions")
    op.drop_table("ai_agent_actions")
