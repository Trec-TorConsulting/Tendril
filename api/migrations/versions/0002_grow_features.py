"""Phase 3 — grow features schema

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Tents ---
    op.create_table(
        "tents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("environment_type", sa.String(50), server_default="indoor"),
        sa.Column("latitude", sa.Float),
        sa.Column("longitude", sa.Float),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tents_tenant_id", "tents", ["tenant_id"])

    # --- Grow Cycles ---
    op.create_table(
        "grow_cycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "tent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tents.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("grow_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("stage", sa.String(50), server_default="seedling"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text),
        sa.Column("settings", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_grow_cycles_tenant_id", "grow_cycles", ["tenant_id"])
    op.create_index("ix_grow_cycles_tent_id", "grow_cycles", ["tent_id"])

    # --- Buckets ---
    op.create_table(
        "buckets",
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
        sa.Column("position", sa.Integer, server_default="1"),
        sa.Column("label", sa.String(255)),
        sa.Column("strain_name", sa.String(255)),
        sa.Column("growth_stage", sa.String(50), server_default="seedling"),
        sa.Column("status", sa.String(50), server_default="active"),
        sa.Column("settings", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_buckets_tenant_id", "buckets", ["tenant_id"])
    op.create_index("ix_buckets_grow_cycle_id", "buckets", ["grow_cycle_id"])

    # --- Bucket Sensor Readings ---
    op.create_table(
        "bucket_sensor_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("device_id", sa.String(100)),
        sa.Column("water_temp_f", sa.Float),
        sa.Column("ph", sa.Float),
        sa.Column("ec", sa.Float),
        sa.Column("ppm", sa.Float),
        sa.Column("water_level_pct", sa.Float),
        sa.Column("dissolved_oxygen", sa.Float),
        sa.Column("flow_rate", sa.Float),
        sa.Column("mist_pressure", sa.Float),
        sa.Column("soil_moisture", sa.Float),
        sa.Column("soil_temp", sa.Float),
        sa.Column("runoff_ph", sa.Float),
        sa.Column("runoff_ec", sa.Float),
        sa.Column("ambient_temp_f", sa.Float),
        sa.Column("ambient_humidity", sa.Float),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_bsr_tenant_id", "bucket_sensor_readings", ["tenant_id"])
    op.create_index("ix_bsr_bucket_id", "bucket_sensor_readings", ["bucket_id"])
    op.create_index("ix_bsr_recorded_at", "bucket_sensor_readings", ["recorded_at"])

    # --- Journal Entries ---
    op.create_table(
        "journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("content", sa.Text),
        sa.Column("payload", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_journal_entries_tenant_id", "journal_entries", ["tenant_id"])
    op.create_index("ix_journal_entries_bucket_id", "journal_entries", ["bucket_id"])

    # --- Bucket Photos ---
    op.create_table(
        "bucket_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("caption", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_bucket_photos_tenant_id", "bucket_photos", ["tenant_id"])
    op.create_index("ix_bucket_photos_bucket_id", "bucket_photos", ["bucket_id"])

    # --- Dose Profiles ---
    op.create_table(
        "dose_profiles",
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
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dose_type", sa.String(50), nullable=False),
        sa.Column("dose_ml", sa.Float, nullable=False),
        sa.Column("enabled", sa.Boolean, server_default="true"),
        sa.Column("settings", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_dose_profiles_tenant_id", "dose_profiles", ["tenant_id"])

    # --- Feeding Schedules ---
    op.create_table(
        "feeding_schedules",
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
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("nutrients", postgresql.JSON, nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_feeding_schedules_tenant_id", "feeding_schedules", ["tenant_id"])

    # --- Strains ---
    op.create_table(
        "strains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("breeder", sa.String(255)),
        sa.Column("genetics", sa.String(255)),
        sa.Column("flowering_days", sa.Integer),
        sa.Column("thc_pct", sa.Float),
        sa.Column("cbd_pct", sa.Float),
        sa.Column("terpene_profile", postgresql.JSON),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_strains_tenant_id", "strains", ["tenant_id"])

    # --- Yields ---
    op.create_table(
        "yields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "bucket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buckets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("wet_weight_g", sa.Float),
        sa.Column("dry_weight_g", sa.Float),
        sa.Column("trim_weight_g", sa.Float),
        sa.Column("quality_rating", sa.Integer),
        sa.Column("terpene_notes", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("harvest_date", sa.DateTime(timezone=True)),
        sa.Column("dry_start", sa.DateTime(timezone=True)),
        sa.Column("dry_end", sa.DateTime(timezone=True)),
        sa.Column("cure_start", sa.DateTime(timezone=True)),
        sa.Column("cure_end", sa.DateTime(timezone=True)),
        sa.Column("dry_environment", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_yields_tenant_id", "yields", ["tenant_id"])
    op.create_index("ix_yields_bucket_id", "yields", ["bucket_id"])

    # --- Weather Readings ---
    op.create_table(
        "weather_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "tent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tents.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("temperature_c", sa.Float),
        sa.Column("humidity_pct", sa.Float),
        sa.Column("precipitation_mm", sa.Float),
        sa.Column("wind_speed_kmh", sa.Float),
        sa.Column("uv_index", sa.Float),
        sa.Column("weather_code", sa.Integer),
        sa.Column("forecast", postgresql.JSON),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_weather_readings_tenant_id", "weather_readings", ["tenant_id"])
    op.create_index("ix_weather_readings_tent_id", "weather_readings", ["tent_id"])

    # --- Grow Type Profiles (seed data — no tenant_id, read-only) ---
    op.create_table(
        "grow_type_profiles",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("terminology", postgresql.JSON, nullable=False),
        sa.Column("sensor_kit", sa.String(100), nullable=False),
        sa.Column("relevant_sensors", postgresql.JSON, nullable=False),
        sa.Column("primary_sensors", postgresql.JSON, nullable=False),
        sa.Column("irrelevant_sensors", postgresql.JSON, nullable=False),
        sa.Column("unique_fields", postgresql.JSON, nullable=False),
        sa.Column("ph_range", postgresql.JSON, nullable=False),
        sa.Column("ec_range", postgresql.JSON, nullable=False),
        sa.Column("health_check_questions", postgresql.JSON, nullable=False),
        sa.Column("automations", postgresql.JSON, nullable=False),
        sa.Column("feeding_approach", sa.Text, nullable=False),
        sa.Column("nutrient_strength", sa.String(50), nullable=False),
        sa.Column("common_problems", postgresql.JSON, nullable=False),
        sa.Column("ai_prompt_context", sa.Text, nullable=False),
    )

    # --- Reference Strains ---
    op.create_table(
        "reference_strains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("breeder", sa.String(255)),
        sa.Column("genetics", sa.String(255)),
        sa.Column("thc_pct", sa.Float),
        sa.Column("cbd_pct", sa.Float),
        sa.Column("description", sa.Text),
        sa.Column("external_id", sa.String(255), unique=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reference_strains_name", "reference_strains", ["name"])

    # --- Nutrient Products ---
    op.create_table(
        "nutrient_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("barcode", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(255)),
        sa.Column("npk", sa.String(50)),
        sa.Column("nutrients", postgresql.JSON),
        sa.Column("image_url", sa.String(1024)),
        sa.Column("source", sa.String(50), server_default="open_food_facts"),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- RLS Policies for all tenant-scoped tables ---
    tenant_tables = [
        "tents",
        "grow_cycles",
        "buckets",
        "bucket_sensor_readings",
        "journal_entries",
        "bucket_photos",
        "dose_profiles",
        "feeding_schedules",
        "strains",
        "yields",
        "weather_readings",
    ]
    for table in tenant_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation_{table} ON {table}
                USING (tenant_id = current_setting('app.current_tenant')::UUID)
        """)


def downgrade() -> None:
    tables = [
        "nutrient_products",
        "reference_strains",
        "grow_type_profiles",
        "weather_readings",
        "yields",
        "strains",
        "feeding_schedules",
        "dose_profiles",
        "bucket_photos",
        "journal_entries",
        "bucket_sensor_readings",
        "buckets",
        "grow_cycles",
        "tents",
    ]
    for table in tables:
        op.drop_table(table)
