"""add outdoor container experience tables — container profiles and runoff readings

Revision ID: 0019
Revises: 0018
Create Date: 2026-04-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Container Profiles (per-pot metadata for outdoor container grows) --
    op.create_table(
        "container_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "bucket_id",
            UUID(as_uuid=True),
            sa.ForeignKey("buckets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("pot_size_gallons", sa.Float, nullable=True),
        sa.Column("media_type", sa.String(100), nullable=True),
        sa.Column("pot_color", sa.String(50), nullable=True),
        sa.Column("pot_material", sa.String(50), nullable=True),
        sa.Column("has_saucer", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_mobile", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("sun_exposure", sa.String(50), nullable=True),
        sa.Column("location_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_container_profiles_grow_cycle_id", "container_profiles", ["grow_cycle_id"])
    op.create_index("ix_container_profiles_bucket_id", "container_profiles", ["bucket_id"])

    # -- Runoff Readings (input vs runoff pH/EC tracking) --
    op.create_table(
        "runoff_readings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("input_ph", sa.Float, nullable=True),
        sa.Column("input_ec", sa.Float, nullable=True),
        sa.Column("runoff_ph", sa.Float, nullable=True),
        sa.Column("runoff_ec", sa.Float, nullable=True),
        sa.Column("runoff_pct", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_runoff_readings_grow_cycle_id", "runoff_readings", ["grow_cycle_id"])
    op.create_index("ix_runoff_readings_bucket_id", "runoff_readings", ["bucket_id"])
    op.create_index("ix_runoff_readings_recorded_at", "runoff_readings", ["recorded_at"])

    # -- RLS policies --
    for table in ("container_profiles", "runoff_readings"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant')::uuid)"
        )


def downgrade() -> None:
    for table in ("runoff_readings", "container_profiles"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")

    op.drop_index("ix_runoff_readings_recorded_at", table_name="runoff_readings")
    op.drop_index("ix_runoff_readings_bucket_id", table_name="runoff_readings")
    op.drop_index("ix_runoff_readings_grow_cycle_id", table_name="runoff_readings")
    op.drop_table("runoff_readings")

    op.drop_index("ix_container_profiles_bucket_id", table_name="container_profiles")
    op.drop_index("ix_container_profiles_grow_cycle_id", table_name="container_profiles")
    op.drop_table("container_profiles")
