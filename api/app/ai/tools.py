"""AI chat tools — allow Ollama to make updates on behalf of the user."""

from __future__ import annotations

import logging
from datetime import UTC
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


# ── Tool execution ───────────────────────────────────────────────────


async def execute_tool(
    tool_name: str,
    arguments: dict,
    *,
    session: AsyncSession,
    tenant_id: UUID,
    grow_id: UUID,
) -> str:
    """Execute a tool call and return a human-readable result string."""
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
            from datetime import datetime

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

        elif tool_name == "create_journal_entry":
            buckets = (
                (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow.id).limit(1))).scalars().all()
            )
            if not buckets:
                return "Error: no buckets found for this grow."
            entry = JournalEntry(
                tenant_id=tenant_id,
                bucket_id=buckets[0].id,
                event_type=arguments.get("event_type", "note"),
                content=arguments.get("content", ""),
            )
            session.add(entry)
            await session.commit()
            return f"Journal entry added: [{arguments.get('event_type', 'note')}] {arguments.get('content', '')}"

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
            if not policy_decision.allowed:
                reason = policy_decision.reason or "Blocked by integration action policy"
                return f"Blocked by integration policy: {reason}"

            result = await integration_service.trigger_sync(session, cfg=cfg)
            if result.error_message:
                return (
                    "Integration sync completed with issues: "
                    f"status={result.status}, readings={result.readings_count}, error={result.error_message}"
                )
            return f"Integration sync completed: status={result.status}, readings={result.readings_count}"

        else:
            return f"Unknown tool: {tool_name}"

    except Exception as e:
        logger.exception("Tool execution failed: %s", tool_name)
        return f"Error executing {tool_name}: {e}"
