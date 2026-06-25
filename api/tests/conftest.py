"""Pytest configuration — fixtures for test DB, tenant factory, and auth helpers."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Set test env vars before importing app
os.environ["JWT_SECRET"] = "test-secret-do-not-use-in-production"  # noqa: S105
os.environ["DATABASE_URL"] = "postgresql+asyncpg://tendril:tendril@localhost:5432/tendril_test"
os.environ["INTEGRATION_ENCRYPTION_KEY"] = "m8eWk-kF4nPTdc7Y0wccVuqqEYTUvrAWdVcF5zKBuo0="


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def _setup_db():
    """One-time DB schema setup. Creates all tables at session start, drops at end."""
    from app.ai.models import AgentAction, AgentActionApproval, Conversation, ConversationMessage  # noqa: F401
    from app.automation.models import AlertHistory, AutomationRule, EnvironmentSchedule  # noqa: F401
    from app.billing.models import (  # noqa: F401
        BillingOverageRate,
        BillingPaygRate,
        BillingPlan,
        BillingPlanPrice,
        BillingUsageRecord,
        PaymentProvider,
    )
    from app.commercial.models import ApiKey, AuditLog, CustomGrowType, Task  # noqa: F401
    from app.config_management import (  # noqa: F401
        GrowTypeEnvironment,
        GrowTypeEquipment,
        GrowTypeNutrient,
        GrowTypeProfile,
        GrowTypeStage,
        GrowTypeTroubleshooting,
        GrowTypeWatering,
        TaskTemplate,
        TaskTemplateStep,
        TenantConfigOverride,
    )
    from app.database import Base
    from app.equipment.models import ControllableEquipment, EquipmentStateLog  # noqa: F401
    from app.grows.models import (  # noqa: F401
        Bucket,
        BucketPhoto,
        BucketSensorReading,
        ContainerProfile,
        DoseProfile,
        FeedingSchedule,
        GrowCycle,
        GrowPhoto,
        HarvestYield,
        HealthEval,
        JournalEntry,
        NutrientProduct,
        PestScoutEntry,
        PlotCell,
        PlotGrid,
        ReferenceStrain,
        RunoffReading,
        SoilAmendment,
        SoilTest,
        Strain,
        Tent,
        TentCamera,
        TentSensorReading,
        WeatherReading,
        Yield,
    )
    from app.integrations.models import IntegrationConfig, IntegrationDeviceMap, IntegrationSyncLog  # noqa: F401
    from app.notifications.models import (  # noqa: F401
        NotificationChannel,
        NotificationLog,
        NotificationPreference,
        PushSubscription,
    )

    # Import ALL models so metadata.create_all picks them up
    from app.tenants.models import (  # noqa: F401
        Account,
        AccountMember,
        Device,
        MembershipGrowAccess,
        Tenant,
        TenantMembership,
        User,
    )

    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("ALTER TABLE devices ENABLE ROW LEVEL SECURITY"))
        await conn.execute(
            text(
                "CREATE POLICY tenant_isolation_devices ON devices "
                "USING (tenant_id = current_setting('app.current_tenant')::UUID)"
            )
        )
        await conn.execute(text("ALTER TABLE tenant_memberships ENABLE ROW LEVEL SECURITY"))
        await conn.execute(
            text(
                "CREATE POLICY tenant_isolation_memberships ON tenant_memberships "
                "USING (tenant_id = current_setting('app.current_tenant')::UUID)"
            )
        )

        # The raw-SQL seeders in app.config_management.seed rely on
        # server-side defaults for created_at/updated_at (production gets
        # them from Alembic migrations). Base.metadata.create_all uses the
        # Python-side defaults instead, so add the server defaults here —
        # conditionally per (table, column) since not every reference
        # table has both columns.
        await conn.execute(
            text(
                "DO $$ DECLARE r RECORD; BEGIN "
                "FOR r IN ("
                "  SELECT table_name, column_name FROM information_schema.columns "
                "  WHERE table_schema = 'public' "
                "  AND column_name IN ('created_at', 'updated_at')"
                ") LOOP "
                "  EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || "
                "    ' ALTER COLUMN ' || quote_ident(r.column_name) || ' SET DEFAULT now()'; "
                "END LOOP; END $$;"
            )
        )

    # Seed reference data once (grow type profiles, task templates, etc.)
    # so tests that exercise endpoints depending on it don't fail when the
    # seed lifespan hook is bypassed. Truncation in ``_clean_tables`` skips
    # these tables.
    #
    # Only the seeders backed by SQLAlchemy models are run here; the rest
    # (stage_transition_tasks, automation_suppressions, etc.) target tables
    # that only exist in Alembic migrations and aren't created by
    # ``Base.metadata.create_all``. They aren't exercised by the test suite.
    from app.config_management import seed as _seed
    from app.database import async_session_factory

    async with async_session_factory() as session:
        await _seed.seed_grow_type_profiles(session)
        await _seed.seed_grow_type_stages(session)
        await _seed.seed_grow_type_equipment(session)
        await _seed.seed_grow_type_troubleshooting(session)
        await _seed.seed_task_templates(session)
        await session.commit()

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# Reference / seed tables that should NOT be truncated between tests.
# They are seeded once in `_setup_db` and shared across every test.
_REFERENCE_TABLES = {
    "grow_type_profiles",
    "grow_type_stages",
    "grow_type_environment",
    "grow_type_nutrients",
    "grow_type_watering",
    "grow_type_equipment",
    "grow_type_troubleshooting",
    "task_templates",
    "task_template_steps",
    "automation_suppressions",
    "companion_plants",
    "feed_charts",
    "nutrient_knowledge",
    "esphome_templates",
}


@pytest_asyncio.fixture
async def db_session(_setup_db):
    """Yield a DB session per test. Uses the app's session factory."""
    from app.database import async_session_factory

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(_setup_db):
    """Truncate per-test tables after each test for isolation. Reference
    (seed) tables are preserved — they're populated once in ``_setup_db``."""
    yield
    from app.database import async_session_factory

    skip_list = ",".join(f"'{name}'" for name in _REFERENCE_TABLES)
    async with async_session_factory() as session:
        # Hardcoded table names from a module-level constant — not user input.
        truncate_sql = (
            "DO $$ DECLARE r RECORD; BEGIN "  # noqa: S608
            "FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
            f"AND tablename NOT IN ({skip_list})) LOOP "
            "EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE'; "
            "END LOOP; END $$;"
        )
        await session.execute(text(truncate_sql))
        await session.commit()


