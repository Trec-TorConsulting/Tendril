"""Plan management API — CRUD for billing plans + provider sync."""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.middleware import require_platform_admin
from app.billing.models import (
    BillingModel,
    BillingPlan,
    BillingPlanPrice,
    PaymentProvider,
    SyncStatus,
)
from app.billing.providers.base import get_provider_class
from app.database import async_session_factory

router = APIRouter()
logger = logging.getLogger("tendril.billing.plans")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# ─── Schemas ──────────────────────────────────────────────────────────────────


class PlanResponse(BaseModel):
    id: UUID
    slug: str
    name: str
    description: str | None
    is_active: bool
    is_public: bool
    sort_order: int
    billing_model: str
    base_price_cents: int
    annual_price_cents: int | None
    currency: str
    max_grows: int | None
    max_devices: int | None
    max_team_members: int | None
    max_ai_analyses_month: int | None
    max_storage_gb: int | None
    max_automations: int | None
    max_integrations: int | None
    max_journal_entries_month: int | None
    data_retention_days: int | None
    included_support_tier: str
    features_json: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class PlanCreateRequest(BaseModel):
    slug: str
    name: str
    description: str | None = None
    is_active: bool = True
    is_public: bool = True
    sort_order: int = 0
    billing_model: str = "flat"
    base_price_cents: int = 0
    annual_price_cents: int | None = None
    currency: str = "usd"
    max_grows: int | None = None
    max_devices: int | None = None
    max_team_members: int | None = None
    max_ai_analyses_month: int | None = None
    max_storage_gb: int | None = None
    max_automations: int | None = None
    max_integrations: int | None = None
    max_journal_entries_month: int | None = None
    data_retention_days: int | None = None
    included_support_tier: str = "community"
    features_json: dict[str, Any] | None = None


class PlanUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    is_public: bool | None = None
    sort_order: int | None = None
    base_price_cents: int | None = None
    annual_price_cents: int | None = None
    max_grows: int | None = None
    max_devices: int | None = None
    max_team_members: int | None = None
    max_ai_analyses_month: int | None = None
    max_storage_gb: int | None = None
    max_automations: int | None = None
    max_integrations: int | None = None
    max_journal_entries_month: int | None = None
    data_retention_days: int | None = None
    included_support_tier: str | None = None
    features_json: dict[str, Any] | None = None


class ProviderResponse(BaseModel):
    id: UUID
    provider_type: str
    display_name: str
    is_active: bool
    is_primary: bool
    supported_methods: list[str] | None

    model_config = ConfigDict(from_attributes=True)


class ProviderCreateRequest(BaseModel):
    provider_type: str
    display_name: str
    config: dict[str, Any]
    webhook_secret: str | None = None
    set_primary: bool = False


# ─── Public Plans (no auth) ───────────────────────────────────────────────────


