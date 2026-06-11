"""Add controllable_equipment and equipment_state_log tables

Revision ID: 0045
Revises: 0044
Create Date: 2026-06-11
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── controllable_equipment ─────────────────────────────────────────────
    op.create_table(
        "controllable_equipment",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "tent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("equipment_type", sa.String(50), nullable=False),
        sa.Column("protocol", sa.String(30), nullable=False),
        sa.Column("protocol_config", JSONB, nullable=False, server_default="{}"),
        sa.Column("capabilities", JSONB, nullable=False, server_default="[]"),
        sa.Column("requested_state", JSONB, nullable=False, server_default="{}"),
        sa.Column("confirmed_state", JSONB, nullable=False, server_default="{}"),
        sa.Column("last_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_on_minutes", sa.Integer, nullable=True),
        sa.Column("cooldown_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "conflicts_with",
            ARRAY(UUID(as_uuid=True)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_controllable_equipment_tenant_id",
        "controllable_equipment",
        ["tenant_id"],
    )
    op.create_index(
        "ix_controllable_equipment_tent_id",
        "controllable_equipment",
        ["tent_id"],
    )

    # RLS policy
    op.execute("ALTER TABLE controllable_equipment ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY controllable_equipment_tenant ON controllable_equipment "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )

    # ── equipment_state_log ────────────────────────────────────────────────
    op.create_table(
        "equipment_state_log",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "equipment_id",
            UUID(as_uuid=True),
            sa.ForeignKey("controllable_equipment.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("state_before", JSONB, nullable=True),
        sa.Column("state_after", JSONB, nullable=True),
        sa.Column("metadata_", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_equipment_state_log_tenant_id",
        "equipment_state_log",
        ["tenant_id"],
    )
    op.create_index(
        "ix_equipment_state_log_equipment_id",
        "equipment_state_log",
        ["equipment_id"],
    )
    op.create_index(
        "ix_equipment_state_log_created_at",
        "equipment_state_log",
        ["created_at"],
    )

    # RLS policy
    op.execute("ALTER TABLE equipment_state_log ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY equipment_state_log_tenant ON equipment_state_log "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def downgrade() -> None:
    # equipment_state_log
    op.execute("DROP POLICY IF EXISTS equipment_state_log_tenant ON equipment_state_log")
    op.execute("ALTER TABLE equipment_state_log DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_equipment_state_log_created_at")
    op.drop_index("ix_equipment_state_log_equipment_id")
    op.drop_index("ix_equipment_state_log_tenant_id")
    op.drop_table("equipment_state_log")

    # controllable_equipment
    op.execute("DROP POLICY IF EXISTS controllable_equipment_tenant ON controllable_equipment")
    op.execute("ALTER TABLE controllable_equipment DISABLE ROW LEVEL SECURITY")
    op.drop_index("ix_controllable_equipment_tent_id")
    op.drop_index("ix_controllable_equipment_tenant_id")
    op.drop_table("controllable_equipment")
