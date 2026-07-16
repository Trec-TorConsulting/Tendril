from __future__ import annotations

from dataclasses import dataclass

from app.vision.contracts import AcceleratorTier, RuntimeAvailability, VisionDetection, VisionModelMetadata


@dataclass(frozen=True, slots=True)
class DetectionResponse:
    model_version: str | None
    accelerator_tier: AcceleratorTier
    detections: tuple[VisionDetection, ...]
    message: str | None = None


def select_accelerator_tier(availability: RuntimeAvailability) -> AcceleratorTier:
    if availability.coral:
        return AcceleratorTier.CORAL
    if availability.gpu:
        return AcceleratorTier.GPU
    if availability.cpu:
        return AcceleratorTier.CPU
    return AcceleratorTier.UNAVAILABLE


def build_unavailable_response(message: str = "detection unavailable") -> DetectionResponse:
    return DetectionResponse(
        model_version=None,
        accelerator_tier=AcceleratorTier.UNAVAILABLE,
        detections=(),
        message=message,
    )


def build_detection_response(
    *,
    metadata: VisionModelMetadata,
    availability: RuntimeAvailability,
    detections: tuple[VisionDetection, ...],
) -> DetectionResponse:
    return DetectionResponse(
        model_version=metadata.version,
        accelerator_tier=select_accelerator_tier(availability),
        detections=detections,
    )
