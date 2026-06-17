"""Conversation CRUD routes — persistent AI chat history.

This module is HTTP-only. All persistence and UUID coercion live in
``app.ai.service``.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service
from app.ai.models import Conversation, ConversationMessage
from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session
from app.pagination import PaginatedResponse, PaginationParams, paginate

router = APIRouter()


class ConversationCreate(BaseModel):
    grow_cycle_id: str | None = None
    title: str | None = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    metadata_json: dict | None = None
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_obj(cls, msg: ConversationMessage) -> MessageResponse:
        return cls(
            id=str(msg.id),
            role=msg.role,
            content=msg.content,
            metadata_json=msg.metadata_json,
            created_at=msg.created_at.isoformat(),
        )


class ConversationResponse(BaseModel):
    id: str
    grow_cycle_id: str | None
    title: str | None
    message_count: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_obj(cls, conv: Conversation) -> ConversationResponse:
        return cls(
            id=str(conv.id),
            grow_cycle_id=str(conv.grow_cycle_id) if conv.grow_cycle_id else None,
            title=conv.title,
            message_count=conv.message_count,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
        )


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse] = []


class ConversationUpdate(BaseModel):
    title: str | None = None


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new AI conversation."""
    assert user.tenant_id is not None  # guaranteed by get_tenant_session
    try:
        grow_cycle_id = service.parse_optional_uuid(body.grow_cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid grow_cycle_id") from exc
    conv = await service.create_conversation(
        session,
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        grow_cycle_id=grow_cycle_id,
        title=body.title,
    )
    return ConversationResponse.from_orm_obj(conv)


@router.get("", response_model=PaginatedResponse[ConversationResponse])
async def list_conversations(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    grow_cycle_id: str | None = None,
):
    """List conversations for the current user."""
    assert user.tenant_id is not None
    try:
        gc_id = service.parse_optional_uuid(grow_cycle_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid grow_cycle_id") from exc
    q = service.list_user_conversations_query(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        grow_cycle_id=gc_id,
    )
    items, total = await paginate(session, q, pagination)
    return PaginatedResponse(
        items=[ConversationResponse.from_orm_obj(c) for c in items],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a conversation with all messages."""
    assert user.tenant_id is not None
    conv = await service.get_conversation_with_messages(
        session, tenant_id=user.tenant_id, conversation_id=conversation_id
    )
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailResponse(
        id=str(conv.id),
        grow_cycle_id=str(conv.grow_cycle_id) if conv.grow_cycle_id else None,
        title=conv.title,
        message_count=conv.message_count,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[MessageResponse.from_orm_obj(m) for m in conv.messages],
    )


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    body: ConversationUpdate,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update conversation title."""
    assert user.tenant_id is not None
    conv = await service.get_conversation(session, tenant_id=user.tenant_id, conversation_id=conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if body.title is not None:
        await service.update_conversation_title(session, conv, title=body.title)
    return ConversationResponse.from_orm_obj(conv)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Delete a conversation and all its messages."""
    assert user.tenant_id is not None
    conv = await service.get_conversation(session, tenant_id=user.tenant_id, conversation_id=conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await service.delete_conversation(session, conv)
