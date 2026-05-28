"""Internal endpoints for cluster-level system alerts (no user auth required).

Protected by a shared secret in the INTERNAL_ALERT_SECRET environment variable.
These routes should only be reachable from within the cluster.
"""

from __future__ import annotations

import logging
import os
import secrets

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import async_session_factory
from app.notifications.models import NotificationChannel
from app.notifications.service import dispatch_alert

logger = logging.getLogger("tendril.internal")

router = APIRouter()

INTERNAL_SECRET = os.environ.get("INTERNAL_ALERT_SECRET", "")


class InternalAlert(BaseModel):
    severity: str = "warning"
    subject: str
    body: str


@router.post("/internal/alert")
async def receive_internal_alert(
    payload: InternalAlert,
    x_internal_secret: str | None = Header(None),
) -> dict:
    """Receive an infrastructure alert and broadcast to all tenant notification channels."""
    # Validate secret (if configured)
    if INTERNAL_SECRET and (not x_internal_secret or not secrets.compare_digest(x_internal_secret, INTERNAL_SECRET)):
        raise HTTPException(status_code=403, detail="Invalid internal secret")

    async with async_session_factory() as session:
        # Get all distinct tenant_ids with enabled channels
        tenant_ids = (
            (
                await session.execute(
                    select(NotificationChannel.tenant_id)
                    .where(
                        NotificationChannel.enabled.is_(True),
                    )
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        dispatched = 0
        for tenant_id in tenant_ids:
            try:
                await dispatch_alert(session, tenant_id, payload.severity, payload.subject, payload.body)
                dispatched += 1
            except Exception as e:
                logger.warning("Failed to dispatch alert to tenant %s: %s", tenant_id, e)

        await session.commit()

    logger.info(
        "Internal alert dispatched: severity=%s subject=%s tenants=%d",
        payload.severity,
        payload.subject,
        dispatched,
    )
    return {"dispatched_to_tenants": dispatched}
