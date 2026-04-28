"""Task management API — create, assign, complete, recurring, calendar."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_current_user, get_tenant_session, require_role
from app.commercial.models import Task
from app.pagination import PaginatedResponse, PaginationParams, paginate
from app.tenants.models import Tenant

router = APIRouter()


# ---------- Schemas ----------

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: str = "medium"
    category: str | None = None
    assigned_to: str | None = None
    grow_cycle_id: str | None = None
    tent_id: str | None = None
    bucket_id: str | None = None
    due_date: str | None = None  # ISO datetime
    recurring: str | None = None  # daily, weekly, biweekly, monthly


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    assigned_to: str | None = None
    due_date: str | None = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    category: str | None
    source: str
    assigned_to: str | None
    created_by: str
    grow_cycle_id: str | None
    tent_id: str | None
    bucket_id: str | None
    due_date: str | None
    completed_at: str | None
    recurring: str | None
    created_at: str


def _to_response(t: Task) -> TaskResponse:
    return TaskResponse(
        id=str(t.id),
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority,
        category=t.category,
        source=t.source,
        assigned_to=str(t.assigned_to) if t.assigned_to else None,
        created_by=str(t.created_by),
        grow_cycle_id=str(t.grow_cycle_id) if t.grow_cycle_id else None,
        tent_id=str(t.tent_id) if t.tent_id else None,
        bucket_id=str(t.bucket_id) if t.bucket_id else None,
        due_date=t.due_date.isoformat() if t.due_date else None,
        completed_at=t.completed_at.isoformat() if t.completed_at else None,
        recurring=t.recurring,
        created_at=t.created_at.isoformat(),
    )


# ---------- CRUD ----------

@router.post("", status_code=201)
async def create_task(
    body: TaskCreate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Create a new task (commercial plan required)."""
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or tenant.plan != "commercial":
        raise HTTPException(status_code=403, detail="Task management requires Commercial plan")
    task = Task(
        tenant_id=user.tenant_id,
        title=body.title,
        description=body.description,
        priority=body.priority,
        category=body.category,
        source="manual",
        assigned_to=UUID(body.assigned_to) if body.assigned_to else None,
        created_by=user.user_id,
        grow_cycle_id=UUID(body.grow_cycle_id) if body.grow_cycle_id else None,
        tent_id=UUID(body.tent_id) if body.tent_id else None,
        bucket_id=UUID(body.bucket_id) if body.bucket_id else None,
        due_date=datetime.fromisoformat(body.due_date) if body.due_date else None,
        recurring=body.recurring,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return _to_response(task)


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    pagination: Annotated[PaginationParams, Depends()],
    status: str | None = Query(None),
    category: str | None = Query(None),
    grow_cycle_id: str | None = Query(None),
    assigned_to: str | None = Query(None),
    due_from: str | None = Query(None),
    due_to: str | None = Query(None),
):
    """List tasks with optional status, category, and date filtering."""
    query = select(Task).where(Task.tenant_id == user.tenant_id)
    if status:
        query = query.where(Task.status == status)
    if category:
        query = query.where(Task.category == category)
    if grow_cycle_id:
        query = query.where(Task.grow_cycle_id == UUID(grow_cycle_id))
    if assigned_to:
        query = query.where(Task.assigned_to == UUID(assigned_to))
    if due_from:
        query = query.where(Task.due_date >= datetime.fromisoformat(due_from))
    if due_to:
        query = query.where(Task.due_date <= datetime.fromisoformat(due_to))
    query = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc())
    items, total = await paginate(session, query, pagination)
    return PaginatedResponse(
        items=[_to_response(t) for t in items],
        total=total, page=pagination.page, page_size=pagination.page_size,
    )


@router.get("/calendar")
async def calendar_tasks(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    start: str = Query(..., description="ISO start date"),
    end: str = Query(..., description="ISO end date"),
):
    """Get tasks for calendar view within a date range."""
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    result = await session.execute(
        select(Task)
        .where(Task.tenant_id == user.tenant_id, Task.due_date >= start_dt, Task.due_date <= end_dt)
        .order_by(Task.due_date.asc())
    )
    return [_to_response(t) for t in result.scalars().all()]


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a task by ID."""
    task = await session.get(Task, UUID(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(task)


@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    body: TaskUpdate,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Update a task's details."""
    task = await session.get(Task, UUID(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if body.title is not None:
        task.title = body.title
    if body.description is not None:
        task.description = body.description
    if body.priority is not None:
        task.priority = body.priority
    if body.category is not None:
        task.category = body.category
    if body.assigned_to is not None:
        task.assigned_to = UUID(body.assigned_to)
    if body.due_date is not None:
        task.due_date = datetime.fromisoformat(body.due_date)
    if body.status is not None:
        task.status = body.status
        if body.status == "completed":
            task.completed_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(task)
    return _to_response(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Soft-delete a task."""
    task = await session.get(Task, UUID(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await session.delete(task)
    await session.commit()


@router.post("/{task_id}/complete")
async def complete_task(
    task_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Mark a task as completed. Creates next recurring instance if applicable."""
    task = await session.get(Task, UUID(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc)

    # Create next recurring task
    if task.recurring and task.due_date:
        from datetime import timedelta
        delta_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "biweekly": timedelta(weeks=2),
            "monthly": timedelta(days=30),
        }
        delta = delta_map.get(task.recurring)
        if delta:
            next_task = Task(
                tenant_id=task.tenant_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                category=task.category,
                source=task.source,
                assigned_to=task.assigned_to,
                created_by=task.created_by,
                grow_cycle_id=task.grow_cycle_id,
                tent_id=task.tent_id,
                bucket_id=task.bucket_id,
                due_date=task.due_date + delta,
                recurring=task.recurring,
                recurring_parent_id=task.id,
            )
            session.add(next_task)

    await session.commit()
    await session.refresh(task)
    return _to_response(task)
