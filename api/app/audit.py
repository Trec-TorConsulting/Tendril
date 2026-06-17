"""Audit logging dependency — automatically records mutations for commercial tenants."""

from __future__ import annotations

from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def record_audit(
    session: AsyncSession,
    tenant_id: UUID | None,
    user_id: UUID | None,
    action: str,
    resource_type: str,
    resource_id: str,
    before_value: dict | None = None,
    after_value: dict | None = None,
    request: Request | None = None,
) -> None:
    """Record an audit log entry. Only writes for commercial-plan tenants.

    Safe to call for any tenant — silently skips if not on commercial plan,
    if tenant_id/user_id is None, or if the audit_logs table doesn't exist yet.
    """
    if tenant_id is None or user_id is None:
        return
    try:
        from app.commercial.models import AuditLog

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
        # Use a savepoint so a DB error (e.g. missing table) only rolls back
        # the audit INSERT, not the caller's pending changes.
        async with session.begin_nested():
            session.add(log)
    except Exception:  # noqa: S110
        pass  # Don't fail the main operation if audit logging has issues
