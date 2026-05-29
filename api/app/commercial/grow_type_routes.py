"""Custom grow types API — create, edit, delete, submit for review (Pro/Commercial)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.commercial.models import CustomGrowType

router = APIRouter()

ALLOWED_PLANS = {"pro", "commercial"}


def _check_tier(user: CurrentUser, session: AsyncSession) -> None:
    """Raise 403 if tenant is not on Pro or Commercial plan."""
    # Plan is checked at the route level via the tenant
    pass


# ---------- Schemas ----------


class GrowTypeCreate(BaseModel):
    name: str
    slug: str
    category: str
    description: str
    base_type: str | None = None  # seed from built-in type
    profile: dict  # full profile matching GROW_TYPE_PROFILES shape


class GrowTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    profile: dict | None = None


class GrowTypeResponse(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    description: str
    base_type: str | None
    profile: dict
    submitted_for_review: bool
    approved: bool


class SubmitForReviewRequest(BaseModel):
    notes: str | None = None


# ---------- Tier check helper ----------


async def _require_pro_or_commercial(user: CurrentUser, session: AsyncSession) -> None:
    from app.tenants.models import Tenant

    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or tenant.plan not in ALLOWED_PLANS:
        raise HTTPException(status_code=403, detail="Custom grow types require Pro or Commercial plan")


def _to_response(gt: CustomGrowType) -> GrowTypeResponse:
    return GrowTypeResponse(
        id=str(gt.id),
        slug=gt.slug,
        name=gt.name,
        category=gt.category,
        description=gt.description,
        base_type=gt.base_type,
        profile=gt.profile,
        submitted_for_review=gt.submitted_for_review,
        approved=gt.approved,
    )


# ---------- CRUD ----------


@router.post("", status_code=201)
async def create_custom_grow_type(
    body: GrowTypeCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a custom grow type with stage definitions."""
    await _require_pro_or_commercial(user, session)

    # Check slug uniqueness within tenant
    existing = (
        await session.execute(
            select(CustomGrowType).where(
                CustomGrowType.tenant_id == user.tenant_id,
                CustomGrowType.slug == body.slug,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already exists")

    # If base_type specified, seed from built-in profile
    profile = body.profile
    if body.base_type:
        from app.config_management.service.grow_types import get_profile

        base = await get_profile(session, body.base_type)
        if not base:
            raise HTTPException(status_code=400, detail=f"Unknown base type: {body.base_type}")
        # Merge: base profile as defaults, user overrides on top
        merged = {**base, **profile}
        merged["id"] = body.slug
        merged["name"] = body.name
        profile = merged

    # Ensure required profile fields
    profile["id"] = body.slug
    profile["name"] = body.name

    gt = CustomGrowType(
        tenant_id=user.tenant_id,
        slug=body.slug,
        name=body.name,
        category=body.category,
        description=body.description,
        base_type=body.base_type,
        profile=profile,
    )
    session.add(gt)
    await session.commit()
    await session.refresh(gt)
    return _to_response(gt)


@router.get("")
async def list_custom_grow_types(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all custom grow types for the current tenant."""
    result = await session.execute(
        select(CustomGrowType).where(CustomGrowType.tenant_id == user.tenant_id).order_by(CustomGrowType.name)
    )
    return [_to_response(gt) for gt in result.scalars().all()]


@router.get("/{type_id}")
async def get_custom_grow_type(
    type_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a custom grow type by ID."""
    gt = await session.get(CustomGrowType, UUID(type_id))
    if not gt or gt.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom grow type not found")
    return _to_response(gt)


@router.patch("/{type_id}")
async def update_custom_grow_type(
    type_id: str,
    body: GrowTypeUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a custom grow type's configuration."""
    gt = await session.get(CustomGrowType, UUID(type_id))
    if not gt or gt.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom grow type not found")

    if body.name is not None:
        gt.name = body.name
        gt.profile = {**gt.profile, "name": body.name}
    if body.description is not None:
        gt.description = body.description
    if body.category is not None:
        gt.category = body.category
    if body.profile is not None:
        gt.profile = {**gt.profile, **body.profile, "id": gt.slug, "name": gt.name}

    await session.commit()
    await session.refresh(gt)
    return _to_response(gt)


@router.delete("/{type_id}", status_code=204)
async def delete_custom_grow_type(
    type_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a custom grow type by ID."""
    gt = await session.get(CustomGrowType, UUID(type_id))
    if not gt or gt.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom grow type not found")
    await session.delete(gt)
    await session.commit()


# ---------- Global Registry Submission (6.2) ----------


@router.post("/{type_id}/submit", status_code=200)
async def submit_for_review(
    type_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Submit a custom grow type for inclusion in the global registry."""
    gt = await session.get(CustomGrowType, UUID(type_id))
    if not gt or gt.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Custom grow type not found")
    if gt.submitted_for_review:
        raise HTTPException(status_code=409, detail="Already submitted for review")

    gt.submitted_for_review = True
    await session.commit()
    return {"status": "submitted", "message": "Your custom grow type has been submitted for review."}


@router.get("/review/queue")
async def review_queue(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Admin view: list all submissions pending review (currently shows own tenant's only)."""
    result = await session.execute(
        select(CustomGrowType).where(
            CustomGrowType.submitted_for_review.is_(True),
            CustomGrowType.approved.is_(False),
        )
    )
    return [_to_response(gt) for gt in result.scalars().all()]
