"""AI domain service.

Holds the business operations for AI features: conversation persistence
(this file), diagnosis flow (added in 3.11b), and the core AI route
helpers (added in 3.11c).

Route handlers in ``app.ai.*_routes`` are HTTP-only and delegate to
this module.

Conventions match the project standard (PR #192 / #208-#220):

* First positional argument is always ``session: AsyncSession``.
* Functions return ORM models, dataclasses, or primitives; they never
  raise ``HTTPException`` — lookup misses return ``None`` and domain
  validation failures raise typed errors.
* Query-builder helpers (``*_query``) return ``Select`` for the route
  layer to paginate.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.models import Conversation, ConversationMessage

# ─────────────────────────────────────────────────────────────────────────────
# Conversations
# ─────────────────────────────────────────────────────────────────────────────


async def create_conversation(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    user_id: UUID,
    grow_cycle_id: UUID | None,
    title: str | None,
) -> Conversation:
    """Create a new AI conversation owned by ``user_id`` in ``tenant_id``."""
    conv = Conversation(
        tenant_id=tenant_id,
        user_id=user_id,
        grow_cycle_id=grow_cycle_id,
        title=title,
    )
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


def list_user_conversations_query(
    *,
    tenant_id: UUID,
    user_id: UUID,
    grow_cycle_id: UUID | None = None,
) -> Select:
    """Build the listing query (most-recently-updated first); route paginates."""
    q = (
        select(Conversation)
        .where(
            Conversation.tenant_id == tenant_id,
            Conversation.user_id == user_id,
        )
        .order_by(desc(Conversation.updated_at))
    )
    if grow_cycle_id is not None:
        q = q.where(Conversation.grow_cycle_id == grow_cycle_id)
    return q


async def get_conversation(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: UUID,
) -> Conversation | None:
    """Fetch a conversation only if it belongs to ``tenant_id``.

    Returns ``None`` for unknown ids and cross-tenant access alike —
    the route maps either to 404 so we don't leak existence.
    """
    conv = await session.get(Conversation, conversation_id)
    if conv is None or conv.tenant_id != tenant_id:
        return None
    return conv


async def get_conversation_with_messages(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    conversation_id: UUID,
) -> Conversation | None:
    """Same as :func:`get_conversation` but eager-loads ``messages``."""
    result = await session.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def update_conversation_title(
    session: AsyncSession,
    conv: Conversation,
    *,
    title: str,
) -> Conversation:
    conv.title = title
    await session.commit()
    await session.refresh(conv)
    return conv


async def delete_conversation(session: AsyncSession, conv: Conversation) -> None:
    await session.delete(conv)
    await session.commit()


def parse_optional_uuid(value: str | None) -> UUID | None:
    """Pure helper — convert a string/None to ``UUID``/None.

    Raises ``ValueError`` on malformed input; route layer maps to 422.
    Centralised so we don't have ``UUID(x) if x else None`` peppered
    through the route file.
    """
    if value is None or value == "":
        return None
    return UUID(value)


# Type re-export — keeps ``service.ConversationMessage`` and
# ``service.Conversation`` available to callers that want a single
# import surface for the AI domain.
__all__ = [
    "Conversation",
    "ConversationMessage",
    "create_conversation",
    "delete_conversation",
    "get_conversation",
    "get_conversation_with_messages",
    "list_user_conversations_query",
    "parse_optional_uuid",
    "update_conversation_title",
]


# ─────────────────────────────────────────────────────────────────────────────
# Diagnose — plant-photo health analysis
# ─────────────────────────────────────────────────────────────────────────────


from dataclasses import dataclass as _dc  # noqa: E402  (kept with section)

# Max accepted photo size for the /diagnose endpoint. 10 MiB matches the
# upstream multipart limit on our reverse proxy + the Pulse/Pulse Wifi
# camera firmware's max single-snap size.
MAX_DIAGNOSE_IMAGE_BYTES: int = 10 * 1024 * 1024

# Default-fallback values returned when the LLM response can't be parsed
# as JSON. Kept here so the route doesn't have to know the defaults.
DEFAULT_DIAGNOSIS_OVERALL_SEVERITY: str = "medium"
DEFAULT_DIAGNOSIS_OVERALL_SCORE: int = 50


# ---- Errors ----


class DiagnoseImageError(Exception):
    """Raised when the request's base64 image is malformed or too large.

    Route maps to HTTP 400.
    """


# ---- Image validation ----


def decode_diagnose_image(image_base64: str) -> bytes:
    """Decode the request's base64 image and enforce the size cap.

    Raises :class:`DiagnoseImageError` for malformed base64 or oversize
    payloads. The cap is documented in
    :data:`MAX_DIAGNOSE_IMAGE_BYTES`.
    """
    import base64 as _b64

    try:
        image_bytes = _b64.b64decode(image_base64)
    except Exception as exc:
        raise DiagnoseImageError("Invalid base64 image data") from exc

    if len(image_bytes) > MAX_DIAGNOSE_IMAGE_BYTES:
        raise DiagnoseImageError(f"Image exceeds {MAX_DIAGNOSE_IMAGE_BYTES // (1024 * 1024)}MB limit")
    return image_bytes


# ---- Prompt building ----


# The instruction block sent to the vision model. Pulled out here so the
# route layer doesn't carry production prompt text (and so tests can
# assert structural properties).
DIAGNOSIS_SYSTEM_PROMPT: str = """You are Tendril, an expert cannabis plant health diagnostic AI.
Analyze the provided photo and identify any health issues.

