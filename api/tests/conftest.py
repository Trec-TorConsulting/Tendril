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
    from app.automation.models import AlertHistory, AutomationRule, EnvironmentSchedule  # noqa: F401
    from app.commercial.models import ApiKey, AuditLog, CustomGrowType, Task  # noqa: F401
    from app.database import Base
    from app.grows.models import (  # noqa: F401
        Bucket,
        BucketPhoto,
        BucketSensorReading,
        ContainerProfile,
        DoseProfile,
        FeedingSchedule,
        GrowCycle,
        GrowPhoto,
        GrowTypeProfile,
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

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(_setup_db):
    """Yield a DB session per test. Uses the app's session factory."""
    from app.database import async_session_factory

    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables(_setup_db):
    """Truncate all tables after each test for isolation."""
    yield
    from app.database import async_session_factory

    async with async_session_factory() as session:
        await session.execute(
            text(
                "DO $$ DECLARE r RECORD; BEGIN "
                "FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP "
                "EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE'; "
                "END LOOP; END $$;"
            )
        )
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
