"""Enterprise RBAC: accounts, tenant_memberships, grow_access, platform_role enum.

Revision ID: 0024
Revises: 0023
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── Create enum types ─────────────────────────────────────────────────────
    platform_role_enum = sa.Enum(
        "super_admin", "support", "readonly_admin", "user",
        name="platform_role",
    )
    platform_role_enum.create(op.get_bind(), checkfirst=True)

    tenant_role_enum = sa.Enum("admin", "member", "viewer", name="tenant_role")
    tenant_role_enum.create(op.get_bind(), checkfirst=True)

    account_role_enum = sa.Enum("owner", "billing_admin", name="account_role")
    account_role_enum.create(op.get_bind(), checkfirst=True)

    # ─── Create accounts table ─────────────────────────────────────────────────
    op.create_table(
        "accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("billing_email", sa.String(255), nullable=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ─── Create account_members table ──────────────────────────────────────────
    op.create_table(
        "account_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", UUID(as_uuid=True), sa.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", account_role_enum, nullable=False, server_default="owner"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("account_id", "user_id"),
    )

    # ─── Add account_id to tenants ────────────────────────────────────────────
    op.add_column("tenants", sa.Column("account_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_tenants_account_id", "tenants", "accounts",
        ["account_id"], ["id"], ondelete="SET NULL",
    )

    # ─── Create tenant_memberships table ───────────────────────────────────────
    op.create_table(
        "tenant_memberships",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", tenant_role_enum, nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "user_id"),
    )

    # ─── Create membership_grow_access table ───────────────────────────────────
    op.create_table(
        "membership_grow_access",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "membership_id", UUID(as_uuid=True),
            sa.ForeignKey("tenant_memberships.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("grow_cycle_id", UUID(as_uuid=True), nullable=False),
        sa.UniqueConstraint("membership_id", "grow_cycle_id"),
    )

    # ─── Add platform_role column to users ─────────────────────────────────────
    op.add_column(
        "users",
        sa.Column("platform_role", platform_role_enum, nullable=False, server_default="user"),
    )

    # ─── Data migration: backfill platform_role from boolean flags ─────────────
    op.execute("""
        UPDATE users SET platform_role = 'super_admin'
        WHERE is_platform_admin = true
    """)
    op.execute("""
        UPDATE users SET platform_role = 'support'
        WHERE is_support = true AND is_platform_admin = false
    """)

    # ─── Data migration: create Account per Tenant, move Stripe fields ─────────
    # For each tenant that has at least one owner, create an Account
    op.execute("""
        INSERT INTO accounts (id, name, billing_email, stripe_customer_id, stripe_subscription_id, created_at)
        SELECT
            t.id,  -- reuse tenant UUID as account UUID for simplicity
            t.name,
            (SELECT u.email FROM users u WHERE u.tenant_id = t.id AND u.role = 'owner' LIMIT 1),
            t.stripe_customer_id,
            t.stripe_subscription_id,
            t.created_at
        FROM tenants t
    """)

    # ─── Set tenants.account_id ────────────────────────────────────────────────
    op.execute("""
        UPDATE tenants SET account_id = id
    """)

    # ─── Data migration: create AccountMember for each existing owner ──────────
    op.execute("""
        INSERT INTO account_members (id, account_id, user_id, role, created_at)
        SELECT
            gen_random_uuid(),
            u.tenant_id,  -- account_id = tenant_id (reused UUID)
            u.id,
            'owner',
            u.created_at
        FROM users u
        WHERE u.role = 'owner'
    """)

    # ─── Data migration: create TenantMembership from existing users ───────────
    op.execute("""
        INSERT INTO tenant_memberships (id, tenant_id, user_id, role, created_at)
        SELECT
            gen_random_uuid(),
            u.tenant_id,
            u.id,
            CASE
                WHEN u.role = 'owner' THEN 'admin'
                WHEN u.role = 'member' THEN 'member'
                WHEN u.role = 'viewer' THEN 'viewer'
                ELSE 'member'
            END::tenant_role,
            u.created_at
        FROM users u
        WHERE u.tenant_id IS NOT NULL
    """)

    # ─── Drop old columns from users ──────────────────────────────────────────
    op.drop_constraint("users_tenant_id_fkey", "users", type_="foreignkey")
    op.drop_column("users", "tenant_id")
    op.drop_column("users", "role")
    op.drop_column("users", "is_platform_admin")
    op.drop_column("users", "is_support")

    # ─── Drop old Stripe columns from tenants ──────────────────────────────────
    op.drop_column("tenants", "stripe_customer_id")
    op.drop_column("tenants", "stripe_subscription_id")


def downgrade() -> None:
    # ─── Re-add old columns to tenants ─────────────────────────────────────────
    op.add_column("tenants", sa.Column("stripe_customer_id", sa.String(255), nullable=True))
    op.add_column("tenants", sa.Column("stripe_subscription_id", sa.String(255), nullable=True))

    # ─── Re-add old columns to users ──────────────────────────────────────────
    op.add_column("users", sa.Column("is_support", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("is_platform_admin", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("role", sa.String(50), server_default="owner", nullable=False))
    op.add_column("users", sa.Column("tenant_id", UUID(as_uuid=True), nullable=True))

    # ─── Restore data from new tables ──────────────────────────────────────────
    op.execute("""
        UPDATE users u SET
            tenant_id = tm.tenant_id,
            role = CASE
                WHEN tm.role = 'admin' THEN 'owner'
                WHEN tm.role = 'member' THEN 'member'
                WHEN tm.role = 'viewer' THEN 'viewer'
                ELSE 'member'
            END
        FROM tenant_memberships tm
        WHERE tm.user_id = u.id
        AND tm.id = (
            SELECT id FROM tenant_memberships
            WHERE user_id = u.id
            ORDER BY created_at LIMIT 1
        )
    """)
    op.execute("""
        UPDATE users SET is_platform_admin = true WHERE platform_role = 'super_admin'
    """)
    op.execute("""
        UPDATE users SET is_support = true WHERE platform_role = 'support'
    """)

    # ─── Restore tenants stripe fields ─────────────────────────────────────────
    op.execute("""
        UPDATE tenants t SET
            stripe_customer_id = a.stripe_customer_id,
            stripe_subscription_id = a.stripe_subscription_id
        FROM accounts a
        WHERE a.id = t.account_id
    """)

    # ─── Re-add FK constraint ──────────────────────────────────────────────────
    op.create_foreign_key(
        "users_tenant_id_fkey", "users", "tenants",
        ["tenant_id"], ["id"], ondelete="CASCADE",
    )

    # ─── Drop new tables ──────────────────────────────────────────────────────
    op.drop_table("membership_grow_access")
    op.drop_table("tenant_memberships")
    op.drop_constraint("fk_tenants_account_id", "tenants", type_="foreignkey")
    op.drop_column("tenants", "account_id")
    op.drop_table("account_members")
    op.drop_table("accounts")

    # ─── Drop platform_role column and enum types ──────────────────────────────
    op.drop_column("users", "platform_role")
    sa.Enum(name="platform_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tenant_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="account_role").drop(op.get_bind(), checkfirst=True)