You MUST respond with valid JSON in this exact format:
{
  "issues": [
    {
      "treatment_id": "nitrogen_deficiency",
      "name": "Nitrogen Deficiency",
      "confidence": 0.85,
      "severity": "medium",
      "description": "Brief description of what you see that indicates this issue",
      "treatment": "Brief recommended treatment action"
    }
  ],
  "summary": "Brief 1-2 sentence summary of what you see",
  "recommended_actions": ["Action 1", "Action 2"],
  "overall_severity": "medium",
  "overall_score": 65,
  "grow_stage_assessment": "Early flower, week 2-3"
}

Valid treatment_ids: nitrogen_deficiency, phosphorus_deficiency, potassium_deficiency,
calcium_deficiency, magnesium_deficiency, iron_deficiency, spider_mites, fungus_gnats,
thrips, powdery_mildew, botrytis, root_rot, light_burn, heat_stress, overwatering, ph_lockout

Severity levels: low, medium, high, critical
Confidence: 0.0 to 1.0 (how sure you are of each diagnosis)
overall_score: 0-100 (100 = perfectly healthy, 0 = dead)

If the plant looks healthy, return:
{"issues": [], "summary": "Plant appears healthy", "recommended_actions": [],
"overall_severity": "low", "overall_score": 95, "grow_stage_assessment": "..."}

