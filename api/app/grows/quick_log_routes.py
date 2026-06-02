"""Quick-Log API — fast logging endpoints for mobile-first workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.grows.models import (
    Bucket,
    BucketSensorReading,
    JournalEntry,
    Tent,
    TentSensorReading,
)

router = APIRouter()


# ---------- Schemas ----------


class NutrientDose(BaseModel):
    name: str
    ml_per_gallon: float | None = None
    ml_total: float | None = None


class FeedingLogRequest(BaseModel):
    bucket_ids: list[UUID] = Field(min_length=1)
    ph: float | None = None
    ec: float | None = None
    ppm: float | None = None
    water_temp_f: float | None = None
    volume_gal: float | None = None
    nutrients: list[NutrientDose] | None = None
    notes: str | None = None
    recorded_at: datetime | None = None  # Client timestamp for offline queue


class ManualReadingRequest(BaseModel):
    tent_id: UUID
    temp_f: float | None = None
    humidity: float | None = None
    vpd: float | None = None
    recorded_at: datetime | None = None


class QuickNoteRequest(BaseModel):
    bucket_id: UUID | None = None
    grow_cycle_id: UUID | None = None
    tags: list[str] | None = None
    content: str | None = None
    recorded_at: datetime | None = None


class BatchAction(BaseModel):
    type: str  # feeding | reading | note | water_change
    data: dict
    client_timestamp: datetime


class BatchRequest(BaseModel):
    actions: list[BatchAction] = Field(min_length=1)


class FeedingLogResponse(BaseModel):
    created: int
    bucket_ids: list[UUID]


class ManualReadingResponse(BaseModel):
    id: UUID
    tent_id: UUID
    recorded_at: datetime


class QuickNoteResponse(BaseModel):
    id: UUID
    event_type: str
    recorded_at: datetime


class BatchResponse(BaseModel):
    processed: int
    succeeded: int
    failed: int
    errors: list[str] | None = None


# ---------- Endpoints ----------


@router.post("/feeding", response_model=FeedingLogResponse, status_code=201)
async def quick_log_feeding(
    body: FeedingLogRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log feeding/watering for one or more buckets (bulk DWC flush-and-fill)."""
    # Validate all bucket_ids belong to current tenant
    result = await session.execute(
        select(Bucket).where(
            Bucket.id.in_(body.bucket_ids),
            Bucket.tenant_id == user.tenant_id,
        )
    )
    buckets = result.scalars().all()
    if len(buckets) != len(body.bucket_ids):
        raise HTTPException(status_code=404, detail="One or more buckets not found")

    recorded_at = body.recorded_at or datetime.now(UTC)
    nutrient_payload = [n.model_dump() for n in body.nutrients] if body.nutrients else None

    # Auto-derive EC↔PPM when only one is provided
    ec = body.ec
    ppm = body.ppm
    if ec is not None and ppm is None:
        ppm = round(ec * 500.0, 1)
    elif ppm is not None and ec is None:
        ec = round(ppm / 500.0, 3)

    readings = []
    for bucket in buckets:
        # Create sensor reading
        reading = BucketSensorReading(
            tenant_id=user.tenant_id,
            bucket_id=bucket.id,
            ph=body.ph,
            ec=ec,
            ppm=ppm,
            water_temp_f=body.water_temp_f,
            recorded_at=recorded_at,
        )
        session.add(reading)
        readings.append(reading)

        # Create journal entry for the feeding event
        entry = JournalEntry(
            tenant_id=user.tenant_id,
            bucket_id=bucket.id,
            event_type="feeding",
            content=body.notes,
            payload={
                "ph": body.ph,
                "ec": body.ec,
                "ppm": body.ppm,
                "water_temp_f": body.water_temp_f,
                "volume_gal": body.volume_gal,
                "nutrients": nutrient_payload,
                "source": "quick_log",
            },
            created_at=recorded_at,
        )
        session.add(entry)

    await session.flush()  # Flush to ensure readings are in session

    # Propagate header readings to all site buckets in RDWC grows
    from app.integrations.connectors.base import propagate_header_bucket_readings

    for reading in readings:
        await propagate_header_bucket_readings(session, str(reading.bucket_id), reading)

    await session.commit()
    return FeedingLogResponse(created=len(buckets), bucket_ids=body.bucket_ids)


class WaterChangeRequest(BaseModel):
    bucket_ids: list[UUID] = Field(min_length=1)
    ph: float | None = None
    ec: float | None = None
    ppm: float | None = None
    water_temp_f: float | None = None
    volume_gal: float | None = None
    notes: str | None = None
    recorded_at: datetime | None = None


