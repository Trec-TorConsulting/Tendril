"""AI Plant Diagnosis routes — photo-based plant health analysis.

POST /v1/ai/diagnose — Upload a photo, get AI diagnosis with treatment links.
GET /v1/ai/treatments — List all treatment entries (reference data).
GET /v1/ai/treatments/{treatment_id} — Get a specific treatment entry.
GET /v1/ai/treatments/search — Search treatments by query.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.billing.metering import record_usage
from app.billing.tier_gate import require_usage_limit
from app.config import get_settings

logger = logging.getLogger("tendril.ai.diagnose")
router = APIRouter()


# ---------- Schemas ----------


class DiagnoseRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded JPEG/PNG image of the plant")
    grow_id: str | None = Field(None, description="Optional grow cycle ID for context-aware diagnosis")
    grow_type: str | None = Field(None, description="e.g., dwc, soil, coco — used for treatment filtering")
    current_stage: str | None = Field(None, description="e.g., vegetative, flowering")
    observations: str | None = Field(None, description="User's text observations about the issue")


class DiagnosisIssue(BaseModel):
    treatment_id: str
    name: str
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str  # low | medium | high | critical
    description: str = ""
    treatment: str = ""


class DiagnoseResponse(BaseModel):
    overall_score: int
    summary: str
    issues: list[DiagnosisIssue]
    actions: list[str]
    grow_stage_assessment: str | None = None
    model_used: str
    health_eval_id: str | None = None


class TreatmentResponse(BaseModel):
    id: str
    category: str
    name: str
    aka: list[str]
    summary: str
    symptoms: list[str]
    identification_tips: list[str]
    causes: list[str]
    severity_criteria: dict[str, str]
    treatments: dict[str, list[str]]
    prevention: list[str]
    recovery_time: str
    commonly_confused_with: list[str]


class TreatmentListResponse(BaseModel):
    items: list[TreatmentResponse]
    total: int


# ---------- Diagnosis Prompt ----------

DIAGNOSIS_SYSTEM_PROMPT = """You are Tendril, an expert cannabis plant health diagnostic AI.
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


def _build_diagnosis_prompt(
    grow_type: str | None = None,
    current_stage: str | None = None,
    observations: str | None = None,
) -> str:
    """Build a contextual diagnosis prompt."""
    prompt = DIAGNOSIS_SYSTEM_PROMPT

    context_parts = []
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


# ---------- Diagnose Endpoint ----------


