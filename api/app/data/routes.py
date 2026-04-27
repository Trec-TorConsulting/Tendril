"""Data management routes — export."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.data.service import export_bucket_csv

router = APIRouter()


@router.get("/export/bucket/{bucket_id}")
async def export_bucket(
    bucket_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Export all sensor readings for a bucket as CSV."""
    from app.grows.models import Bucket

    bucket = await session.get(Bucket, UUID(bucket_id))
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")

    csv_data = await export_bucket_csv(session, bucket.id)
    label = bucket.label or f"bucket-{str(bucket.id)[:8]}"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{label}-readings.csv"'},
    )
