"""Vision detection → draft record + approval-gated action generation.

Detections are advisory. This module maps actionable detection classes to a
cannabis quality-first concern, then routes each one through the existing
``grow-assistant-core`` agent-action lifecycle as an approval-gated proposal.
Nothing here mutates grow state: draft ``PestScoutEntry`` / ``HealthEval``
payloads are carried in the proposed action's metadata and only materialize when
a grower explicitly approves the action. This preserves the platform-wide
"no auto-mutation without a human gate" guarantee.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service as ai_service
from app.ai.models import AgentAction
from app.vision.contracts import VisionDetection

PEST_SCOUT_ACTION = "vision_pest_scout_draft"
HEALTH_EVAL_ACTION = "vision_health_eval_draft"

# Default per-concern confidence floor below which a detection is not actionable.
DEFAULT_MIN_CONFIDENCE = 0.5


@dataclass(frozen=True, slots=True)
class DetectionConcern:
    kind: str  # "pest_scout" | "health_eval"
    action_type: str
    pest_type: str  # insect | disease | animal | unknown (pest-scout only)
    species: str
    severity: str  # low | medium | high | critical
    min_confidence: float = DEFAULT_MIN_CONFIDENCE


# Keyword → concern rules, evaluated in order. Quality-threatening pathogens map
# to the highest severity because they degrade resin, terpenes, and cannabinoids
# fastest (see openspec/project.md cannabis-first philosophy).
_CONCERN_RULES: tuple[tuple[tuple[str, ...], DetectionConcern], ...] = (
    (
        ("powdery_mildew", "mildew", "botrytis", "bud_rot", "mold", "rot"),
        DetectionConcern("pest_scout", PEST_SCOUT_ACTION, "disease", "Mold / powdery mildew", "critical"),
    ),
    (
        ("spider_mite", "mite", "thrip", "aphid", "whitefly", "fungus_gnat", "gnat", "caterpillar"),
        DetectionConcern("pest_scout", PEST_SCOUT_ACTION, "insect", "Pest infestation", "high"),
    ),
    (
        ("blight", "rust", "leaf_spot", "septoria", "disease"),
        DetectionConcern("pest_scout", PEST_SCOUT_ACTION, "disease", "Plant disease", "high"),
    ),
    (
        (
            "nutrient_deficiency",
            "deficiency",
            "nitrogen",
            "phosphorus",
            "potassium",
            "calcium",
            "magnesium",
            "nutrient_burn",
        ),
        DetectionConcern("health_eval", HEALTH_EVAL_ACTION, "unknown", "Nutrient deficiency", "medium"),
    ),
    (
        ("pest", "insect"),
        DetectionConcern("pest_scout", PEST_SCOUT_ACTION, "unknown", "Possible pest / disease", "medium"),
    ),
)

# Informational classes that never warrant an action on their own.
_BENIGN_TOKENS = ("plant", "canopy", "bud", "flower", "trichome", "stage", "beneficial", "healthy")


def _risk_from_severity(severity: str) -> str:
    return {"critical": "high", "high": "high", "medium": "medium", "low": "low"}.get(severity, "low")


def map_detection_to_concern(class_name: str, confidence: float) -> DetectionConcern | None:
    """Return the quality-first concern for a detection, or ``None`` if benign.

    Non-actionable/informational classes and low-confidence detections return
    ``None`` so no draft is proposed.
    """
    normalized = class_name.strip().lower().replace("-", "_").replace(" ", "_")
    if not normalized:
        return None

    for tokens, concern in _CONCERN_RULES:
        if any(token in normalized for token in tokens):
            if confidence < concern.min_confidence:
                return None
            return concern

    if any(token in normalized for token in _BENIGN_TOKENS):
        return None
    return None


def _draft_metadata(
    concern: DetectionConcern,
    *,
    detection: VisionDetection,
    image_storage_key: str | None,
    model_version: str,
) -> dict:
    payload = {
        "draft_kind": "pest_scout_entry" if concern.kind == "pest_scout" else "health_eval",
        "unconfirmed": True,
        "severity": concern.severity,
        "species": concern.species,
        "detected_class": detection.class_name,
        "confidence": round(float(detection.confidence), 4),
        "bbox": detection.bbox.as_list(),
        "photo_storage_key": image_storage_key,
        "model_version": model_version,
        "phase": "vision_detection",
        "safe_action": False,
    }
    if concern.kind == "pest_scout":
        payload["pest_type"] = concern.pest_type
    return payload


async def propose_vision_drafts(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    grow_cycle_id: UUID | None,
    source: str,
    source_ref: str,
    image_storage_key: str | None,
    detections: tuple[VisionDetection, ...],
    model_version: str | None,
    actor_user_id: UUID | None = None,
) -> list[AgentAction]:
    """Create approval-gated draft actions for actionable detections.

    Returns the created :class:`AgentAction` records. When ``grow_cycle_id`` or
    ``model_version`` is missing, or no detection is actionable, returns an empty
    list. Never writes ``PestScoutEntry`` / ``HealthEval`` rows directly.
    """
    if grow_cycle_id is None or not model_version:
        return []

    recorded: list[AgentAction] = []
    for index, detection in enumerate(detections):
        concern = map_detection_to_concern(detection.class_name, float(detection.confidence))
        if concern is None:
            continue

        action_source = f"vision_{source}"
        title = f"Review {concern.species} detection ({float(detection.confidence):.0%})"
        action = await ai_service.create_agent_action(
            session,
            tenant_id=tenant_id,
            source=action_source,
            action_type=concern.action_type,
            title=title[:255],
            idempotency_key=ai_service.build_agent_action_idempotency_key(
                tenant_id=tenant_id,
                source=action_source,
                action_type=concern.action_type,
                grow_cycle_id=grow_cycle_id,
                conversation_id=None,
                dedupe_token=f"{source_ref}:{index}:{detection.class_name}:{model_version}",
            ),
            grow_cycle_id=grow_cycle_id,
            created_by_user_id=actor_user_id,
            risk_level=_risk_from_severity(concern.severity),
            requires_approval=True,
            auto_approved=False,
            summary=f"{concern.species} suspected from vision detection — confirm before acting.",
            metadata_json=_draft_metadata(
                concern,
                detection=detection,
                image_storage_key=image_storage_key,
                model_version=model_version,
            ),
            evidence_json={
                "detected_class": detection.class_name,
                "confidence": round(float(detection.confidence), 4),
                "source": source,
                "source_ref": source_ref,
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
            requested_by_user_id=actor_user_id,
            reason="Vision detection draft requires grower confirmation before any action",
        )
        recorded.append(action)

    return recorded
