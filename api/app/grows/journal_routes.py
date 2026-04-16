"""Journal entries API — bucket event logging."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.grows.models import JournalEntry

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


@router.post("", response_model=JournalResponse, status_code=201)
async def create_entry(
    body: JournalCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    entry = JournalEntry(tenant_id=user.tenant_id, **body.model_dump())
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("", response_model=list[JournalResponse])
async def list_entries(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    bucket_id: UUID | None = None,
):
    q = select(JournalEntry).order_by(desc(JournalEntry.created_at))
    if bucket_id:
        q = q.where(JournalEntry.bucket_id == bucket_id)
    result = await session.execute(q)
    return result.scalars().all()


@router.patch("/{entry_id}", response_model=JournalResponse)
async def update_entry(
    entry_id: UUID,
    body: JournalUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
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
    entry = await session.get(JournalEntry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    await session.delete(entry)
    await session.commit()
