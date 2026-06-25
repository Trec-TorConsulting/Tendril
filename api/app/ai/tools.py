"""AI chat tools — allow Ollama to make updates on behalf of the user."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.integration_policy import evaluate_integration_action_policy

logger = logging.getLogger("tendril.ai.tools")

# ── Ollama tool schemas ──────────────────────────────────────────────

CHAT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "update_grow_stage",
            "description": "Update the current growth stage of the active grow cycle. Use when the user says they want to change or advance the stage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stage": {
                        "type": "string",
                        "description": "The new growth stage",
                        "enum": [
                            "seedling",
                            "vegetative",
                            "flowering",
                            "ripening",
                            "harvesting",
                            "drying",
                            "curing",
                        ],
                    },
                },
                "required": ["stage"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_grow",
            "description": "Update the grow cycle's name, status, or notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "New name for the grow cycle"},
                    "status": {
                        "type": "string",
                        "description": "New status",
                        "enum": ["active", "harvesting", "completed", "archived"],
                    },
                    "notes": {"type": "string", "description": "Updated grow notes"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a single follow-up task for the grower. Use for safe reminders, to-dos, or documented next steps that do not control equipment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Short task title"},
                    "description": {"type": "string", "description": "Optional details or checklist notes"},
                    "priority": {
                        "type": "string",
                        "description": "Task priority",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "category": {"type": "string", "description": "Optional task category label"},
                    "due_date": {
                        "type": "string",
                        "description": "Optional ISO-8601 due date/time",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_checklist",
            "description": "Create a recommended checklist as multiple safe follow-up tasks. Use for prep lists, maintenance runs, or staged reminders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Checklist title or theme"},
                    "items": {
                        "type": "array",
                        "description": "Checklist items to turn into tasks",
                        "items": {"type": "string"},
                        "minItems": 1,
                    },
                    "priority": {
                        "type": "string",
                        "description": "Default priority for created tasks",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "category": {"type": "string", "description": "Optional shared task category label"},
                    "due_date": {
                        "type": "string",
                        "description": "Optional ISO-8601 due date/time for all checklist tasks",
                    },
                },
                "required": ["title", "items"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_journal_entry",
            "description": "Add a journal entry or note to the grow log. Use for recording feedings, water changes, training, observations, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "Type of journal event",
                        "enum": [
                            "note",
                            "feeding",
                            "water_change",
                            "training",
                            "transplant",
                            "defoliation",
                            "topping",
                        ],
                    },
                    "content": {"type": "string", "description": "Description of what happened"},
                },
                "required": ["event_type", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_feeding_schedule",
            "description": "Update the target PPM, target EC, or notes for a feeding schedule at the current growth stage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_ppm": {"type": "number", "description": "New target PPM value"},
                    "target_ec": {"type": "number", "description": "New target EC value"},
                    "notes": {"type": "string", "description": "Feeding schedule notes"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_bucket",
            "description": "Update a bucket/plant's strain name, label, or growth stage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bucket_position": {
                        "type": "integer",
                        "description": "Position number of the bucket (1-based)",
                    },
                    "strain_name": {"type": "string", "description": "New strain name"},
                    "label": {"type": "string", "description": "New label for the bucket"},
                    "growth_stage": {
                        "type": "string",
                        "description": "New growth stage for the bucket",
                        "enum": [
                            "seedling",
                            "vegetative",
                            "flowering",
                            "ripening",
                            "harvesting",
                            "drying",
                            "curing",
                        ],
                    },
                },
                "required": ["bucket_position"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "integration_trigger_sync",
            "description": "Trigger an immediate integration sync for one configured connector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "integration_id": {
                        "type": "string",
                        "description": "Integration config ID to sync",
                    },
                    "integration_type": {
                        "type": "string",
                        "description": "Connector type hint (pulse, openweather, ecowitt)",
                    },
                },
                "required": ["integration_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "integration_control_command",
            "description": "Prepare a high-risk outbound integration control command for approval.",
            "parameters": {
                "type": "object",
                "properties": {
                    "integration_id": {
                        "type": "string",
                        "description": "Integration config ID to target",
                    },
                    "command": {
                        "type": "string",
                        "description": "Control command to send after approval",
                    },
                    "integration_type": {
                        "type": "string",
                        "description": "Connector type hint (pulse, openweather, ecowitt)",
                    },
                },
                "required": ["integration_id", "command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_tent",
            "description": "Update the grow space/tent name or notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "New name for the tent/space"},
                    "notes": {"type": "string", "description": "Updated notes"},
                },
            },
        },
    },
]


def _parse_due_date(raw_due_date: Any) -> datetime | None:
    if not isinstance(raw_due_date, str) or not raw_due_date.strip():
        return None

    parsed = datetime.fromisoformat(raw_due_date.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


async def _get_task_owner_id(session: AsyncSession, *, tenant_id: UUID) -> UUID | None:
    from app.tenants.models import TenantMembership, TenantRole

    return (
        await session.execute(
            select(TenantMembership.user_id)
            .where(TenantMembership.tenant_id == tenant_id, TenantMembership.role == TenantRole.admin)
            .limit(1)
        )
    ).scalar_one_or_none()


async def _tenant_supports_tasks(session: AsyncSession, *, tenant_id: UUID) -> bool:
    from app.tenants.models import Tenant

    tenant = await session.get(Tenant, tenant_id)
    return tenant is not None and tenant.plan == "commercial"


# ── Tool execution ───────────────────────────────────────────────────


async def execute_tool(
    tool_name: str,
    arguments: dict,
    *,
    session: AsyncSession,
    tenant_id: UUID,
    grow_id: UUID,
) -> str | dict[str, Any]:
    """Execute a tool call and return a human-readable result string."""
    from app.ai import service as ai_service
    from app.commercial.models import Task
    from app.grows.models import (
        Bucket,
        FeedingSchedule,
        GrowCycle,
        JournalEntry,
        Tent,
    )
    from app.integrations import service as integration_service

    grow = await session.get(GrowCycle, grow_id)
    if not grow or grow.tenant_id != tenant_id:
        return "Error: grow not found or access denied."

    try:
        if tool_name == "update_grow_stage":
            stage = arguments.get("stage", "")
            old = grow.stage
            grow.stage = stage
            # Auto-record milestone
            if grow.milestones is None:
                grow.milestones = {}
            grow.milestones = {**grow.milestones, stage: datetime.now(UTC).isoformat()}
            await session.commit()
            return f"Updated grow stage from '{old}' to '{stage}'."

        elif tool_name == "update_grow":
            changes = []
            if "name" in arguments:
                grow.name = arguments["name"]
                changes.append(f"name → '{arguments['name']}'")
            if "status" in arguments:
                grow.status = arguments["status"]
                changes.append(f"status → '{arguments['status']}'")
            if "notes" in arguments:
                grow.notes = arguments["notes"]
                changes.append("notes updated")
            await session.commit()
            return f"Updated grow: {', '.join(changes)}." if changes else "No changes specified."

        elif tool_name == "create_task":
            title = str(arguments.get("title", "")).strip()
            if not title:
                return "Error: title is required."

            description = arguments.get("description")
            if description is not None and not isinstance(description, str):
                description = str(description)
            priority = str(arguments.get("priority") or "medium")
            category = arguments.get("category")
            if category is not None and not isinstance(category, str):
                category = str(category)

            action = await ai_service.create_agent_action(
                session,
                tenant_id=tenant_id,
                source="chat",
                action_type="create_task",
                title=f"Create task: {title}"[:255],
                idempotency_key=ai_service.build_agent_action_idempotency_key(
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="create_task",
                    grow_cycle_id=grow.id,
                    conversation_id=None,
                    dedupe_token=f"{title}:{description}:{datetime.now(UTC).isoformat()}",
                ),
                grow_cycle_id=grow.id,
                risk_level="low",
                requires_approval=False,
                auto_approved=True,
                summary=description or title,
                metadata_json={
                    "phase": "chat",
                    "safe_action": True,
                    "priority": priority,
                    "category": category,
                },
                evidence_json={
                    "recommended_action": title,
                    "description": description,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_APPROVED,
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_EXECUTING,
                execution_json={"target": "task"},
            )

            if not await _tenant_supports_tasks(session, tenant_id=tenant_id):
                error_text = "Task management requires Commercial plan"
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "task", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            owner_id = await _get_task_owner_id(session, tenant_id=tenant_id)
            if owner_id is None:
                error_text = "Error: no tenant admin available to own the task."
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "task", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            try:
                due_date = _parse_due_date(arguments.get("due_date"))
            except ValueError:
                error_text = "Error: due_date must be a valid ISO-8601 datetime."
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "task", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            task = Task(
                tenant_id=tenant_id,
                title=title[:500],
                description=description,
                priority=priority,
                category=category,
                source="ai",
                created_by=owner_id,
                grow_cycle_id=grow.id,
                tent_id=grow.tent_id,
                due_date=due_date,
                routine="on_demand",
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_COMPLETED,
                execution_json={
                    "target": "task",
                    "task_id": str(task.id),
                    "priority": task.priority,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_VERIFIED,
                verification_json={
                    "result": "task_created",
                    "task_id": str(task.id),
                },
            )
            return {
                "status": "completed",
                "phase": "completed",
                "action_id": str(action.id),
                "result": {
                    "task_id": str(task.id),
                    "title": task.title,
                },
            }

        elif tool_name == "generate_checklist":
            checklist_title = str(arguments.get("title", "")).strip()
            if not checklist_title:
                return "Error: title is required."

            raw_items = arguments.get("items")
            if not isinstance(raw_items, list):
                return "Error: items must be a list of checklist strings."
            items = [str(item).strip() for item in raw_items if str(item).strip()]
            if not items:
                return "Error: at least one checklist item is required."

            priority = str(arguments.get("priority") or "medium")
            category = arguments.get("category")
            if category is not None and not isinstance(category, str):
                category = str(category)

            action = await ai_service.create_agent_action(
                session,
                tenant_id=tenant_id,
                source="chat",
                action_type="generate_checklist",
                title=f"Generate checklist: {checklist_title}"[:255],
                idempotency_key=ai_service.build_agent_action_idempotency_key(
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="generate_checklist",
                    grow_cycle_id=grow.id,
                    conversation_id=None,
                    dedupe_token=f"{checklist_title}:{'|'.join(items)}:{datetime.now(UTC).isoformat()}",
                ),
                grow_cycle_id=grow.id,
                risk_level="low",
                requires_approval=False,
                auto_approved=True,
                summary=f"{checklist_title} ({len(items)} items)",
                metadata_json={
                    "phase": "chat",
                    "safe_action": True,
                    "priority": priority,
                    "category": category,
                    "item_count": len(items),
                },
                evidence_json={
                    "checklist_title": checklist_title,
                    "items": items,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_APPROVED,
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_EXECUTING,
                execution_json={"target": "checklist", "item_count": len(items)},
            )

            if not await _tenant_supports_tasks(session, tenant_id=tenant_id):
                error_text = "Task management requires Commercial plan"
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "checklist", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            owner_id = await _get_task_owner_id(session, tenant_id=tenant_id)
            if owner_id is None:
                error_text = "Error: no tenant admin available to own checklist tasks."
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "checklist", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            try:
                due_date = _parse_due_date(arguments.get("due_date"))
            except ValueError:
                error_text = "Error: due_date must be a valid ISO-8601 datetime."
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={"target": "checklist", "error": error_text},
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }

            created_tasks: list[Task] = []
            for index, item in enumerate(items, start=1):
                task = Task(
                    tenant_id=tenant_id,
                    title=item[:500],
                    description=f"Checklist: {checklist_title}\n\nItem {index} of {len(items)}",
                    priority=priority,
                    category=category,
                    source="ai",
                    created_by=owner_id,
                    grow_cycle_id=grow.id,
                    tent_id=grow.tent_id,
                    due_date=due_date,
                    routine="on_demand",
                )
                session.add(task)
                created_tasks.append(task)

            await session.commit()
            for task in created_tasks:
                await session.refresh(task)

            task_ids = [str(task.id) for task in created_tasks]
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_COMPLETED,
                execution_json={
                    "target": "checklist",
                    "checklist_title": checklist_title,
                    "task_count": len(created_tasks),
                    "task_ids": task_ids,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_VERIFIED,
                verification_json={
                    "result": "checklist_created",
                    "checklist_title": checklist_title,
                    "task_count": len(created_tasks),
                    "task_ids": task_ids,
                },
            )
            return {
                "status": "completed",
                "phase": "completed",
                "action_id": str(action.id),
                "result": {
                    "checklist_title": checklist_title,
                    "task_count": len(created_tasks),
                    "task_ids": task_ids,
                },
            }

        elif tool_name == "create_journal_entry":
            event_type = arguments.get("event_type", "note")
            content = arguments.get("content", "")
            action = await ai_service.create_agent_action(
                session,
                tenant_id=tenant_id,
                source="chat",
                action_type="create_journal_entry",
                title=f"Create journal entry: {event_type}",
                idempotency_key=ai_service.build_agent_action_idempotency_key(
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="create_journal_entry",
                    grow_cycle_id=grow.id,
                    conversation_id=None,
                    dedupe_token=f"{event_type}:{content}:{datetime.now(UTC).isoformat()}",
                ),
                grow_cycle_id=grow.id,
                risk_level="low",
                requires_approval=False,
                auto_approved=True,
                summary=content,
                metadata_json={
                    "phase": "chat",
                    "safe_action": True,
                    "event_type": event_type,
                },
                evidence_json={
                    "recommended_action": content or f"Create {event_type} journal entry",
                    "event_type": event_type,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_APPROVED,
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_EXECUTING,
                execution_json={
                    "target": "journal_entry",
                    "event_type": event_type,
                },
            )

            buckets = (
                (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id).limit(1))).scalars().all()
            )
            if not buckets:
                error_text = "Error: no buckets found for this grow."
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={
                        "target": "journal_entry",
                        "event_type": event_type,
                        "error": error_text,
                    },
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                }
            entry = JournalEntry(
                tenant_id=tenant_id,
                bucket_id=buckets[0].id,
                event_type=event_type,
                content=content,
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_COMPLETED,
                execution_json={
                    "target": "journal_entry",
                    "event_type": event_type,
                    "journal_entry_id": str(entry.id),
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_VERIFIED,
                verification_json={
                    "result": "journal_entry_created",
                    "journal_entry_id": str(entry.id),
                    "event_type": event_type,
                },
            )
            return {
                "status": "completed",
                "phase": "completed",
                "action_id": str(action.id),
                "result": {
                    "journal_entry_id": str(entry.id),
                    "event_type": event_type,
                },
            }

        elif tool_name == "update_feeding_schedule":
            schedules = (
                (
                    await session.execute(
                        select(FeedingSchedule).where(
                            FeedingSchedule.grow_cycle_id == grow.id,
                            FeedingSchedule.stage == grow.stage,
                        )
                    )
                )
                .scalars()
                .all()
            )
            if not schedules:
                return f"No feeding schedule found for stage '{grow.stage}'."
            sched = schedules[0]
            changes = []
            if "target_ppm" in arguments:
                sched.target_ppm = arguments["target_ppm"]
                changes.append(f"target PPM → {arguments['target_ppm']}")
            if "target_ec" in arguments:
                sched.target_ec = arguments["target_ec"]
                changes.append(f"target EC → {arguments['target_ec']}")
            if "notes" in arguments:
                sched.notes = arguments["notes"]
                changes.append("notes updated")
            await session.commit()
            return f"Feeding schedule updated: {', '.join(changes)}." if changes else "No changes specified."

        elif tool_name == "update_bucket":
            pos = arguments.get("bucket_position", 1)
            bucket = (
                await session.execute(
                    select(Bucket).where(
                        Bucket.grow_cycle_id == grow.id,
                        Bucket.position == pos,
                    )
                )
            ).scalar_one_or_none()
            if not bucket:
                return f"No bucket found at position {pos}."
            changes = []
            if "strain_name" in arguments:
                bucket.strain_name = arguments["strain_name"]
                changes.append(f"strain → '{arguments['strain_name']}'")
            if "label" in arguments:
                bucket.label = arguments["label"]
                changes.append(f"label → '{arguments['label']}'")
            if "growth_stage" in arguments:
                bucket.growth_stage = arguments["growth_stage"]
                changes.append(f"stage → '{arguments['growth_stage']}'")
            await session.commit()
            return f"Bucket {pos} updated: {', '.join(changes)}." if changes else "No changes specified."

        elif tool_name == "update_tent":
            tent = await session.get(Tent, grow.tent_id)
            if not tent:
                return "Error: tent not found."
            changes = []
            if "name" in arguments:
                tent.name = arguments["name"]
                changes.append(f"name → '{arguments['name']}'")
            if "notes" in arguments:
                tent.notes = arguments["notes"]
                changes.append("notes updated")
            await session.commit()
            return f"Tent updated: {', '.join(changes)}." if changes else "No changes specified."

        elif tool_name == "integration_trigger_sync":
            raw_integration_id = arguments.get("integration_id")
            if not isinstance(raw_integration_id, str) or not raw_integration_id.strip():
                return "Error: integration_id is required."

            try:
                integration_id = UUID(raw_integration_id.strip())
            except ValueError:
                return "Error: integration_id must be a valid UUID."

            cfg = await integration_service.get_integration(
                session,
                integration_id,
                tenant_id=tenant_id,
            )
            if cfg is None:
                return "Error: integration not found or access denied."

            policy_decision = evaluate_integration_action_policy(
                integration_type=cfg.type,
                operation="trigger_sync",
            )
            policy_payload = {
                "integration_type": cfg.type,
                "operation": "trigger_sync",
                "supported": policy_decision.supported,
                "allowed": policy_decision.allowed,
                "risk_level": policy_decision.risk_level,
                "requires_approval": policy_decision.requires_approval,
                "requires_simulation": policy_decision.requires_simulation,
            }
            if not policy_decision.allowed:
                reason = policy_decision.reason or "Blocked by integration action policy"
                action = await ai_service.create_agent_action(
                    session,
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="integration_trigger_sync",
                    title=f"Trigger sync for {cfg.name}",
                    idempotency_key=ai_service.build_agent_action_idempotency_key(
                        tenant_id=tenant_id,
                        source="chat",
                        action_type="integration_trigger_sync",
                        grow_cycle_id=grow.id,
                        conversation_id=None,
                        dedupe_token=f"{cfg.id}:blocked:{datetime.now(UTC).isoformat()}",
                    ),
                    grow_cycle_id=grow.id,
                    risk_level=policy_decision.risk_level,
                    requires_approval=policy_decision.requires_approval,
                    auto_approved=False,
                    summary=reason,
                    metadata_json={
                        "integration_id": str(cfg.id),
                        "integration_name": cfg.name,
                        "integration_type": cfg.type,
                        "operation": "trigger_sync",
                        "policy": {
                            "supported": policy_decision.supported,
                            "allowed": policy_decision.allowed,
                            "risk_level": policy_decision.risk_level,
                            "requires_approval": policy_decision.requires_approval,
                            "requires_simulation": policy_decision.requires_simulation,
                            "reason": reason,
                        },
                    },
                    evidence_json={
                        "integration_id": str(cfg.id),
                        "integration_type": cfg.type,
                        "operation": "trigger_sync",
                    },
                )
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_BLOCKED,
                    execution_json={
                        "target": "integration",
                        "integration_id": str(cfg.id),
                        "integration_type": cfg.type,
                        "operation": "trigger_sync",
                        "error": reason,
                    },
                )
                return {
                    "status": "blocked",
                    "phase": "blocked",
                    "action_id": str(action.id),
                    "error": reason,
                    "policy": {**policy_payload, "reason": reason},
                }

            action = await ai_service.create_agent_action(
                session,
                tenant_id=tenant_id,
                source="chat",
                action_type="integration_trigger_sync",
                title=f"Trigger sync for {cfg.name}",
                idempotency_key=ai_service.build_agent_action_idempotency_key(
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="integration_trigger_sync",
                    grow_cycle_id=grow.id,
                    conversation_id=None,
                    dedupe_token=f"{cfg.id}:execute:{datetime.now(UTC).isoformat()}",
                ),
                grow_cycle_id=grow.id,
                risk_level=policy_decision.risk_level,
                requires_approval=policy_decision.requires_approval,
                auto_approved=not policy_decision.requires_approval,
                summary=f"Trigger sync for {cfg.name}",
                metadata_json={
                    "integration_id": str(cfg.id),
                    "integration_name": cfg.name,
                    "integration_type": cfg.type,
                    "operation": "trigger_sync",
                    "policy": policy_payload,
                },
                evidence_json={
                    "integration_id": str(cfg.id),
                    "integration_type": cfg.type,
                    "operation": "trigger_sync",
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_APPROVED,
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_EXECUTING,
                execution_json={
                    "target": "integration",
                    "integration_id": str(cfg.id),
                    "integration_type": cfg.type,
                    "operation": "trigger_sync",
                },
            )

            result = await integration_service.trigger_sync(session, cfg=cfg)
            if result.error_message or result.status == "error":
                error_text = result.error_message or "Integration sync failed"
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_FAILED,
                    execution_json={
                        "target": "integration",
                        "integration_id": str(cfg.id),
                        "integration_type": cfg.type,
                        "operation": "trigger_sync",
                        "sync_status": result.status,
                        "readings_count": result.readings_count,
                        "error": error_text,
                    },
                )
                return {
                    "status": "failed",
                    "phase": "failed",
                    "action_id": str(action.id),
                    "error": error_text,
                    "result": {
                        "sync_status": result.status,
                        "readings_count": result.readings_count,
                    },
                    "policy": policy_payload,
                }

            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_COMPLETED,
                execution_json={
                    "target": "integration",
                    "integration_id": str(cfg.id),
                    "integration_type": cfg.type,
                    "operation": "trigger_sync",
                    "sync_status": result.status,
                    "readings_count": result.readings_count,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_VERIFIED,
                verification_json={
                    "result": "integration_sync_completed",
                    "integration_id": str(cfg.id),
                    "integration_type": cfg.type,
                    "operation": "trigger_sync",
                    "sync_status": result.status,
                    "readings_count": result.readings_count,
                },
            )
            return {
                "status": "completed",
                "phase": "completed",
                "action_id": str(action.id),
                "result": {
                    "sync_status": result.status,
                    "readings_count": result.readings_count,
                },
                "policy": policy_payload,
            }

        elif tool_name == "integration_control_command":
            raw_integration_id = arguments.get("integration_id")
            if not isinstance(raw_integration_id, str) or not raw_integration_id.strip():
                return "Error: integration_id is required."

            command = arguments.get("command")
            if not isinstance(command, str) or not command.strip():
                return "Error: command is required."

            try:
                integration_id = UUID(raw_integration_id.strip())
            except ValueError:
                return "Error: integration_id must be a valid UUID."

            cfg = await integration_service.get_integration(
                session,
                integration_id,
                tenant_id=tenant_id,
            )
            if cfg is None:
                return "Error: integration not found or access denied."

            policy_decision = evaluate_integration_action_policy(
                integration_type=cfg.type,
                operation="outbound_control",
            )
            policy_payload = {
                "integration_type": cfg.type,
                "operation": "outbound_control",
                "supported": policy_decision.supported,
                "allowed": policy_decision.allowed,
                "risk_level": policy_decision.risk_level,
                "requires_approval": policy_decision.requires_approval,
                "requires_simulation": policy_decision.requires_simulation,
            }

            if not policy_decision.allowed:
                reason = policy_decision.reason or "Blocked by integration action policy"
                action = await ai_service.create_agent_action(
                    session,
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="integration_control_command",
                    title=f"Control command for {cfg.name}",
                    idempotency_key=ai_service.build_agent_action_idempotency_key(
                        tenant_id=tenant_id,
                        source="chat",
                        action_type="integration_control_command",
                        grow_cycle_id=grow.id,
                        conversation_id=None,
                        dedupe_token=f"{cfg.id}:control:blocked:{datetime.now(UTC).isoformat()}",
                    ),
                    grow_cycle_id=grow.id,
                    risk_level=policy_decision.risk_level,
                    requires_approval=policy_decision.requires_approval,
                    auto_approved=False,
                    summary=reason,
                    metadata_json={
                        "integration_id": str(cfg.id),
                        "integration_name": cfg.name,
                        "integration_type": cfg.type,
                        "operation": "outbound_control",
                        "command": command,
                        "policy": {**policy_payload, "reason": reason},
                    },
                    evidence_json={
                        "integration_id": str(cfg.id),
                        "integration_type": cfg.type,
                        "operation": "outbound_control",
                        "command": command,
                    },
                )
                await ai_service.transition_agent_action(
                    session,
                    action,
                    next_status=ai_service.AGENT_ACTION_STATUS_BLOCKED,
                    execution_json={
                        "target": "integration",
                        "integration_id": str(cfg.id),
                        "integration_type": cfg.type,
                        "operation": "outbound_control",
                        "command": command,
                        "error": reason,
                    },
                )
                return {
                    "status": "blocked",
                    "phase": "blocked",
                    "action_id": str(action.id),
                    "error": reason,
                    "policy": {**policy_payload, "reason": reason},
                }

            approval_reason = (
                "High-risk integration control command requires approval and simulation before execution"
            )
            action = await ai_service.create_agent_action(
                session,
                tenant_id=tenant_id,
                source="chat",
                action_type="integration_control_command",
                title=f"Control command for {cfg.name}",
                idempotency_key=ai_service.build_agent_action_idempotency_key(
                    tenant_id=tenant_id,
                    source="chat",
                    action_type="integration_control_command",
                    grow_cycle_id=grow.id,
                    conversation_id=None,
                    dedupe_token=f"{cfg.id}:control:pending:{datetime.now(UTC).isoformat()}",
                ),
                grow_cycle_id=grow.id,
                risk_level=policy_decision.risk_level,
                requires_approval=True,
                auto_approved=False,
                summary=command,
                metadata_json={
                    "integration_id": str(cfg.id),
                    "integration_name": cfg.name,
                    "integration_type": cfg.type,
                    "operation": "outbound_control",
                    "command": command,
                    "policy": policy_payload,
                },
                evidence_json={
                    "integration_id": str(cfg.id),
                    "integration_type": cfg.type,
                    "operation": "outbound_control",
                    "command": command,
                },
            )
            await ai_service.transition_agent_action(
                session,
                action,
                next_status=ai_service.AGENT_ACTION_STATUS_PENDING_APPROVAL,
            )
            await ai_service.create_agent_action_approval(
                session,
                tenant_id=tenant_id,
                action_id=action.id,
                requested_by_user_id=None,
                reason=approval_reason,
            )
            return {
                "status": "pending_approval",
                "phase": "pending_approval",
                "action_id": str(action.id),
                "result": {
                    "message": "Command queued for approval",
                },
                "policy": {**policy_payload, "reason": approval_reason},
            }

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        logger.exception("Tool execution failed: %s", tool_name)
        return f"Error executing {tool_name}: {e}"
