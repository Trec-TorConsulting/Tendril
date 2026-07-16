from __future__ import annotations

import httpx
import pytest

from app.vision.client import VisionDetectorClient
from app.vision.contracts import AcceleratorTier, VisionProfile


@pytest.mark.asyncio
async def test_scan_image_parses_detection_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/detect"
        assert request.headers["content-type"].startswith("application/json")
        return httpx.Response(
            200,
            json={
                "model_version": "v2.0.0",
                "accelerator_tier": "coral",
                "detections": [
                    {"class": "pest", "confidence": 0.9, "bbox": [0.1, 0.2, 0.3, 0.4]},
                ],
            },
        )

    client = VisionDetectorClient(base_url="http://vision-detector.test", timeout_seconds=1)
    transport = httpx.MockTransport(handler)

    original_client = httpx.AsyncClient

    def fake_async_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    response = await client.scan_image(
        image_base64="ZmFrZQ==",
        profile=VisionProfile.TENT_OVERVIEW,
        source="tent",
        source_ref="tent-123",
    )

    assert response.model_version == "v2.0.0"
    assert response.accelerator_tier is AcceleratorTier.CORAL
    assert response.detections[0].class_name == "pest"
    assert response.detections[0].as_payload() == {
        "class": "pest",
        "confidence": 0.9,
        "bbox": [0.1, 0.2, 0.3, 0.4],
    }


@pytest.mark.asyncio
async def test_scan_image_returns_unavailable_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"detail": "down"})

    client = VisionDetectorClient(base_url="http://vision-detector.test", timeout_seconds=1)
    transport = httpx.MockTransport(handler)

    original_client = httpx.AsyncClient

    def fake_async_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    response = await client.scan_image(
        image_base64="ZmFrZQ==",
        profile=VisionProfile.PHOTO_SCAN,
        source="photo",
        source_ref="photo-1",
    )

    assert response.model_version is None
    assert response.accelerator_tier is AcceleratorTier.UNAVAILABLE
    assert response.detections == ()


@pytest.mark.asyncio
async def test_scan_image_uses_gpu_fallback_when_primary_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    call_counts: dict[str, int] = {"primary": 0, "fallback": 0}

    async def handler(request: httpx.Request) -> httpx.Response:
        if "vision-detector-primary" in str(request.url):
            call_counts["primary"] += 1
            return httpx.Response(503, json={"detail": "primary down"})
        call_counts["fallback"] += 1
        return httpx.Response(
            200,
            json={
                "model_version": "gpu-v1",
                "accelerator_tier": "gpu",
                "detections": [],
            },
        )

    client = VisionDetectorClient(
        base_url="http://vision-detector-primary.test",
        gpu_fallback_url="http://vision-detector-fallback.test",
        timeout_seconds=1,
    )
    transport = httpx.MockTransport(handler)

    original_client = httpx.AsyncClient

    def fake_async_client(*args, **kwargs):
        kwargs["transport"] = transport
        return original_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_async_client)

    response = await client.scan_image(
        image_base64="ZmFrZQ==",
        profile=VisionProfile.PHOTO_SCAN,
        source="photo",
        source_ref="photo-2",
    )

    assert call_counts["primary"] == 1
    assert call_counts["fallback"] == 1
    assert response.model_version == "gpu-v1"
    assert response.accelerator_tier is AcceleratorTier.GPU
