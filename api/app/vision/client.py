from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import get_settings
from app.vision.contracts import AcceleratorTier, BoundingBox, VisionDetection, VisionProfile
from app.vision.service import DetectionResponse, build_unavailable_response


@dataclass(frozen=True, slots=True)
class VisionDetectorClient:
    base_url: str
    gpu_fallback_url: str = ""
    timeout_seconds: float = 15.0

    @classmethod
    def from_settings(cls) -> VisionDetectorClient:
        settings = get_settings()
        return cls(
            base_url=settings.vision_detector_base_url,
            gpu_fallback_url=settings.vision_detector_gpu_fallback_url,
            timeout_seconds=settings.vision_detector_timeout_seconds,
        )

    async def _scan_image_at_url(
        self,
        *,
        target_base_url: str,
        image_base64: str,
        profile: VisionProfile,
        source: str,
        source_ref: str,
    ) -> DetectionResponse:
        payload = {
            "image_base64": image_base64,
            "profile": profile.value,
            "source": source,
            "source_ref": source_ref,
        }
        timeout = httpx.Timeout(self.timeout_seconds)

        try:
            async with httpx.AsyncClient(timeout=timeout, base_url=target_base_url) as client:
                response = await client.post("/detect", json=payload)
                response.raise_for_status()
        except (httpx.HTTPError, ValueError):
            return build_unavailable_response()

        data = response.json()
        model_version = data.get("model_version")
        if not model_version:
            return build_unavailable_response(data.get("message", "detection unavailable"))

        accelerator_tier = AcceleratorTier(data.get("accelerator_tier", AcceleratorTier.UNAVAILABLE))
        detections = tuple(
            VisionDetection(
                class_name=item["class"],
                confidence=float(item["confidence"]),
                bbox=BoundingBox(
                    x=float(item["bbox"][0]),
                    y=float(item["bbox"][1]),
                    width=float(item["bbox"][2]),
                    height=float(item["bbox"][3]),
                ),
            )
            for item in data.get("detections", [])
        )

        return DetectionResponse(
            model_version=str(model_version),
            accelerator_tier=accelerator_tier,
            detections=detections,
            message=data.get("message"),
        )

    async def scan_image(
        self,
        *,
        image_base64: str,
        profile: VisionProfile,
        source: str,
        source_ref: str,
    ) -> DetectionResponse:
        primary_response = await self._scan_image_at_url(
            target_base_url=self.base_url,
            image_base64=image_base64,
            profile=profile,
            source=source,
            source_ref=source_ref,
        )

        if primary_response.model_version is not None:
            return primary_response

        fallback_url = self.gpu_fallback_url.strip()
        if not fallback_url or fallback_url == self.base_url:
            return primary_response

        return await self._scan_image_at_url(
            target_base_url=fallback_url,
            image_base64=image_base64,
            profile=profile,
            source=source,
            source_ref=source_ref,
        )

    async def healthz(self) -> dict[str, str]:
        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, base_url=self.base_url) as client:
            response = await client.get("/healthz")
            response.raise_for_status()
            return response.json()
