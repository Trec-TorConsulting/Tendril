from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.inference import DetectorError, run_detection
from app.runtime import AcceleratorTier, build_runtime_state, load_runtime_config

logger = logging.getLogger("tendril.vision.detector")

app = FastAPI(title="Tendril Vision Detector", version="0.1.0")


class DetectRequest(BaseModel):
    image_base64: str
    profile: str
    source: str
    source_ref: str


class DetectionBox(BaseModel):
    class_name: str = Field(serialization_alias="class", validation_alias="class")
    confidence: float
    bbox: list[float]


class DetectResponse(BaseModel):
    model_version: str | None
    accelerator_tier: str
    detections: list[DetectionBox]
    message: str | None = None


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    config = load_runtime_config()
    state = build_runtime_state(config)
    return {
        "status": "ok",
        "model_version": state.model_version,
        "accelerator_tier": state.accelerator_tier.value,
    }


@app.post("/detect", response_model=DetectResponse)
async def detect(payload: DetectRequest) -> DetectResponse:
    config = load_runtime_config()
    state = build_runtime_state(config)

    if state.model_version is None:
        return DetectResponse(
            model_version=None,
            accelerator_tier=AcceleratorTier.UNAVAILABLE.value,
            detections=[],
            message="detection unavailable",
        )

    logger.info(
        "Running detection: profile=%s source=%s source_ref=%s bytes=%d tier=%s",
        payload.profile,
        payload.source,
        payload.source_ref,
        len(payload.image_base64),
        state.accelerator_tier.value,
    )

    try:
        detections = run_detection(payload.image_base64)
    except DetectorError as exc:
        logger.warning("Detector error: %s", exc)
        return DetectResponse(
            model_version=state.model_version,
            accelerator_tier=state.accelerator_tier.value,
            detections=[],
            message=str(exc),
        )
    except Exception:
        logger.exception("Unexpected detector failure")
        return DetectResponse(
            model_version=state.model_version,
            accelerator_tier=state.accelerator_tier.value,
            detections=[],
            message="detector execution failed",
        )

    return DetectResponse(
        model_version=state.model_version,
        accelerator_tier=state.accelerator_tier.value,
        detections=[
            DetectionBox(class_name=item.class_name, confidence=item.confidence, bbox=item.bbox)
            for item in detections
        ],
        message=None,
    )