@router.post("/water-change", response_model=FeedingLogResponse, status_code=201)
async def quick_log_water_change(
    body: WaterChangeRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a water change for one or more buckets (flush-and-fill)."""
    result = await session.execute(
        select(Bucket).where(
            Bucket.id.in_(body.bucket_ids),
            Bucket.tenant_id == user.tenant_id,
        )
    )
    buckets = result.scalars().all()
    if len(buckets) != len(body.bucket_ids):
        raise HTTPException(status_code=404, detail="One or more buckets not found")

    recorded_at = body.recorded_at or datetime.now(UTC)

    # Auto-derive EC↔PPM when only one is provided
    ec = body.ec
    ppm = body.ppm
    if ec is not None and ppm is None:
        ppm = round(ec * 500.0, 1)
    elif ppm is not None and ec is None:
        ec = round(ppm / 500.0, 3)

    readings = []
    for bucket in buckets:
        # Create sensor reading
        reading = BucketSensorReading(
            tenant_id=user.tenant_id,
            bucket_id=bucket.id,
            ph=body.ph,
            ec=ec,
            ppm=ppm,
            water_temp_f=body.water_temp_f,
            recorded_at=recorded_at,
        )
        session.add(reading)
        readings.append(reading)

        # Create journal entry for water change
        entry = JournalEntry(
            tenant_id=user.tenant_id,
            bucket_id=bucket.id,
            event_type="water_change",
            content=body.notes,
            payload={
                "ph": body.ph,
                "ec": body.ec,
                "ppm": body.ppm,
                "water_temp_f": body.water_temp_f,
                "volume_gal": body.volume_gal,
                "source": "quick_log",
            },
            created_at=recorded_at,
        )
        session.add(entry)

    await session.flush()

    from app.integrations.connectors.base import propagate_header_bucket_readings

    for reading in readings:
        await propagate_header_bucket_readings(session, str(reading.bucket_id), reading)

    await session.commit()
    return FeedingLogResponse(created=len(buckets), bucket_ids=body.bucket_ids)


@router.post("/reading", response_model=ManualReadingResponse, status_code=201)
async def quick_log_reading(
    body: ManualReadingRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a manual environment reading for a tent (no sensor required)."""
    tent = await session.get(Tent, body.tent_id)
    if not tent or tent.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Tent not found")

    recorded_at = body.recorded_at or datetime.now(UTC)
    reading = TentSensorReading(
        tenant_id=user.tenant_id,
        tent_id=body.tent_id,
        device_id=None,
        ambient_temp_f=body.temp_f,
        ambient_humidity=body.humidity,
        vpd=body.vpd,
        recorded_at=recorded_at,
    )
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return ManualReadingResponse(id=reading.id, tent_id=body.tent_id, recorded_at=recorded_at)


@router.post("/note", response_model=QuickNoteResponse, status_code=201)
async def quick_log_note(
    body: QuickNoteRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Log a quick note/observation tagged to a bucket or grow."""
    # Resolve bucket_id — either provided directly or inferred from grow
    bucket_id = body.bucket_id
    if not bucket_id and body.grow_cycle_id:
        # Get first active bucket in the grow
        result = await session.execute(
            select(Bucket)
            .where(
                Bucket.grow_cycle_id == body.grow_cycle_id,
                Bucket.status == "active",
            )
            .limit(1)
        )
        bucket = result.scalar_one_or_none()
        if bucket:
            bucket_id = bucket.id

    if not bucket_id:
        raise HTTPException(status_code=422, detail="Must provide bucket_id or grow_cycle_id with active buckets")

    # Validate bucket belongs to tenant
    bucket = await session.get(Bucket, bucket_id)
    if not bucket or bucket.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="Bucket not found")

    recorded_at = body.recorded_at or datetime.now(UTC)
    event_type = body.tags[0] if body.tags else "note"

    entry = JournalEntry(
        tenant_id=user.tenant_id,
        bucket_id=bucket_id,
        event_type=event_type,
        content=body.content,
        payload={"tags": body.tags, "source": "quick_log"} if body.tags else {"source": "quick_log"},
        created_at=recorded_at,
    )
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return QuickNoteResponse(id=entry.id, event_type=event_type, recorded_at=recorded_at)


@router.post("/batch", response_model=BatchResponse)
async def quick_log_batch(
    body: BatchRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Replay offline-queued quick-log actions. Processes each action in order."""
    succeeded = 0
    errors: list[str] = []
    # Track readings that need RDWC header→site propagation
    readings_to_propagate: list[BucketSensorReading] = []

    for i, action in enumerate(body.actions):
        try:
            if action.type == "feeding":
                req = FeedingLogRequest(**action.data, recorded_at=action.client_timestamp)
                # Validate buckets
                result = await session.execute(
                    select(Bucket).where(
                        Bucket.id.in_(req.bucket_ids),
                        Bucket.tenant_id == user.tenant_id,
                    )
                )
                buckets = result.scalars().all()
                if len(buckets) != len(req.bucket_ids):
                    errors.append(f"Action {i}: bucket not found")
                    continue
                nutrient_payload = [n.model_dump() for n in req.nutrients] if req.nutrients else None
                # Auto-derive EC↔PPM
                _ec = req.ec
                _ppm = req.ppm
                if _ec is not None and _ppm is None:
                    _ppm = round(_ec * 500.0, 1)
                elif _ppm is not None and _ec is None:
                    _ec = round(_ppm / 500.0, 3)

                for bucket in buckets:
                    reading = BucketSensorReading(
                        tenant_id=user.tenant_id,
                        bucket_id=bucket.id,
                        ph=req.ph,
                        ec=_ec,
                        ppm=_ppm,
                        water_temp_f=req.water_temp_f,
                        recorded_at=action.client_timestamp,
                    )
                    session.add(reading)
                    readings_to_propagate.append(reading)
                    session.add(
                        JournalEntry(
                            tenant_id=user.tenant_id,
                            bucket_id=bucket.id,
                            event_type="feeding",
                            content=req.notes,
                            payload={
                                "ph": req.ph,
                                "ec": req.ec,
                                "ppm": req.ppm,
                                "water_temp_f": req.water_temp_f,
                                "volume_gal": req.volume_gal,
                                "nutrients": nutrient_payload,
                                "source": "quick_log",
                            },
                            created_at=action.client_timestamp,
                        )
                    )
                succeeded += 1

            elif action.type == "reading":
                req = ManualReadingRequest(**action.data, recorded_at=action.client_timestamp)
                tent = await session.get(Tent, req.tent_id)
                if not tent or tent.tenant_id != user.tenant_id:
                    errors.append(f"Action {i}: tent not found")
                    continue
                session.add(
                    TentSensorReading(
                        tenant_id=user.tenant_id,
                        tent_id=req.tent_id,
                        device_id=None,
                        ambient_temp_f=req.temp_f,
                        ambient_humidity=req.humidity,
                        vpd=req.vpd,
                        recorded_at=action.client_timestamp,
                    )
                )
                succeeded += 1

            elif action.type == "note":
                req = QuickNoteRequest(**action.data, recorded_at=action.client_timestamp)
                bucket_id = req.bucket_id
                if not bucket_id and req.grow_cycle_id:
                    result = await session.execute(
                        select(Bucket)
                        .where(Bucket.grow_cycle_id == req.grow_cycle_id, Bucket.status == "active")
                        .limit(1)
                    )
                    b = result.scalar_one_or_none()
                    bucket_id = b.id if b else None
                if not bucket_id:
                    errors.append(f"Action {i}: no bucket resolved")
                    continue
                event_type = req.tags[0] if req.tags else "note"
                session.add(
                    JournalEntry(
                        tenant_id=user.tenant_id,
                        bucket_id=bucket_id,
                        event_type=event_type,
                        content=req.content,
                        payload={"tags": req.tags, "source": "quick_log"},
                        created_at=action.client_timestamp,
                    )
                )
                succeeded += 1

            elif action.type == "water_change":
                req = WaterChangeRequest(**action.data, recorded_at=action.client_timestamp)
                result = await session.execute(
                    select(Bucket).where(
                        Bucket.id.in_(req.bucket_ids),
                        Bucket.tenant_id == user.tenant_id,
                    )
                )
                buckets = result.scalars().all()
                if len(buckets) != len(req.bucket_ids):
                    errors.append(f"Action {i}: bucket not found")
                    continue
                _ec = req.ec
                _ppm = req.ppm
                if _ec is not None and _ppm is None:
                    _ppm = round(_ec * 500.0, 1)
                elif _ppm is not None and _ec is None:
                    _ec = round(_ppm / 500.0, 3)
                for bucket in buckets:
                    reading = BucketSensorReading(
                        tenant_id=user.tenant_id,
                        bucket_id=bucket.id,
                        ph=req.ph,
                        ec=_ec,
                        ppm=_ppm,
                        water_temp_f=req.water_temp_f,
                        recorded_at=action.client_timestamp,
                    )
                    session.add(reading)
                    readings_to_propagate.append(reading)
                    session.add(
                        JournalEntry(
                            tenant_id=user.tenant_id,
                            bucket_id=bucket.id,
                            event_type="water_change",
                            content=req.notes,
                            payload={
                                "ph": req.ph,
                                "ec": req.ec,
                                "ppm": req.ppm,
                                "water_temp_f": req.water_temp_f,
                                "volume_gal": req.volume_gal,
                                "source": "quick_log",
                            },
                            created_at=action.client_timestamp,
                        )
                    )
                succeeded += 1

            else:
                errors.append(f"Action {i}: unknown type '{action.type}'")
        except Exception as exc:
            errors.append(f"Action {i}: {exc!s}")

    # Propagate header readings to site buckets for RDWC grows
    if readings_to_propagate:
        await session.flush()
        from app.integrations.connectors.base import propagate_header_bucket_readings

        for reading in readings_to_propagate:
            await propagate_header_bucket_readings(session, str(reading.bucket_id), reading)

    await session.commit()
    return BatchResponse(
        processed=len(body.actions),
        succeeded=succeeded,
        failed=len(errors),
        errors=errors if errors else None,
    )
