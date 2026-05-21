"""Billing service — provider resolution, config encryption, usage helpers."""

from __future__ import annotations

import json
import logging
from typing import Any
from uuid import UUID

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.billing.models import BillingPlan, PaymentProvider
from app.billing.providers.base import BasePaymentProvider, get_provider_class
from app.config import get_settings

logger = logging.getLogger("tendril.billing.service")


def _get_fernet() -> Fernet:
    """Get Fernet cipher from app secret key."""
    settings = get_settings()
    # Use first 32 bytes of secret key as Fernet key (base64 encoded)
    import base64

    key_bytes = settings.jwt_secret.encode()[:32].ljust(32, b"\0")
    key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(key)


def encrypt_provider_config(config: dict[str, Any]) -> bytes:
    """Encrypt provider config dict to bytes for DB storage."""
    f = _get_fernet()
    return f.encrypt(json.dumps(config).encode())


def decrypt_provider_config(encrypted: bytes) -> dict[str, Any]:
    """Decrypt provider config from DB storage."""
    f = _get_fernet()
    return json.loads(f.decrypt(encrypted).decode())


async def get_primary_provider(session: AsyncSession) -> tuple[PaymentProvider, BasePaymentProvider] | None:
    """Get the primary active payment provider and instantiate its adapter."""
    provider_row = (
        await session.execute(
            select(PaymentProvider).where(
                PaymentProvider.is_active.is_(True),
                PaymentProvider.is_primary.is_(True),
            )
        )
    ).scalar_one_or_none()

    if not provider_row:
        return None

    config = decrypt_provider_config(provider_row.config_encrypted)
    provider_cls = get_provider_class(provider_row.provider_type.value)
    if not provider_cls:
        logger.error("No adapter for provider type: %s", provider_row.provider_type)
        return None

    return provider_row, provider_cls(config)


async def get_plan_for_tenant(session: AsyncSession, plan_slug: str) -> BillingPlan | None:
    """Look up a billing plan by its slug."""
    return (
        await session.execute(select(BillingPlan).where(BillingPlan.slug == plan_slug, BillingPlan.is_active.is_(True)))
    ).scalar_one_or_none()


async def get_plan_by_id(session: AsyncSession, plan_id: UUID) -> BillingPlan | None:
    """Look up a billing plan by ID."""
    return await session.get(BillingPlan, plan_id)


async def get_plan_limits(session: AsyncSession, plan_slug: str) -> dict[str, int | None]:
    """Get all limits for a plan as a dict. None means unlimited."""
    plan = await get_plan_for_tenant(session, plan_slug)
    if not plan:
        # Default to free limits
        return {
            "grows": 1,
            "devices": 2,
            "team_members": 1,
            "ai_analyses": 10,
            "storage_gb": 1,
            "automations": 2,
            "integrations": 1,
            "journal_entries": 50,
        }

    return {
        "grows": plan.max_grows,
        "devices": plan.max_devices,
        "team_members": plan.max_team_members,
        "ai_analyses": plan.max_ai_analyses_month,
        "storage_gb": plan.max_storage_gb,
        "automations": plan.max_automations,
        "integrations": plan.max_integrations,
        "journal_entries": plan.max_journal_entries_month,
    }
