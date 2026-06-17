"""AI Plant Diagnosis routes — photo-based plant health analysis.

POST /v1/ai/diagnose — Upload a photo, get AI diagnosis with treatment links.
GET /v1/ai/treatments — List all treatment entries (reference data).
GET /v1/ai/treatments/{treatment_id} — Get a specific treatment entry.
GET /v1/ai/treatments/search — Search treatments by query.

This module is HTTP-only. Image validation, prompt building, and LLM
response parsing live in ``app.ai.service``. The Ollama→Gemini
fallback orchestration stays here (HTTP-flow + service unavailability
mapping).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai import service
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

    # Validate image (raises 400 on malformed base64 or oversize payload).
    try:
        image_bytes = service.decode_diagnose_image(body.image_base64)
    except service.DiagnoseImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Get grow context if provided
    grow = None
    grow_type = body.grow_type
    current_stage = body.current_stage
    if body.grow_id:
        grow = await session.get(GrowCycle, UUID(body.grow_id))
        if grow:
            grow_type = grow_type or grow.grow_type
            current_stage = current_stage or grow.current_stage

    prompt = service.build_diagnosis_prompt(grow_type, current_stage, body.observations)

    # Try Ollama vision first, fall back to Gemini. The fallback /
    # 503-mapping orchestration stays in the route — it's HTTP-flow.
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

    # Parse LLM response into a structured ParsedDiagnosis.
    parsed = service.parse_diagnosis_response(raw_response)

    issues = [
        DiagnosisIssue(
            treatment_id=i.treatment_id,
            name=i.name,
            confidence=i.confidence,
            severity=i.severity,
            description=i.description,
            treatment=i.treatment,
        )
        for i in parsed.issues
    ]

    # Store photo in MinIO when we have a grow context
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
                caption=f"AI Diagnosis: {parsed.summary[:100]}" if parsed.summary else "AI Diagnosis photo",
            )
            session.add(grow_photo)
        except Exception:
            logger.exception("Failed to upload diagnosis photo to S3")

    # Store HealthEval with treatment links
    health_eval = HealthEval(
        tenant_id=user.tenant_id,
        grow_cycle_id=grow.id if grow else UUID("00000000-0000-0000-0000-000000000000"),
        score=parsed.overall_score,
        issues=[i.name for i in issues],
        actions=parsed.actions,
        raw_analysis=raw_response,
        source="diagnose",
        diagnosis_treatment_ids=[i.treatment_id for i in issues],
        confidence_scores={i.treatment_id: i.confidence for i in issues},
        severity=parsed.overall_severity,
        model_used=model_used,
    )
    session.add(health_eval)
    await session.commit()
    await session.refresh(health_eval)

    await record_usage(session, user.tenant_id, "ai_analyses")
    await session.commit()

    return DiagnoseResponse(
        overall_score=parsed.overall_score,
        summary=parsed.summary,
        issues=issues,
        actions=parsed.actions,
        grow_stage_assessment=parsed.grow_stage_assessment,
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
    result = await session.execute(service.list_treatments_query(category=category))
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
    result = await session.execute(service.search_treatments_query(query_text=q))
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
    treatment = await service.get_treatment(session, treatment_id)
    if treatment is None:
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