Important rules:
- Only identify issues you can actually SEE in the photo
- Be conservative with confidence scores — don't overclaim
- Consider the grow type and stage when making recommendations
- Multiple issues can co-exist (e.g., pH lockout causing calcium deficiency)
- Provide a brief description for each issue explaining what visual evidence you see
- Provide a one-line treatment recommendation for each issue
"""


def build_diagnosis_prompt(
    grow_type: str | None = None,
    current_stage: str | None = None,
    observations: str | None = None,
) -> str:
    """Compose the vision-model prompt with optional grow context.

    The base prompt enumerates valid treatment_ids and the required
    JSON schema. ``grow_type`` / ``current_stage`` / ``observations``
    each contribute an additional context line. The instruction line
    at the end always asks for the JSON diagnosis.
    """
    prompt = DIAGNOSIS_SYSTEM_PROMPT

    context_parts: list[str] = []
    if grow_type:
        context_parts.append(f"Grow method: {grow_type}")
    if current_stage:
        context_parts.append(f"Current stage: {current_stage}")
    if observations:
        context_parts.append(f"Grower observations: {observations}")

    if context_parts:
        prompt += "\n\nContext:\n" + "\n".join(context_parts)

    prompt += "\n\nAnalyze the photo and provide your diagnosis as JSON."
    return prompt


# ---- Response parsing ----


@_dc(frozen=True, slots=True)
class ParsedDiagnosisIssue:
    """One issue extracted from the LLM JSON response."""

    treatment_id: str
    name: str
    confidence: float
    severity: str
    description: str
    treatment: str


@_dc(frozen=True, slots=True)
class ParsedDiagnosis:
    """The shape the route layer receives after parsing the LLM output.

    ``issues`` is empty when the LLM returns ``"issues": []`` (healthy)
    or when JSON parsing failed (route falls back to a "could not be
    parsed" summary).
    """

    summary: str
    actions: list[str]
    overall_severity: str
    overall_score: int
    grow_stage_assessment: str | None
    issues: list[ParsedDiagnosisIssue]


def _strip_markdown_fence(raw: str) -> str:
    """Strip a leading/trailing ```…``` fence the LLM sometimes adds.

    Matches previous route behaviour exactly:
    * leading ``` (optionally followed by a language tag and newline)
      is stripped,
    * trailing ``` is stripped,
    * surrounding whitespace is removed.
    """
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Drop everything up to and including the first newline (which
        # eats any language hint like ``json``), or just the ``` itself
        # if there's no newline.
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def parse_diagnosis_response(raw_response: str) -> ParsedDiagnosis:
    """Parse the LLM's raw text into a :class:`ParsedDiagnosis`.

    Robust against the model emitting fenced code blocks. On any JSON
    error returns a fallback diagnosis with the first 500 chars of
    ``raw_response`` as the summary and the documented default
    severity/score — same behaviour as the previous route.
    """
    import json as _json

    try:
        cleaned = _strip_markdown_fence(raw_response)
        parsed = _json.loads(cleaned)

        issues: list[ParsedDiagnosisIssue] = []
        for issue_data in parsed.get("issues", []):
            issues.append(
                ParsedDiagnosisIssue(
                    treatment_id=issue_data.get("treatment_id", "unknown"),
                    name=issue_data.get("name", "Unknown Issue"),
                    confidence=min(1.0, max(0.0, float(issue_data.get("confidence", 0.5)))),
                    severity=issue_data.get("severity", "medium"),
                    description=issue_data.get("description", ""),
                    treatment=issue_data.get("treatment", ""),
                )
            )

        return ParsedDiagnosis(
            summary=parsed.get("summary", ""),
            actions=parsed.get("recommended_actions", []),
            overall_severity=parsed.get("overall_severity", DEFAULT_DIAGNOSIS_OVERALL_SEVERITY),
            overall_score=int(parsed.get("overall_score", DEFAULT_DIAGNOSIS_OVERALL_SCORE)),
            grow_stage_assessment=parsed.get("grow_stage_assessment"),
            issues=issues,
        )
    except (_json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Fallback: return whatever raw text we got as the summary so
        # the user sees *something* useful.
        summary = raw_response[:500] if raw_response else "Diagnosis could not be parsed"
        return ParsedDiagnosis(
            summary=summary,
            actions=[],
            overall_severity=DEFAULT_DIAGNOSIS_OVERALL_SEVERITY,
            overall_score=DEFAULT_DIAGNOSIS_OVERALL_SCORE,
            grow_stage_assessment=None,
            issues=[],
        )


# ---- Treatment DB lookups ----


def list_treatments_query(*, category: str | None = None):
    """Build the listing query for the treatment reference table.

    Returns a SQLAlchemy ``Select``. Route layer doesn't paginate this
    one because the treatment library is small and the frontend uses
    the full list for autocomplete.
    """
    from sqlalchemy import select as _select

    from app.grows.models import PlantHealthTreatment

    q = _select(PlantHealthTreatment)
    if category:
        q = q.where(PlantHealthTreatment.category == category)
    return q.order_by(PlantHealthTreatment.category, PlantHealthTreatment.name)


def search_treatments_query(*, query_text: str):
    """Build the search query — case-insensitive ILIKE across name +
    summary + category. Returns a SQLAlchemy ``Select``.
    """
    from sqlalchemy import or_ as _or
    from sqlalchemy import select as _select

    from app.grows.models import PlantHealthTreatment

    search_term = f"%{query_text.lower()}%"
    return _select(PlantHealthTreatment).where(
        _or(
            PlantHealthTreatment.name.ilike(search_term),
            PlantHealthTreatment.summary.ilike(search_term),
            PlantHealthTreatment.category.ilike(search_term),
        )
    )


async def get_treatment(session: AsyncSession, treatment_id: str):
    """Fetch a treatment by id (str — treatments use string primary keys)."""
    from app.grows.models import PlantHealthTreatment

    return await session.get(PlantHealthTreatment, treatment_id)
