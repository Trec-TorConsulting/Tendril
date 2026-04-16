"""API key management — generate, list, revoke (Commercial only)."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.commercial.models import ApiKey

router = APIRouter()


# ---------- Schemas ----------

class ApiKeyCreate(BaseModel):
    name: str
    scopes: str = "read"  # comma-separated: read, write, admin
    expires_in_days: int | None = None  # None = no expiry

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: str
    last_used: str | None
    expires_at: str | None
    revoked: bool
    created_at: str

class ApiKeyCreated(ApiKeyResponse):
    key: str  # only returned on creation


def _to_response(k: ApiKey) -> ApiKeyResponse:
    return ApiKeyResponse(
        id=str(k.id), name=k.name, key_prefix=k.key_prefix,
        scopes=k.scopes,
        last_used=k.last_used.isoformat() if k.last_used else None,
        expires_at=k.expires_at.isoformat() if k.expires_at else None,
        revoked=k.revoked,
        created_at=k.created_at.isoformat(),
    )


async def _require_commercial(user: CurrentUser, session: AsyncSession) -> None:
    from app.tenants.models import Tenant
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or tenant.plan != "commercial":
        raise HTTPException(status_code=403, detail="API keys require Commercial plan")


# ---------- Endpoints ----------

@router.post("", status_code=201)
async def create_api_key(
    body: ApiKeyCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    await _require_commercial(user, session)

    # Validate scopes
    valid_scopes = {"read", "write", "admin"}
    requested = {s.strip() for s in body.scopes.split(",")}
    if not requested.issubset(valid_scopes):
        raise HTTPException(status_code=400, detail=f"Invalid scopes. Valid: {valid_scopes}")

    full_key, prefix = ApiKey.generate_key()
    key_hash = bcrypt.hashpw(full_key.encode(), bcrypt.gensalt()).decode()

    expires_at = None
    if body.expires_in_days:
        from datetime import datetime, timedelta, timezone
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

    api_key = ApiKey(
        tenant_id=user.tenant_id,
        created_by=user.user_id,
        name=body.name,
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=body.scopes,
        expires_at=expires_at,
    )
    session.add(api_key)
    await session.commit()
    await session.refresh(api_key)

    resp = _to_response(api_key)
    return ApiKeyCreated(**resp.model_dump(), key=full_key)


@router.get("")
async def list_api_keys(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    await _require_commercial(user, session)
    result = await session.execute(
        select(ApiKey).where(
            ApiKey.tenant_id == user.tenant_id,
            ApiKey.revoked.is_(False),
        ).order_by(ApiKey.created_at.desc())
    )
    return [_to_response(k) for k in result.scalars().all()]


@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    api_key = await session.get(ApiKey, UUID(key_id))
    if not api_key or api_key.tenant_id != user.tenant_id:
        raise HTTPException(status_code=404, detail="API key not found")
    api_key.revoked = True
    await session.commit()
