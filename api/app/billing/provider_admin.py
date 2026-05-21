"""Provider admin routes — CRUD for payment provider configs."""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import require_platform_admin
from app.billing.models import PaymentProvider, ProviderType
from app.billing.providers.base import get_provider_class
from app.billing.service import decrypt_provider_config, encrypt_provider_config
from app.database import async_session_factory

router = APIRouter()
logger = logging.getLogger("tendril.billing.provider_admin")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ─── Schemas ──────────────────────────────────────────────────────────────────


class ProviderListResponse(BaseModel):
    id: UUID
    provider_type: str
    display_name: str
    is_active: bool
    is_primary: bool
    supported_methods: list[str] | None

    class Config:
        from_attributes = True


class ProviderCreateRequest(BaseModel):
    provider_type: str  # stripe, paypal, square, paddle
    display_name: str
    config: dict[str, Any]
    webhook_secret: str | None = None
    set_primary: bool = False


class ProviderUpdateRequest(BaseModel):
    display_name: str | None = None
    config: dict[str, Any] | None = None
    webhook_secret: str | None = None
    is_active: bool | None = None
    set_primary: bool | None = None


# ─── Routes ───────────────────────────────────────────────────────────────────


@router.get("", dependencies=[Depends(require_platform_admin)])
async def list_providers(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[ProviderListResponse]:
    """List all configured payment providers."""
    providers = (await session.execute(select(PaymentProvider))).scalars().all()
    return [ProviderListResponse.model_validate(p) for p in providers]


@router.post("", dependencies=[Depends(require_platform_admin)], status_code=201)
async def create_provider(
    body: ProviderCreateRequest,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> ProviderListResponse:
    """Add a new payment provider."""
    # Validate provider type
    try:
        ptype = ProviderType(body.provider_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid provider type: {body.provider_type}") from None

    # Validate adapter exists
    provider_cls = get_provider_class(body.provider_type)
    if not provider_cls:
        raise HTTPException(status_code=400, detail=f"No adapter for provider: {body.provider_type}")

    # Test connection before saving
    adapter = provider_cls(body.config)
    connected = await adapter.test_connection()
    if not connected:
        raise HTTPException(status_code=400, detail="Failed to connect with provided credentials")

    # If setting as primary, unset existing primary
    if body.set_primary:
        existing_primary = (
            await session.execute(select(PaymentProvider).where(PaymentProvider.is_primary.is_(True)))
        ).scalar_one_or_none()
        if existing_primary:
            existing_primary.is_primary = False

    encrypted_config = encrypt_provider_config(body.config)
    encrypted_webhook = encrypt_provider_config({"secret": body.webhook_secret}) if body.webhook_secret else None

    provider = PaymentProvider(
        provider_type=ptype,
        display_name=body.display_name,
        is_active=True,
        is_primary=body.set_primary,
        config_encrypted=encrypted_config,
        webhook_secret_encrypted=encrypted_webhook,
        supported_methods=adapter.list_supported_checkout_methods(),
    )
    session.add(provider)
    await session.commit()
    await session.refresh(provider)
    return ProviderListResponse.model_validate(provider)


@router.patch("/{provider_id}", dependencies=[Depends(require_platform_admin)])
async def update_provider(
    provider_id: UUID,
    body: ProviderUpdateRequest,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> ProviderListResponse:
    """Update a payment provider config."""
    provider = await session.get(PaymentProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    if body.display_name is not None:
        provider.display_name = body.display_name

    if body.config is not None:
        provider.config_encrypted = encrypt_provider_config(body.config)
        # Update supported methods
        provider_cls = get_provider_class(provider.provider_type.value)
        if provider_cls:
            adapter = provider_cls(body.config)
            provider.supported_methods = adapter.list_supported_checkout_methods()

    if body.webhook_secret is not None:
        provider.webhook_secret_encrypted = encrypt_provider_config({"secret": body.webhook_secret})

    if body.is_active is not None:
        provider.is_active = body.is_active

    if body.set_primary:
        # Unset other primaries
        existing = (
            (
                await session.execute(
                    select(PaymentProvider).where(
                        PaymentProvider.is_primary.is_(True),
                        PaymentProvider.id != provider_id,
                    )
                )
            )
            .scalars()
            .all()
        )
        for p in existing:
            p.is_primary = False
        provider.is_primary = True

    await session.commit()
    await session.refresh(provider)
    return ProviderListResponse.model_validate(provider)


@router.delete("/{provider_id}", dependencies=[Depends(require_platform_admin)], status_code=204)
async def delete_provider(
    provider_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Remove a payment provider."""
    provider = await session.get(PaymentProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    if provider.is_primary:
        raise HTTPException(status_code=400, detail="Cannot delete the primary provider. Set another as primary first.")
    await session.delete(provider)
    await session.commit()


@router.post("/{provider_id}/test", dependencies=[Depends(require_platform_admin)])
async def test_provider_connection(
    provider_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Test credentials for a payment provider."""
    provider = await session.get(PaymentProvider, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    config = decrypt_provider_config(provider.config_encrypted)
    provider_cls = get_provider_class(provider.provider_type.value)
    if not provider_cls:
        raise HTTPException(status_code=500, detail="No adapter found")

    adapter = provider_cls(config)
    success = await adapter.test_connection()
    return {"connected": success}
