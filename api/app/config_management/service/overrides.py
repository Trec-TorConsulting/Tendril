"""Tenant config override service — JSON merge of global defaults + per-tenant overrides."""

from __future__ import annotations

import copy
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config_management import TenantConfigOverride
from app.config_management.service.cache import cache


async def get_with_overrides(
    session: AsyncSession,
    tenant_id: str,
    config_type: str,
    config_key: str,
    global_default: dict,
) -> dict:
    """Return global_default merged with tenant override (if any).

    Uses shallow JSON merge — override keys replace global keys at top level.
    """
    cache_key = f"override:{tenant_id}:{config_type}:{config_key}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = await session.execute(
        select(TenantConfigOverride).where(
            TenantConfigOverride.tenant_id == UUID(tenant_id),
            TenantConfigOverride.config_type == config_type,
            TenantConfigOverride.config_key == config_key,
        )
    )
    override = result.scalar_one_or_none()

    if override is None:
        cache.set(cache_key, global_default)
        return global_default

    # Deep merge: override values replace global at each key level
    merged = _deep_merge(global_default, override.override_json)
    cache.set(cache_key, merged)
    return merged


async def list_overrides(session: AsyncSession, tenant_id: str) -> list[dict]:
    """List all overrides for a tenant."""
    result = await session.execute(
        select(TenantConfigOverride).where(TenantConfigOverride.tenant_id == UUID(tenant_id))
    )
    overrides = result.scalars().all()
    return [
        {
            "id": str(o.id),
            "config_type": o.config_type,
            "config_key": o.config_key,
            "override_json": o.override_json,
            "updated_at": o.updated_at.isoformat() if o.updated_at else None,
        }
        for o in overrides
    ]


async def set_override(
    session: AsyncSession,
    tenant_id: str,
    config_type: str,
    config_key: str,
    override_json: dict,
) -> dict:
    """Create or update a tenant override."""
    from sqlalchemy.dialects.postgresql import insert

    stmt = (
        insert(TenantConfigOverride)
        .values(
            tenant_id=UUID(tenant_id),
            config_type=config_type,
            config_key=config_key,
            override_json=override_json,
        )
        .on_conflict_do_update(
            constraint="uq_tenant_config_override",
            set_={"override_json": override_json},
        )
        .returning(TenantConfigOverride.id)
    )

    result = await session.execute(stmt)
    override_id = result.scalar_one()
    await session.commit()

    # Invalidate cache
    cache.invalidate(f"override:{tenant_id}:{config_type}:{config_key}")

    return {"id": str(override_id), "config_type": config_type, "config_key": config_key}


async def delete_override(
    session: AsyncSession,
    tenant_id: str,
    config_type: str,
    config_key: str,
) -> bool:
    """Delete a tenant override. Returns True if deleted."""
    result = await session.execute(
        delete(TenantConfigOverride).where(
            TenantConfigOverride.tenant_id == UUID(tenant_id),
            TenantConfigOverride.config_type == config_type,
            TenantConfigOverride.config_key == config_key,
        )
    )
    await session.commit()
    cache.invalidate(f"override:{tenant_id}:{config_type}:{config_key}")
    return result.rowcount > 0


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base (override wins on conflict)."""
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged
