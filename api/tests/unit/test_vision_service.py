from __future__ import annotations

from app.vision.contracts import AcceleratorTier, BoundingBox, RuntimeAvailability, VisionDetection, VisionModelMetadata
from app.vision.service import build_detection_response, build_unavailable_response, select_accelerator_tier


def test_select_accelerator_prefers_coral_then_gpu_then_cpu() -> None:
    assert select_accelerator_tier(RuntimeAvailability(coral=True, gpu=True, cpu=True)) is AcceleratorTier.CORAL
    assert select_accelerator_tier(RuntimeAvailability(coral=False, gpu=True, cpu=True)) is AcceleratorTier.GPU
    assert select_accelerator_tier(RuntimeAvailability(coral=False, gpu=False, cpu=True)) is AcceleratorTier.CPU


def test_select_accelerator_returns_unavailable_when_no_runtime_exists() -> None:
    assert (
        select_accelerator_tier(RuntimeAvailability(coral=False, gpu=False, cpu=False)) is AcceleratorTier.UNAVAILABLE
    )


def test_build_unavailable_response_is_graceful() -> None:
    response = build_unavailable_response()

    assert response.model_version is None
    assert response.accelerator_tier is AcceleratorTier.UNAVAILABLE
    assert response.detections == ()
    assert response.message == "detection unavailable"


def test_build_detection_response_preserves_metadata_and_payload() -> None:
    metadata = VisionModelMetadata(version="v1.2.3", input_size=(640, 640), classes=("pest", "bud"))
    detection = VisionDetection(
        class_name="pest",
        confidence=0.91,
        bbox=BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4),
    )

    response = build_detection_response(
        metadata=metadata,
        availability=RuntimeAvailability(coral=False, gpu=True, cpu=True),
        detections=(detection,),
    )

    assert response.model_version == "v1.2.3"
    assert response.accelerator_tier is AcceleratorTier.GPU
    assert response.detections == (detection,)
    assert response.detections[0].as_payload() == {
        "class": "pest",
        "confidence": 0.91,
        "bbox": [0.1, 0.2, 0.3, 0.4],
    }
