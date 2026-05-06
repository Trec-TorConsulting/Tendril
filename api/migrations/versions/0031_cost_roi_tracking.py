"""cost_roi_tracking

Revision ID: 0031
Revises: 0030
Create Date: 2026-05-06
"""

import sqlalchemy as sa  # noqa: F401
from alembic import op
from sqlalchemy.dialects.postgresql import UUID  # noqa: F401

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Expense category enum (idempotent — asyncpg doesn't support checkfirst)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE expense_category AS ENUM (
                'nutrients', 'electricity', 'water', 'equipment',
                'labor', 'rent', 'supplies', 'other'
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Expenses table
    op.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            grow_cycle_id UUID NOT NULL REFERENCES grow_cycles(id) ON DELETE CASCADE,
            category expense_category NOT NULL,
            amount_cents INTEGER NOT NULL,
            currency VARCHAR(3) DEFAULT 'usd',
            description VARCHAR(255),
            vendor VARCHAR(255),
            date TIMESTAMPTZ DEFAULT now(),
            is_recurring BOOLEAN DEFAULT false,
            recurring_interval VARCHAR(20),
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_expenses_tenant_id ON expenses(tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_expenses_grow_cycle_id ON expenses(grow_cycle_id)")

    # Harvest values table
    op.execute("""
        CREATE TABLE IF NOT EXISTS harvest_values (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
            grow_cycle_id UUID NOT NULL REFERENCES grow_cycles(id) ON DELETE CASCADE,
            grade VARCHAR(20) NOT NULL,
            weight_g DOUBLE PRECISION NOT NULL,
            price_per_gram_cents INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_harvest_values_tenant_id ON harvest_values(tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_harvest_values_grow_cycle_id ON harvest_values(grow_cycle_id)")

    # RLS policies
    op.execute("ALTER TABLE expenses ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS expenses_tenant_isolation ON expenses")
    op.execute("""
        CREATE POLICY expenses_tenant_isolation ON expenses
            USING (tenant_id::text = current_setting('app.current_tenant', true))
    """)
    op.execute("ALTER TABLE harvest_values ENABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS harvest_values_tenant_isolation ON harvest_values")
    op.execute("""
        CREATE POLICY harvest_values_tenant_isolation ON harvest_values
            USING (tenant_id::text = current_setting('app.current_tenant', true))
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS harvest_values_tenant_isolation ON harvest_values")
    op.execute("ALTER TABLE harvest_values DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS expenses_tenant_isolation ON expenses")
    op.execute("ALTER TABLE expenses DISABLE ROW LEVEL SECURITY")
    op.drop_table("harvest_values")
    op.drop_table("expenses")
    op.execute("DROP TYPE IF EXISTS expense_category")
