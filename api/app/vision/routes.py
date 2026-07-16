from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.middleware import CurrentUser, require_permission
from app.auth.permissions import PHOTO_READ
from app.vision.client import VisionDetectorClient
from app.vision.contracts import VisionProfile

router = APIRouter()


class VisionScanRequest(BaseModel):
    image_base64: str
    profile: VisionProfile = VisionProfile.TENT_OVERVIEW
    source: str
    source_ref: str


class VisionDetectionBoxResponse(BaseModel):
    class_name: str
    confidence: float
    bbox: list[float]


class VisionScanResponse(BaseModel):
    model_version: str | None
    accelerator_tier: str
    detections: list[VisionDetectionBoxResponse]
    message: str | None = None


def get_vision_detector_client() -> VisionDetectorClient:
    return VisionDetectorClient.from_settings()


@router.post("/scan", response_model=VisionScanResponse)
async def scan_image(
    payload: VisionScanRequest,
    _user: Annotated[CurrentUser, Depends(require_permission(PHOTO_READ))],
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> VisionScanResponse:
    response = await client.scan_image(
        image_base64=payload.image_base64,
        profile=payload.profile,
        source=payload.source,
        source_ref=payload.source_ref,
    )
    return VisionScanResponse(
        model_version=response.model_version,
        accelerator_tier=response.accelerator_tier.value,
        detections=[
            VisionDetectionBoxResponse(
                class_name=item.class_name,
                confidence=item.confidence,
                bbox=item.bbox.as_list(),
            )
            for item in response.detections
        ],
        message=response.message,
    )


@router.get("/healthz")
async def vision_healthz(
    client: Annotated[VisionDetectorClient, Depends(get_vision_detector_client)],
) -> dict[str, Any]:
    return await client.healthz()
