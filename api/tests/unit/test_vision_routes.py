from __future__ import annotations

import os
from uuid import UUID

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET", "test-secret")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.middleware import CurrentUser, get_current_user
from app.tenants.models import TenantRole
from app.vision.contracts import AcceleratorTier, BoundingBox, VisionDetection
from app.vision.routes import get_vision_detector_client, router
from app.vision.service import DetectionResponse


class FakeClient:
    async def scan_image(self, **_: object) -> DetectionResponse:
        return DetectionResponse(
            model_version="v1",
            accelerator_tier=AcceleratorTier.CORAL,
            detections=(VisionDetection(class_name="pest", confidence=0.8, bbox=BoundingBox(0.1, 0.2, 0.3, 0.4)),),
        )

    async def healthz(self) -> dict[str, str]:
        return {"status": "ok"}


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/v1/vision")
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(
        user_id=UUID("00000000-0000-0000-0000-000000000001"),
        tenant_id=UUID("00000000-0000-0000-0000-000000000002"),
        tenant_role=TenantRole.viewer,
    )
    app.dependency_overrides[get_vision_detector_client] = lambda: FakeClient()
    return app


def test_scan_route_returns_detection_payload() -> None:
    app = _build_app()
    client = TestClient(app)

    response = client.post(
        "/v1/vision/scan",
        json={
            "image_base64": "ZmFrZQ==",
            "profile": "tent_overview",
            "source": "tent",
            "source_ref": "tent-123",
        },
    )

    assert response.status_code == 200
    assert response.json()["model_version"] == "v1"
    assert response.json()["accelerator_tier"] == "coral"
    assert response.json()["detections"][0]["class_name"] == "pest"
