from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AcceleratorTier(StrEnum):
    CORAL = "coral"
    GPU = "gpu"
    CPU = "cpu"
    UNAVAILABLE = "unavailable"


class VisionProfile(StrEnum):
    TENT_OVERVIEW = "tent_overview"
    PHOTO_SCAN = "photo_scan"
    TRICHOME_MACRO = "trichome_macro"
    CONTINUOUS_SCAN = "continuous_scan"


@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    def as_list(self) -> list[float]:
        return [self.x, self.y, self.width, self.height]


@dataclass(frozen=True, slots=True)
class VisionDetection:
    class_name: str
    confidence: float
    bbox: BoundingBox

    def as_payload(self) -> dict[str, Any]:
        return {
            "class": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox.as_list(),
        }


@dataclass(frozen=True, slots=True)
class VisionModelMetadata:
    version: str
    input_size: tuple[int, int]
    classes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RuntimeAvailability:
    coral: bool = False
    gpu: bool = False
    cpu: bool = True
