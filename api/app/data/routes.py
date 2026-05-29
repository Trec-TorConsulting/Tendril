"""Data management routes — export (CSV, JSON)."""

from __future__ import annotations

import zipfile
from datetime import datetime
from io import BytesIO
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.data.service import (
    export_bucket_csv,
    export_grow_csv,
    export_journal_csv,
    export_sensor_data_csv,
    export_tasks_csv,
)

router = APIRouter()


@router.get("/export/bucket/{bucket_id}")
async def export_bucket(
    bucket_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    start: datetime | None = None,
    end: datetime | None = None,
):
    """Export sensor readings for a bucket as CSV. Optional date range filtering."""
    from app.grows.models import Bucket

    bucket = await session.get(Bucket, UUID(bucket_id))
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")

    if start or end:
        csv_data = await export_sensor_data_csv(session, bucket.id, start, end)
    else:
        csv_data = await export_bucket_csv(session, bucket.id)

    label = bucket.label or f"bucket-{str(bucket.id)[:8]}"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{label}-readings.csv"'},
    )


@router.get("/export/grow/{grow_id}")
async def export_grow(
    grow_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    include: Annotated[
        list[str] | None,
        Query(description="Sections to include: readings, tasks, journal. Default: all"),
    ] = None,
):
    """Export full grow data as CSV (sensor readings, tasks, journal)."""
    from app.grows.models import GrowCycle

    grow = await session.get(GrowCycle, UUID(grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    sections = include or ["readings", "tasks", "journal"]

    # If only one section, return single CSV
    if len(sections) == 1:
        if sections[0] == "readings":
            data = await export_grow_csv(session, grow.id)
        elif sections[0] == "tasks":
            data = await export_tasks_csv(session, grow.id)
        elif sections[0] == "journal":
            data = await export_journal_csv(session, grow.id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown section: {sections[0]}")

        label = grow.name or f"grow-{str(grow.id)[:8]}"
        return Response(
            content=data,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{label}-{sections[0]}.csv"'},
        )

    # Multiple sections → ZIP file
    label = grow.name or f"grow-{str(grow.id)[:8]}"
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        if "readings" in sections:
            data = await export_grow_csv(session, grow.id)
            zf.writestr(f"{label}-readings.csv", data)
        if "tasks" in sections:
            data = await export_tasks_csv(session, grow.id)
            zf.writestr(f"{label}-tasks.csv", data)
        if "journal" in sections:
            data = await export_journal_csv(session, grow.id)
            zf.writestr(f"{label}-journal.csv", data)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{label}-export.zip"'},
    )


@router.get("/export/all")
async def export_all(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Export all grow data for the tenant as a ZIP of CSVs (backup/migration)."""
    from sqlalchemy import select

    from app.grows.models import GrowCycle

    grows = (await session.execute(select(GrowCycle).where(GrowCycle.tenant_id == user.tenant_id))).scalars().all()

    if not grows:
        raise HTTPException(status_code=404, detail="No grows found")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for grow in grows:
            label = grow.name or f"grow-{str(grow.id)[:8]}"
            safe_label = label.replace("/", "-").replace("\\", "-")

            readings = await export_grow_csv(session, grow.id)
            zf.writestr(f"{safe_label}/readings.csv", readings)

            tasks = await export_tasks_csv(session, grow.id)
            zf.writestr(f"{safe_label}/tasks.csv", tasks)

            journal = await export_journal_csv(session, grow.id)
            zf.writestr(f"{safe_label}/journal.csv", journal)

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="tendril-export.zip"'},
    )


@router.get("/export/grow/{grow_id}/report")
async def export_grow_report_pdf(
    grow_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Generate a PDF report for a grow cycle with sensor stats, health evals, and journal."""
    from app.data.reports import generate_grow_report_pdf
    from app.grows.models import GrowCycle

    grow = await session.get(GrowCycle, UUID(grow_id))
    if not grow:
        raise HTTPException(status_code=404, detail="Grow not found")

    pdf_bytes = await generate_grow_report_pdf(session, UUID(grow_id))
    label = grow.name or f"grow-{str(grow.id)[:8]}"
    safe_label = label.replace("/", "-").replace("\\", "-")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_label}-report.pdf"'},
    )
