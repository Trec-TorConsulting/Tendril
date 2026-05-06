"""Add billing plans, payment providers, usage metering tables.

Revision ID: 0029
Revises: 0028_task_routine_duration
Create Date: 2026-05-05
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB, UUID

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums — use raw DDL with IF NOT EXISTS for async driver compatibility
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            "CREATE TYPE provider_type AS ENUM ('stripe', 'paypal', 'square', 'paddle'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            "CREATE TYPE billing_model_enum AS ENUM ('flat', 'tiered_usage', 'pay_as_you_go'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            "CREATE TYPE sync_status_enum AS ENUM ('pending', 'synced', 'error'); "
            "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
        )
    )

    provider_type_enum = ENUM("stripe", "paypal", "square", "paddle", name="provider_type", create_type=False)
    billing_model_enum = ENUM("flat", "tiered_usage", "pay_as_you_go", name="billing_model_enum", create_type=False)
    sync_status_enum = ENUM("pending", "synced", "error", name="sync_status_enum", create_type=False)

    # Payment Providers
    op.create_table(
        "payment_providers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("provider_type", provider_type_enum, nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false"),
        sa.Column("is_primary", sa.Boolean(), server_default="false"),
        sa.Column("config_encrypted", sa.LargeBinary(), nullable=False),
        sa.Column("webhook_secret_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("supported_methods", ARRAY(sa.String(50)), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Billing Plans
    op.create_table(
        "billing_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("slug", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_public", sa.Boolean(), server_default="true"),
        sa.Column("sort_order", sa.Integer(), server_default="0"),
        sa.Column("billing_model", billing_model_enum, server_default="flat"),
        sa.Column("base_price_cents", sa.Integer(), server_default="0"),
        sa.Column("annual_price_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(3), server_default=sa.text("'usd'")),
        # Feature limits
        sa.Column("max_grows", sa.Integer(), nullable=True),
        sa.Column("max_devices", sa.Integer(), nullable=True),
        sa.Column("max_team_members", sa.Integer(), nullable=True),
        sa.Column("max_ai_analyses_month", sa.Integer(), nullable=True),
        sa.Column("max_storage_gb", sa.Integer(), nullable=True),
        sa.Column("max_automations", sa.Integer(), nullable=True),
        sa.Column("max_integrations", sa.Integer(), nullable=True),
        sa.Column("max_journal_entries_month", sa.Integer(), nullable=True),
        sa.Column("data_retention_days", sa.Integer(), nullable=True),
        sa.Column("included_support_tier", sa.String(20), server_default=sa.text("'community'")),
        sa.Column("features_json", JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Plan ↔ Provider price mapping
    op.create_table(
        "billing_plan_prices",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "provider_id",
            UUID(as_uuid=True),
            sa.ForeignKey("payment_providers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_product_id", sa.String(255), nullable=True),
        sa.Column("external_price_id", sa.String(255), nullable=True),
        sa.Column("external_annual_price_id", sa.String(255), nullable=True),
        sa.Column("sync_status", sync_status_enum, server_default=sa.text("'pending'")),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_error", sa.Text(), nullable=True),
        sa.UniqueConstraint("plan_id", "provider_id"),
    )

    # Overage rates
    op.create_table(
        "billing_overage_rates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("billing_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric", sa.String(50), nullable=False),
        sa.Column("unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.UniqueConstraint("plan_id", "metric"),
    )

    # PAYG rates
    op.create_table(
        "billing_payg_rates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("metric", sa.String(50), unique=True, nullable=False),
        sa.Column("unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # Usage records
    op.create_table(
        "billing_usage_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", UUID(as_uuid=True), sa.ForeignKey("billing_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metric", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="0"),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("reported_to_provider", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "metric", "period_start"),
    )

    # Add billing_model column to tenants
    op.add_column("tenants", sa.Column("billing_model", billing_model_enum, server_default=sa.text("'flat'")))
    op.add_column("tenants", sa.Column("custom_domain", sa.String(255), nullable=True))

    # Seed default plans
    op.execute("""
        INSERT INTO billing_plans (slug, name, description, sort_order, base_price_cents, annual_price_cents,
            max_grows, max_devices, max_team_members, max_ai_analyses_month, max_storage_gb,
            max_automations, max_integrations, max_journal_entries_month, data_retention_days,
            included_support_tier, features_json)
        VALUES
        ('free', 'Seedling', 'Perfect for getting started with your first grow', 0, 0, NULL,
            1, 2, 1, 10, 1, 2, 1, 50, 90,
            'community', '{"data_export": false, "custom_grow_types": false, "api_keys": false, "audit_trail": false}'),
        ('hobby', 'Sprout', 'For home growers expanding their garden', 1, 999, 9590,
            3, 5, 1, 50, 5, 10, 3, NULL, 365,
            'email', '{"data_export": true, "custom_grow_types": false, "api_keys": false, "audit_trail": false}'),
        ('pro', 'Canopy', 'Serious cultivators who want full control', 2, 2999, 28790,
            NULL, 20, 5, 200, 25, 50, NULL, NULL, 730,
            'priority', '{"data_export": true, "custom_grow_types": true, "api_keys": true, "audit_trail": false, "live_chat": true}'),
        ('commercial', 'Grove', 'Small businesses and commercial operations', 3, 7999, 76790,
            NULL, 100, 25, 1000, 100, NULL, NULL, NULL, 1825,
            'priority', '{"data_export": true, "custom_grow_types": true, "api_keys": true, "audit_trail": true, "live_chat": true, "white_label_reports": true, "advanced_analytics": true}'),
        ('enterprise', 'Forest', 'Large operations with custom needs', 4, 0, NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            'dedicated', '{"data_export": true, "custom_grow_types": true, "api_keys": true, "audit_trail": true, "live_chat": true, "sso_saml": true, "compliance": true, "custom_integrations": true}'),
        ('dedicated', 'Greenhouse', 'Fully isolated infrastructure hosted by Trec-Tor Consulting', 5, 0, NULL,
            NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
            'dedicated', '{"data_export": true, "custom_grow_types": true, "api_keys": true, "audit_trail": true, "live_chat": true, "sso_saml": true, "compliance": true, "custom_integrations": true, "dedicated_infra": true, "custom_domain": true, "white_label": true}')
    """)

    # Seed overage rates (for tiered_usage model)
    op.execute("""
        INSERT INTO billing_overage_rates (plan_id, metric, unit_price_cents, description)
        SELECT id, 'ai_analyses', 5, '$0.05 per analysis over limit' FROM billing_plans WHERE slug = 'hobby'
        UNION ALL
        SELECT id, 'storage_gb', 50, '$0.50 per GB over limit' FROM billing_plans WHERE slug = 'hobby'
        UNION ALL
        SELECT id, 'devices', 100, '$1.00 per device over limit' FROM billing_plans WHERE slug = 'hobby'
        UNION ALL
        SELECT id, 'ai_analyses', 5, '$0.05 per analysis over limit' FROM billing_plans WHERE slug = 'pro'
        UNION ALL
        SELECT id, 'storage_gb', 50, '$0.50 per GB over limit' FROM billing_plans WHERE slug = 'pro'
        UNION ALL
        SELECT id, 'devices', 100, '$1.00 per device over limit' FROM billing_plans WHERE slug = 'pro'
        UNION ALL
        SELECT id, 'team_members', 500, '$5.00 per member over limit' FROM billing_plans WHERE slug = 'pro'
        UNION ALL
        SELECT id, 'ai_analyses', 5, '$0.05 per analysis over limit' FROM billing_plans WHERE slug = 'commercial'
        UNION ALL
        SELECT id, 'storage_gb', 50, '$0.50 per GB over limit' FROM billing_plans WHERE slug = 'commercial'
        UNION ALL
        SELECT id, 'devices', 100, '$1.00 per device over limit' FROM billing_plans WHERE slug = 'commercial'
        UNION ALL
        SELECT id, 'team_members', 500, '$5.00 per member over limit' FROM billing_plans WHERE slug = 'commercial'
    """)

    # Seed PAYG rates
    op.execute("""
        INSERT INTO billing_payg_rates (metric, unit_price_cents, description) VALUES
        ('ai_analyses', 10, '$0.10 per AI analysis'),
        ('storage_gb', 100, '$1.00 per GB per month'),
        ('devices', 200, '$2.00 per device per month'),
        ('grow_spaces', 500, '$5.00 per grow space per month'),
        ('automations', 50, '$0.50 per automation per month')
    """)

    # Migrate existing tenant plan names: grower → hobby
    op.execute("UPDATE tenants SET plan = 'hobby' WHERE plan = 'grower'")


def downgrade() -> None:
    op.execute("UPDATE tenants SET plan = 'grower' WHERE plan = 'hobby'")
    op.drop_column("tenants", "custom_domain")
    op.drop_column("tenants", "billing_model")
    op.drop_table("billing_usage_records")
    op.drop_table("billing_payg_rates")
    op.drop_table("billing_overage_rates")
    op.drop_table("billing_plan_prices")
    op.drop_table("billing_plans")
    op.drop_table("payment_providers")

    op.execute("DROP TYPE IF EXISTS sync_status_enum")
    op.execute("DROP TYPE IF EXISTS billing_model_enum")
    op.execute("DROP TYPE IF EXISTS provider_type")
