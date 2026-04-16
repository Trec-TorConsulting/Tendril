"""Tenant isolation tests — verify RLS prevents cross-tenant data access."""
from __future__ import annotations

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_rls_users_isolation(tenant_factory, db_session):
    """Users from tenant A must not be visible when tenant B's context is set."""
    tenant_a = await tenant_factory.create(name="Tenant A")
    tenant_b = await tenant_factory.create(name="Tenant B")

    # Set tenant context to A and count users
    tid_a = str(tenant_a["tenant"].id)
    await db_session.execute(text(f"SET app.current_tenant = '{tid_a}'"))
    result = await db_session.execute(text("SELECT count(*) FROM users"))
    count_a = result.scalar()
    assert count_a == 1  # Only tenant A's user

    # Set tenant context to B
    tid_b = str(tenant_b["tenant"].id)
    await db_session.execute(text(f"SET app.current_tenant = '{tid_b}'"))
    result = await db_session.execute(text("SELECT count(*) FROM users"))
    count_b = result.scalar()
    assert count_b == 1  # Only tenant B's user


@pytest.mark.asyncio
async def test_rls_devices_isolation(tenant_factory, db_session):
    """Devices from one tenant must not be visible to another."""
    from app.tenants.models import Device

    tenant_a = await tenant_factory.create(name="Device Tenant A")
    tenant_b = await tenant_factory.create(name="Device Tenant B")

    # Add device to tenant A
    device = Device(
        tenant_id=tenant_a["tenant"].id,
        device_id="esp32-001",
        psk_hash="fakehash",
        label="Sensor A",
    )
    db_session.add(device)
    await db_session.commit()

    # Query as tenant B — should see 0 devices
    tid_b = str(tenant_b["tenant"].id)
    await db_session.execute(text(f"SET app.current_tenant = '{tid_b}'"))
    result = await db_session.execute(text("SELECT count(*) FROM devices"))
    assert result.scalar() == 0

    # Query as tenant A — should see 1 device
    tid_a = str(tenant_a["tenant"].id)
    await db_session.execute(text(f"SET app.current_tenant = '{tid_a}'"))
    result = await db_session.execute(text("SELECT count(*) FROM devices"))
    assert result.scalar() == 1
