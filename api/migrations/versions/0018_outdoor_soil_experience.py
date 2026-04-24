"""add outdoor soil experience tables — plot grids, soil tests, amendments, pest scouting, harvest yields; extend buckets

Revision ID: 0018
Revises: 0017
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -- Plot Grids --
    op.create_table(
        "plot_grids",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("rows", sa.Integer, nullable=False),
        sa.Column("cols", sa.Integer, nullable=False),
        sa.Column("cell_size_inches", sa.Integer, nullable=False, server_default="12"),
        sa.Column("orientation", sa.String(10), nullable=False, server_default="north"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_plot_grids_grow_cycle_id", "plot_grids", ["grow_cycle_id"])

    # -- Plot Cells --
    op.create_table(
        "plot_cells",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plot_grid_id", UUID(as_uuid=True), sa.ForeignKey("plot_grids.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row", sa.Integer, nullable=False),
        sa.Column("col", sa.Integer, nullable=False),
        sa.Column("cell_type", sa.String(50), nullable=False, server_default="empty"),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("companion_plant", sa.String(100), nullable=True),
        sa.Column("device_id", sa.String(100), nullable=True),
        sa.Column("irrigation_zone", sa.String(100), nullable=True),
        sa.Column("sun_zone", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.UniqueConstraint("plot_grid_id", "row", "col", name="uq_plot_cell_position"),
    )
    op.create_index("ix_plot_cells_plot_grid_id", "plot_cells", ["plot_grid_id"])

    # -- Soil Tests --
    op.create_table(
        "soil_tests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ph", sa.Float, nullable=True),
        sa.Column("nitrogen_ppm", sa.Float, nullable=True),
        sa.Column("phosphorus_ppm", sa.Float, nullable=True),
        sa.Column("potassium_ppm", sa.Float, nullable=True),
        sa.Column("organic_matter_pct", sa.Float, nullable=True),
        sa.Column("cec", sa.Float, nullable=True),
        sa.Column("calcium_ppm", sa.Float, nullable=True),
        sa.Column("magnesium_ppm", sa.Float, nullable=True),
        sa.Column("sulfur_ppm", sa.Float, nullable=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="home_kit"),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_soil_tests_grow_cycle_id", "soil_tests", ["grow_cycle_id"])
    op.create_index("ix_soil_tests_tested_at", "soil_tests", ["tested_at"])

    # -- Soil Amendments --
    op.create_table(
        "soil_amendments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("amendment_type", sa.String(100), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("quantity", sa.String(255), nullable=True),
        sa.Column("area_applied", sa.String(255), nullable=True),
        sa.Column("cost", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_soil_amendments_grow_cycle_id", "soil_amendments", ["grow_cycle_id"])

    # -- Pest Scout Entries --
    op.create_table(
        "pest_scout_entries",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scouted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("pest_type", sa.String(50), nullable=False),
        sa.Column("species", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False, server_default="low"),
        sa.Column("grid_row", sa.Integer, nullable=True),
        sa.Column("grid_col", sa.Integer, nullable=True),
        sa.Column("photo_url", sa.String(1024), nullable=True),
        sa.Column("treatment_applied", sa.String(255), nullable=True),
        sa.Column("treatment_type", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_pest_scout_entries_grow_cycle_id", "pest_scout_entries", ["grow_cycle_id"])
    op.create_index("ix_pest_scout_entries_scouted_at", "pest_scout_entries", ["scouted_at"])

    # -- Harvest Yields (per-plant outdoor tracking) --
    op.create_table(
        "harvest_yields",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), sa.ForeignKey("grow_cycles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bucket_id", UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("harvested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("wet_weight_oz", sa.Float, nullable=True),
        sa.Column("dry_weight_oz", sa.Float, nullable=True),
        sa.Column("trim_weight_oz", sa.Float, nullable=True),
        sa.Column("quality_rating", sa.Integer, nullable=True),
        sa.Column("trichome_stage", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_harvest_yields_grow_cycle_id", "harvest_yields", ["grow_cycle_id"])
    op.create_index("ix_harvest_yields_bucket_id", "harvest_yields", ["bucket_id"])

    # -- Extend buckets for outdoor grid placement --
    op.add_column("buckets", sa.Column("grid_row", sa.Integer, nullable=True))
    op.add_column("buckets", sa.Column("grid_col", sa.Integer, nullable=True))
    op.add_column("buckets", sa.Column("plant_spacing_in", sa.Integer, nullable=True))
    op.add_column("buckets", sa.Column("companion_plants", sa.JSON, nullable=True))
    op.add_column("buckets", sa.Column("sun_zone", sa.String(50), nullable=True))
    op.add_column("buckets", sa.Column("planting_method", sa.String(50), nullable=True))
    op.add_column("buckets", sa.Column("transplant_date", sa.Date, nullable=True))

    # -- RLS policies for all new tables --
    for table in ("plot_grids", "plot_cells", "soil_tests", "soil_amendments", "pest_scout_entries", "harvest_yields"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation_{table} ON {table} "
            f"USING (tenant_id = current_setting('app.current_tenant')::uuid)"
        )


def downgrade() -> None:
    for table in ("harvest_yields", "pest_scout_entries", "soil_amendments", "soil_tests", "plot_cells", "plot_grids"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_{table} ON {table}")

    op.drop_column("buckets", "transplant_date")
    op.drop_column("buckets", "planting_method")
    op.drop_column("buckets", "sun_zone")
    op.drop_column("buckets", "companion_plants")
    op.drop_column("buckets", "plant_spacing_in")
    op.drop_column("buckets", "grid_col")
    op.drop_column("buckets", "grid_row")

    op.drop_index("ix_harvest_yields_bucket_id", table_name="harvest_yields")
    op.drop_index("ix_harvest_yields_grow_cycle_id", table_name="harvest_yields")
    op.drop_table("harvest_yields")

    op.drop_index("ix_pest_scout_entries_scouted_at", table_name="pest_scout_entries")
    op.drop_index("ix_pest_scout_entries_grow_cycle_id", table_name="pest_scout_entries")
    op.drop_table("pest_scout_entries")

    op.drop_index("ix_soil_amendments_grow_cycle_id", table_name="soil_amendments")
    op.drop_table("soil_amendments")

    op.drop_index("ix_soil_tests_tested_at", table_name="soil_tests")
    op.drop_index("ix_soil_tests_grow_cycle_id", table_name="soil_tests")
    op.drop_table("soil_tests")

    op.drop_index("ix_plot_cells_plot_grid_id", table_name="plot_cells")
    op.drop_table("plot_cells")

    op.drop_index("ix_plot_grids_grow_cycle_id", table_name="plot_grids")
    op.drop_table("plot_grids")