@pytest_asyncio.fixture
async def client(_setup_db):
    """Async test client for the FastAPI app."""
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "test-csrf-token"},
    ) as ac:
        yield ac


class TenantFactory:
    """Helper to create test tenants + users with tokens."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str = "Test Org", plan: str = "free") -> dict:
        import bcrypt

        from app.auth.jwt import create_access_token
        from app.tenants.models import (
            Account,
            AccountMember,
            AccountRole,
            PlatformRole,
            Tenant,
            TenantMembership,
            TenantRole,
            User,
        )

        # Create account
        account = Account(name=name, billing_email=f"billing-{uuid4().hex[:8]}@test.com")
        self.session.add(account)
        await self.session.flush()

        # Create tenant
        tenant = Tenant(name=name, slug=f"test-{uuid4().hex[:8]}", plan=plan, account_id=account.id)
        self.session.add(tenant)
        await self.session.flush()

        # Create user
        password = "testpass123"  # noqa: S105
        user = User(
            email=f"user-{uuid4().hex[:8]}@test.com",
            password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            display_name="Test User",
            platform_role=PlatformRole.user,
        )
        self.session.add(user)
        await self.session.flush()

        # Account membership
        account_member = AccountMember(
            account_id=account.id,
            user_id=user.id,
            role=AccountRole.owner,
        )
        self.session.add(account_member)

        # Tenant membership
        membership = TenantMembership(
            tenant_id=tenant.id,
            user_id=user.id,
            role=TenantRole.admin,
        )
        self.session.add(membership)
        await self.session.commit()
        await self.session.refresh(tenant)
        await self.session.refresh(user)

        token = create_access_token(
            user.id,
            platform_role=user.platform_role.value,
            tenant_id=tenant.id,
            tenant_role=TenantRole.admin.value,
            account_id=account.id,
        )

        return {
            "tenant": tenant,
            "user": user,
            "account": account,
            "token": token,
            "password": password,
            "headers": {
                "Authorization": f"Bearer {token}",
                "X-CSRF-Token": "test-csrf-token",
            },
        }


@pytest_asyncio.fixture
async def tenant_factory(db_session):
    return TenantFactory(db_session)


@pytest_asyncio.fixture
async def db_tenant(db_session):
    """Create a real, persisted tenant + owner user. Useful for tests that need
    to persist tenant-scoped rows (e.g. ControllableEquipment) via the session
    fixture rather than going through the HTTP client."""
    factory = TenantFactory(db_session)
    return await factory.create()
