"""Container profile API — pot metadata for outdoor container grows."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import GrowCycle, Bucket, ContainerProfile

router = APIRouter()


# ---------- Schemas ----------

class ContainerProfileUpsert(BaseModel):
    pot_size_gallons: float | None = Field(default=None, ge=0.1, le=200)
    media_type: str | None = Field(default=None, max_length=100)
    pot_color: str | None = Field(default=None, max_length=50)
    pot_material: str | None = Field(default=None, pattern=r"^(plastic|fabric|ceramic|terracotta|metal|wood|concrete|other)$")
    has_saucer: bool = False
    is_mobile: bool = True
    sun_exposure: str | None = Field(default=None, pattern=r"^(full_sun|partial_sun|partial_shade|full_shade)$")
    location_notes: str | None = None


class ContainerProfileResponse(BaseModel):
    id: UUID
    grow_cycle_id: UUID
    bucket_id: UUID
    pot_size_gallons: float | None
    media_type: str | None
    pot_color: str | None
    pot_material: str | None
    has_saucer: bool
    is_mobile: bool
    sun_exposure: str | None
    location_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------- Endpoints ----------

@router.put("/{grow_id}/containers/{bucket_id}", response_model=ContainerProfileResponse, status_code=200)
async def upsert_container_profile(
    grow_id: UUID,
    bucket_id: UUID,
    body: ContainerProfileUpsert,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create or update the container profile for a specific pot/bucket."""
    grow = await session.get(GrowCycle, grow_id)
    if grow is None:
        raise HTTPException(status_code=404, detail="Grow not found")

    bucket = await session.get(Bucket, bucket_id)
    if bucket is None or bucket.grow_cycle_id != grow_id:
        raise HTTPException(status_code=404, detail="Bucket not found in this grow")

    result = await session.execute(
        select(ContainerProfile).where(ContainerProfile.bucket_id == bucket_id)
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = ContainerProfile(
            tenant_id=user.tenant_id,
            grow_cycle_id=grow_id,
            bucket_id=bucket_id,
            **body.model_dump(),
        )
        session.add(profile)
    else:
        for k, v in body.model_dump().items():
            setattr(profile, k, v)
        profile.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/{grow_id}/containers", response_model=list[ContainerProfileResponse])
async def list_container_profiles(
    grow_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """List all container profiles for a grow."""
    result = await session.execute(
        select(ContainerProfile).where(ContainerProfile.grow_cycle_id == grow_id)
    )
    return result.scalars().all()


@router.get("/{grow_id}/containers/{bucket_id}", response_model=ContainerProfileResponse)
async def get_container_profile(
    grow_id: UUID,
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get the container profile for a specific pot."""
    result = await session.execute(
        select(ContainerProfile).where(
            ContainerProfile.grow_cycle_id == grow_id,
            ContainerProfile.bucket_id == bucket_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Container profile not found")
    return profile


@router.delete("/{grow_id}/containers/{bucket_id}", status_code=204)
async def delete_container_profile(
    grow_id: UUID,
    bucket_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a container profile."""
    result = await session.execute(
        select(ContainerProfile).where(
            ContainerProfile.grow_cycle_id == grow_id,
            ContainerProfile.bucket_id == bucket_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(status_code=404, detail="Container profile not found")
    await session.delete(profile)
    await session.commit()