@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    dependencies=[Depends(require_usage_limit("ai_analyses"))],
)
async def diagnose_plant(
    body: DiagnoseRequest,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Analyze a plant photo using AI vision (Ollama first, Gemini fallback).

    Returns identified issues linked to the treatment database with confidence scores.
    """
    from app.grows.models import GrowCycle, GrowPhoto, HealthEval
    from app.storage import upload_photo as s3_upload

    # Validate image
    try:
        image_bytes = base64.b64decode(body.image_base64)
    except Exception as err:
        raise HTTPException(status_code=400, detail="Invalid base64 image data") from err

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds 10MB limit")

    # Get grow context if provided
    grow = None
    grow_type = body.grow_type
    current_stage = body.current_stage
    if body.grow_id:
        grow = await session.get(GrowCycle, UUID(body.grow_id))
        if grow:
            grow_type = grow_type or grow.grow_type
            current_stage = current_stage or grow.current_stage

    # Build prompt
    prompt = _build_diagnosis_prompt(grow_type, current_stage, body.observations)

    # Try Ollama vision first, fall back to Gemini
    raw_response = ""
    model_used = ""

    try:
        from app.ai.ollama import vision_diagnose

        raw_response = await vision_diagnose(body.image_base64, prompt)
        settings = get_settings()
        model_used = f"ollama:{settings.ollama_vision_model}"
        logger.info("Diagnosis completed via Ollama vision")
    except Exception as ollama_err:
        logger.warning("Ollama vision failed, falling back to Gemini: %s", ollama_err)

        # Gemini fallback
        try:
            from app.ai.gemini import chat_completion as gemini_chat
            from app.ai.gemini import is_configured as gemini_configured

            if not gemini_configured():
                raise HTTPException(
                    status_code=503,
                    detail="AI vision service unavailable (Ollama failed, Gemini not configured)",
                )

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Analyze this plant photo for health issues."},
            ]
            raw_response = await gemini_chat(messages, image_bytes=image_bytes)
            settings = get_settings()
            model_used = f"gemini:{settings.gemini_model}"
            logger.info("Diagnosis completed via Gemini fallback")
        except HTTPException:
            raise
        except Exception as gemini_err:
            logger.exception("Both Ollama and Gemini vision failed")
            raise HTTPException(
                status_code=503,
                detail="AI vision service unavailable",
            ) from gemini_err

    # Parse response
    issues: list[DiagnosisIssue] = []
    summary = ""
    actions: list[str] = []
    overall_severity = "low"
    overall_score = 50
    grow_stage_assessment: str | None = None

    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        parsed = json.loads(cleaned)

        summary = parsed.get("summary", "")
        actions = parsed.get("recommended_actions", [])
        overall_severity = parsed.get("overall_severity", "low")
        overall_score = int(parsed.get("overall_score", 50))
        grow_stage_assessment = parsed.get("grow_stage_assessment")

        for issue_data in parsed.get("issues", []):
            issues.append(
                DiagnosisIssue(
                    treatment_id=issue_data.get("treatment_id", "unknown"),
                    name=issue_data.get("name", "Unknown Issue"),
                    confidence=min(1.0, max(0.0, float(issue_data.get("confidence", 0.5)))),
                    severity=issue_data.get("severity", "medium"),
                    description=issue_data.get("description", ""),
                    treatment=issue_data.get("treatment", ""),
                )
            )
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse diagnosis JSON: %s — raw: %s", e, raw_response[:300])
        # Return raw analysis as summary if JSON parsing fails
        summary = raw_response[:500] if raw_response else "Diagnosis could not be parsed"
        overall_severity = "medium"
        overall_score = 50

    # Store photo in MinIO
    photo_key = None
    if grow:
        try:
            loop = asyncio.get_running_loop()
            photo_key = await loop.run_in_executor(
                None,
                s3_upload,
                image_bytes,
                "image/jpeg",
                str(grow.tenant_id),
                str(grow.id),
            )
            grow_photo = GrowPhoto(
                tenant_id=grow.tenant_id,
                grow_cycle_id=grow.id,
                source="diagnose",
                storage_key=photo_key,
                caption=f"AI Diagnosis: {summary[:100]}" if summary else "AI Diagnosis photo",
            )
            session.add(grow_photo)
        except Exception:
            logger.exception("Failed to upload diagnosis photo to S3")

    # Store HealthEval with treatment links
    health_eval = HealthEval(
        tenant_id=user.tenant_id,
        grow_cycle_id=grow.id if grow else UUID("00000000-0000-0000-0000-000000000000"),
        score=overall_score,
        issues=[i.name for i in issues],
        actions=actions,
        raw_analysis=raw_response,
        source="diagnose",
        diagnosis_treatment_ids=[i.treatment_id for i in issues],
        confidence_scores={i.treatment_id: i.confidence for i in issues},
        severity=overall_severity,
        model_used=model_used,
    )
    session.add(health_eval)
    await session.commit()
    await session.refresh(health_eval)

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    return DiagnoseResponse(
        overall_score=overall_score,
        summary=summary,
        issues=issues,
        actions=actions,
        grow_stage_assessment=grow_stage_assessment,
        model_used=model_used,
        health_eval_id=str(health_eval.id),
    )


# ---------- Treatment Endpoints ----------


@router.get("/treatments", response_model=TreatmentListResponse)
async def list_treatments(
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    category: str | None = Query(None, description="Filter by category: deficiency, pest, disease, environmental"),
):
    """List all plant health treatment entries."""
    from app.grows.models import PlantHealthTreatment

    query = select(PlantHealthTreatment)
    if category:
        query = query.where(PlantHealthTreatment.category == category)
    query = query.order_by(PlantHealthTreatment.category, PlantHealthTreatment.name)

    result = await session.execute(query)
    treatments = result.scalars().all()

    return TreatmentListResponse(
        items=[_treatment_to_response(t) for t in treatments],
        total=len(treatments),
    )


@router.get("/treatments/search", response_model=TreatmentListResponse)
async def search_treatments(
    q: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Search treatments by name, symptoms, or alternate names."""
    from sqlalchemy import or_

    from app.grows.models import PlantHealthTreatment

    search_term = f"%{q.lower()}%"
    query = select(PlantHealthTreatment).where(
        or_(
            PlantHealthTreatment.name.ilike(search_term),
            PlantHealthTreatment.summary.ilike(search_term),
            PlantHealthTreatment.category.ilike(search_term),
        )
    )
    result = await session.execute(query)
    treatments = result.scalars().all()

    return TreatmentListResponse(
        items=[_treatment_to_response(t) for t in treatments],
        total=len(treatments),
    )


@router.get("/treatments/{treatment_id}", response_model=TreatmentResponse)
async def get_treatment(
    treatment_id: str,
    user: Annotated[CurrentUser, Depends(require_role("owner", "member"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
):
    """Get a specific treatment entry by ID."""
    from app.grows.models import PlantHealthTreatment

    treatment = await session.get(PlantHealthTreatment, treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return _treatment_to_response(treatment)


def _treatment_to_response(t) -> TreatmentResponse:
    """Convert a PlantHealthTreatment model to response schema."""
    return TreatmentResponse(
        id=t.id,
        category=t.category,
        name=t.name,
        aka=t.aka or [],
        summary=t.summary,
        symptoms=t.symptoms or [],
        identification_tips=t.identification_tips or [],
        causes=t.causes or [],
        severity_criteria=t.severity_criteria or {},
        treatments=t.treatments or {},
        prevention=t.prevention or [],
        recovery_time=t.recovery_time or "",
        commonly_confused_with=t.commonly_confused_with or [],
    )