@router.get("/public")
async def list_public_plans(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[PlanResponse]:
    """List all active public plans (for pricing page)."""
    plans = (
        (
            await session.execute(
                select(BillingPlan)
                .where(BillingPlan.is_active.is_(True), BillingPlan.is_public.is_(True))
                .order_by(BillingPlan.sort_order)
            )
        )
        .scalars()
        .all()
    )
    return [PlanResponse.model_validate(p) for p in plans]


# ─── Admin Plan CRUD ──────────────────────────────────────────────────────────


@router.get("/", dependencies=[Depends(require_platform_admin)])
async def list_plans(
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> list[PlanResponse]:
    """List all plans (admin view, includes inactive)."""
    plans = (await session.execute(select(BillingPlan).order_by(BillingPlan.sort_order))).scalars().all()
    return [PlanResponse.model_validate(p) for p in plans]


@router.get("/{plan_id}", dependencies=[Depends(require_platform_admin)])
async def get_plan(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> PlanResponse:
    """Get a single plan by ID."""
    plan = await session.get(BillingPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanResponse.model_validate(plan)


@router.post("/", dependencies=[Depends(require_platform_admin)], status_code=201)
async def create_plan(
    body: PlanCreateRequest,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> PlanResponse:
    """Create a new billing plan."""
    # Check slug uniqueness
    existing = (await session.execute(select(BillingPlan).where(BillingPlan.slug == body.slug))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail=f"Plan slug '{body.slug}' already exists")

    plan = BillingPlan(
        slug=body.slug,
        name=body.name,
        description=body.description,
        is_active=body.is_active,
        is_public=body.is_public,
        sort_order=body.sort_order,
        billing_model=BillingModel(body.billing_model),
        base_price_cents=body.base_price_cents,
        annual_price_cents=body.annual_price_cents,
        currency=body.currency,
        max_grows=body.max_grows,
        max_devices=body.max_devices,
        max_team_members=body.max_team_members,
        max_ai_analyses_month=body.max_ai_analyses_month,
        max_storage_gb=body.max_storage_gb,
        max_automations=body.max_automations,
        max_integrations=body.max_integrations,
        max_journal_entries_month=body.max_journal_entries_month,
        data_retention_days=body.data_retention_days,
        included_support_tier=body.included_support_tier,
        features_json=body.features_json or {},
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.patch("/{plan_id}", dependencies=[Depends(require_platform_admin)])
async def update_plan(
    plan_id: UUID,
    body: PlanUpdateRequest,
    session: Annotated[AsyncSession, Depends(_get_db)],
) -> PlanResponse:
    """Update a billing plan."""
    plan = await session.get(BillingPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)

    await session.commit()
    await session.refresh(plan)
    return PlanResponse.model_validate(plan)


@router.delete("/{plan_id}", dependencies=[Depends(require_platform_admin)], status_code=204)
async def archive_plan(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Archive (soft-delete) a plan by marking inactive."""
    plan = await session.get(BillingPlan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.is_active = False
    plan.is_public = False
    await session.commit()


# ─── Provider Sync ────────────────────────────────────────────────────────────


@router.post("/{plan_id}/sync", dependencies=[Depends(require_platform_admin)])
async def sync_plan_to_provider(
    plan_id: UUID,
    session: Annotated[AsyncSession, Depends(_get_db)],
):
    """Push a plan to the primary payment provider."""
    plan = await session.get(BillingPlan, plan_id, options=[selectinload(BillingPlan.prices)])
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Get primary provider
    provider_row = (
        await session.execute(
            select(PaymentProvider).where(
                PaymentProvider.is_active.is_(True),
                PaymentProvider.is_primary.is_(True),
            )
        )
    ).scalar_one_or_none()
    if not provider_row:
        raise HTTPException(status_code=400, detail="No active primary payment provider configured")

    # Decrypt config
    from app.billing.service import decrypt_provider_config

    config = decrypt_provider_config(provider_row.config_encrypted)
    provider_cls = get_provider_class(provider_row.provider_type.value)
    if not provider_cls:
        raise HTTPException(status_code=500, detail=f"No adapter for {provider_row.provider_type}")

    provider = provider_cls(config)

    # Find existing price mapping
    price_mapping = next((p for p in plan.prices if p.provider_id == provider_row.id), None)

    try:
        result = await provider.sync_plan(
            name=plan.name,
            description=plan.description,
            price_cents=plan.base_price_cents,
            interval="month",
            currency=plan.currency,
            existing_product_id=price_mapping.external_product_id if price_mapping else None,
            existing_price_id=price_mapping.external_price_id if price_mapping else None,
        )

        # Update or create price mapping
        if price_mapping:
            price_mapping.external_product_id = result.external_product_id
            price_mapping.external_price_id = result.external_price_id
            price_mapping.sync_status = SyncStatus.synced
            price_mapping.sync_error = None
        else:
            price_mapping = BillingPlanPrice(
                plan_id=plan.id,
                provider_id=provider_row.id,
                external_product_id=result.external_product_id,
                external_price_id=result.external_price_id,
                sync_status=SyncStatus.synced,
            )
            session.add(price_mapping)

        await session.commit()
        return {"status": "synced", "external_price_id": result.external_price_id}

    except Exception as e:
        logger.exception("Failed to sync plan %s to provider", plan_id)
        if price_mapping:
            price_mapping.sync_status = SyncStatus.error
            price_mapping.sync_error = str(e)
            await session.commit()
        raise HTTPException(status_code=502, detail=f"Provider sync failed: {e!s}") from e
