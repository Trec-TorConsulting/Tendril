"""Audit trail routes — filterable, paginated log viewer (Commercial only)."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.commercial.models import AuditLog

router = APIRouter()


# ---------- Schemas ----------

class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    before_value: dict | None
    after_value: dict | None
    ip_address: str | None
    created_at: str

class AuditLogPage(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


def _to_response(log: AuditLog) -> AuditLogResponse:
    return AuditLogResponse(
        id=str(log.id), user_id=str(log.user_id),
        action=log.action, resource_type=log.resource_type,
        resource_id=log.resource_id,
        before_value=log.before_value, after_value=log.after_value,
        ip_address=log.ip_address,
        created_at=log.created_at.isoformat(),
    )


# ---------- Query ----------

@router.get("")
async def list_audit_logs(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    user_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List audit log entries (paginated, filterable)."""
    from app.tenants.models import Tenant
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or tenant.plan != "commercial":
        raise HTTPException(status_code=403, detail="Audit trail requires Commercial plan")

    query = select(AuditLog).where(AuditLog.tenant_id == user.tenant_id)
    count_query = select(func.count(AuditLog.id)).where(AuditLog.tenant_id == user.tenant_id)

    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
        count_query = count_query.where(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.where(AuditLog.user_id == UUID(user_id))
        count_query = count_query.where(AuditLog.user_id == UUID(user_id))

    total = (await session.execute(count_query)).scalar() or 0

    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(query)
    items = [_to_response(log) for log in result.scalars().all()]

    return AuditLogPage(items=items, total=total, page=page, page_size=page_size)


# ---------- Audit helper (used by other modules) ----------

async def record_audit(
    session: AsyncSession,
    tenant_id: UUID,
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: str,
    before_value: dict | None = None,
    after_value: dict | None = None,
    request: Request | None = None,
) -> None:
    """Record an audit log entry. Called from route handlers."""
    ip = None
    ua = None
    if request:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent", "")[:500]

    log = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before_value=before_value,
        after_value=after_value,
        ip_address=ip,
        user_agent=ua,
    )
    session.add(log)
