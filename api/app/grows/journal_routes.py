"""Journal entries API — bucket event logging."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.billing.tier_gate import require_usage_limit
from app.grows.models import JournalEntry
from app.pagination import PaginatedResponse, PaginationParams, paginate

logger = logging.getLogger(__name__)

router = APIRouter()


class JournalCreate(BaseModel):
    bucket_id: UUID
    event_type: str
    content: str | None = None
    payload: dict | None = None


class JournalUpdate(BaseModel):
    content: str | None = None
    payload: dict | None = None


class JournalResponse(BaseModel):
    id: UUID
    bucket_id: UUID
    event_type: str
    content: str | None
    payload: dict | None
    created_at: datetime
    model_config = {"from_attributes": True}


class QuickJournalCreate(BaseModel):
    """Combined journal entry + optional sensor reading in one action."""

    bucket_id: UUID
    event_type: str
    content: str | None = None
    payload: dict | None = None
    # Optional sensor fields — if any are provided, a reading is also created
    ph: float | None = None
    ec: float | None = None
    ppm: float | None = None
    water_temp_f: float | None = None
    volume_gallons: float | None = None


class QuickJournalResponse(BaseModel):
    journal: JournalResponse
    reading_id: UUID | None = None


@router.post(
    "",
    response_model=JournalResponse,
    status_code=201,
    dependencies=[Depends(require_usage_limit("journal_entries"))],
)
async def create_entry(
    body: JournalCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new journal entry for a bucket."""
    entry = JournalEntry(tenant_id=user.tenant_id, **body.model_dump())
    session.add(entry)
    from app.billing.metering import record_usage

    await record_usage(session, user.tenant_id, "journal_entries")
    await session.commit()
    await session.refresh(entry)

    # Create follow-up tasks based on event type
    if body.event_type in ("feeding", "water_change", "training", "topping", "defoliation", "transplant"):
        try:
            from app.grows.models import Bucket

            bucket = await session.get(Bucket, body.bucket_id)
            grow_cycle_id = bucket.grow_cycle_id if bucket else None
            from app.scheduler.task_generator import create_journal_followup_tasks

            await create_journal_followup_tasks(
                session,
                tenant_id=user.tenant_id,
                grow_cycle_id=grow_cycle_id,
                bucket_id=body.bucket_id,
                event_type=body.event_type,
                content=body.content,
                payload=body.payload,
            )
        except Exception:
            logger.debug("journal followup task failed", exc_info=True)

    return entry


@router.post(
    "/quick",
    response_model=QuickJournalResponse,
    status_code=201,
    dependencies=[Depends(require_usage_limit("journal_entries"))],
)
async def create_quick_entry(
    body: QuickJournalCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a journal entry with optional sensor reading in one atomic action."""
    from app.billing.metering import record_usage
    from app.grows.models import Bucket, BucketSensorReading

    # Create journal entry
    entry = JournalEntry(
        tenant_id=user.tenant_id,
        bucket_id=body.bucket_id,
        event_type=body.event_type,
        content=body.content,
        payload=body.payload,
    )
    session.add(entry)
    await record_usage(session, user.tenant_id, "journal_entries")

    # Create sensor reading if any sensor fields are provided
    reading_id = None
    has_reading = any([body.ph, body.ec, body.ppm, body.water_temp_f])
    if has_reading:
        reading = BucketSensorReading(
            tenant_id=user.tenant_id,
            bucket_id=body.bucket_id,
            ph=body.ph,
            ec=body.ec,
            ppm=body.ppm,
            water_temp_f=body.water_temp_f,
        )
        session.add(reading)

    await session.commit()
    await session.refresh(entry)
    if has_reading:
        await session.refresh(reading)
        reading_id = reading.id

    # Create follow-up tasks based on event type
    if body.event_type in ("feeding", "water_change", "training", "topping", "defoliation", "transplant"):
        try:
            bucket = await session.get(Bucket, body.bucket_id)
            grow_cycle_id = bucket.grow_cycle_id if bucket else None
            from app.scheduler.task_generator import create_journal_followup_tasks

            await create_journal_followup_tasks(
                session,
                tenant_id=user.tenant_id,
                grow_cycle_id=grow_cycle_id,
                bucket_id=body.bucket_id,
                event_type=body.event_type,
                content=body.content,
                payload=body.payload,
            )
        except Exception:
            logger.debug("journal followup task failed", exc_info=True)

    return QuickJournalResponse(
        journal=JournalResponse.model_validate(entry),
        reading_id=reading_id,
    )


@router.get("", response_model=PaginatedResponse[JournalResponse])
async def list_entries(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    bucket_id: UUID | None = None,
):
    """List journal entries with optional bucket filtering."""
    q = select(JournalEntry).where(JournalEntry.tenant_id == user.tenant_id).order_by(desc(JournalEntry.created_at))
    if bucket_id:
        q = q.where(JournalEntry.bucket_id == bucket_id)
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/{entry_id}", response_model=JournalResponse)
async def get_entry(
    entry_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a single journal entry by ID."""
    entry = await session.get(JournalEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return entry


@router.patch("/{entry_id}", response_model=JournalResponse)
async def update_entry(
    entry_id: UUID,
    body: JournalUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a journal entry."""
    entry = await session.get(JournalEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: UUID,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a journal entry by ID."""
    entry = await session.get(JournalEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    await session.delete(entry)
    await session.commit()
