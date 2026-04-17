"""Make strains.tenant_id nullable for global (shared) strains.

Revision ID: 0010
Create Date: 2026-04-17

Global strains have tenant_id IS NULL and are visible to all tenants.
Custom strains have a tenant_id and are only visible to that tenant.
"""
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Make tenant_id nullable (global strains have NULL)
    op.alter_column("strains", "tenant_id", nullable=True)

    # 2. Drop the FK constraint so NULL tenant_id doesn't violate it
    #    Then re-add with nullable support (Postgres FKs already allow NULL, so
    #    we just need the column nullable which we did above)

    # 3. Drop the old RLS policy and create a new one that includes global strains
    op.execute("DROP POLICY IF EXISTS tenant_isolation_strains ON strains")
    op.execute("""
        CREATE POLICY tenant_isolation_strains ON strains
        FOR SELECT
        USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant')::uuid)
    """)
    # Separate policy for INSERT/UPDATE/DELETE — tenant strains only
    op.execute("""
        CREATE POLICY tenant_write_strains ON strains
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant')::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant')::uuid)
    """)

    # 4. Set all existing seeded strains to global (NULL tenant_id)
    op.execute("UPDATE strains SET tenant_id = NULL")


def downgrade() -> None:
    # Revert: assign all global strains to the first tenant
    op.execute("""
        UPDATE strains SET tenant_id = (SELECT id FROM tenants LIMIT 1)
        WHERE tenant_id IS NULL
    """)
    op.alter_column("strains", "tenant_id", nullable=False)
    op.execute("DROP POLICY IF EXISTS tenant_write_strains ON strains")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_strains ON strains")
    op.execute("""
        CREATE POLICY tenant_isolation_strains ON strains
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant')::uuid)
    """)
