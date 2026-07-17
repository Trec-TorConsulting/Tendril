from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import func, select

from app.ai import service
from app.ai.models import AgentAction, AgentActionApproval
from app.grows.models import GrowCycle, HealthEval, PestScoutEntry, Tent
from app.vision.contracts import BoundingBox, VisionDetection
from app.vision.drafts import (
    HEALTH_EVAL_ACTION,
    PEST_SCOUT_ACTION,
    map_detection_to_concern,
    propose_vision_drafts,
)
from tests.conftest import TenantFactory


def _detection(class_name: str, confidence: float) -> VisionDetection:
    return VisionDetection(
        class_name=class_name,
        confidence=confidence,
        bbox=BoundingBox(x=0.1, y=0.1, width=0.2, height=0.2),
    )


@pytest_asyncio.fixture
async def tenant(db_session):
    return await TenantFactory(db_session).create()


@pytest_asyncio.fixture
async def grow(db_session, tenant):
    tent = Tent(tenant_id=tenant["tenant"].id, name="Vision Tent")
    db_session.add(tent)
    await db_session.flush()
    cycle = GrowCycle(
        tenant_id=tenant["tenant"].id,
        tent_id=tent.id,
        name="Vision Grow",
        grow_type="dwc",
        stage="flowering",
    )
    db_session.add(cycle)
    await db_session.commit()
    await db_session.refresh(cycle)
    return cycle


class TestDetectionMapping:
    def test_mildew_is_critical_disease(self) -> None:
        concern = map_detection_to_concern("powdery_mildew", 0.9)
        assert concern is not None
        assert concern.kind == "pest_scout"
        assert concern.action_type == PEST_SCOUT_ACTION
        assert concern.pest_type == "disease"
        assert concern.severity == "critical"

    def test_mite_is_high_insect(self) -> None:
        concern = map_detection_to_concern("spider_mites", 0.8)
        assert concern is not None
        assert concern.pest_type == "insect"
        assert concern.severity == "high"

    def test_deficiency_maps_to_health_eval(self) -> None:
        concern = map_detection_to_concern("nutrient_deficiency", 0.7)
        assert concern is not None
        assert concern.kind == "health_eval"
        assert concern.action_type == HEALTH_EVAL_ACTION

    def test_benign_class_returns_none(self) -> None:
        assert map_detection_to_concern("bud", 0.99) is None
        assert map_detection_to_concern("trichome_cloudy", 0.99) is None

    def test_low_confidence_returns_none(self) -> None:
        assert map_detection_to_concern("powdery_mildew", 0.2) is None


@pytest.mark.asyncio(loop_scope="session")
class TestProposeVisionDrafts:
    async def test_creates_approval_gated_actions_without_mutating_grow_state(self, db_session, tenant, grow) -> None:
        detections = (
            _detection("powdery_mildew", 0.92),
            _detection("nutrient_deficiency", 0.75),
            _detection("bud", 0.99),  # benign — skipped
            _detection("spider_mites", 0.3),  # below threshold — skipped
        )

        actions = await propose_vision_drafts(
            db_session,
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=grow.id,
            source="tent",
            source_ref=str(grow.tent_id),
            image_storage_key="photos/example.jpg",
            detections=detections,
            model_version="v1",
            actor_user_id=tenant["user"].id,
        )

        assert len(actions) == 2
        action_types = {a.action_type for a in actions}
        assert action_types == {PEST_SCOUT_ACTION, HEALTH_EVAL_ACTION}
        for action in actions:
            assert action.requires_approval is True
            assert action.auto_approved is False
            assert action.status == service.AGENT_ACTION_STATUS_PENDING_APPROVAL
            assert action.metadata_json["unconfirmed"] is True

        approvals = (
            await db_session.execute(
                select(func.count())
                .select_from(AgentActionApproval)
                .where(AgentActionApproval.tenant_id == tenant["tenant"].id)
            )
        ).scalar_one()
        assert approvals == 2

        # No-auto-mutation guarantee: no grow-state rows were written.
        pest_rows = (
            await db_session.execute(select(func.count()).select_from(PestScoutEntry))
        ).scalar_one()
        eval_rows = (await db_session.execute(select(func.count()).select_from(HealthEval))).scalar_one()
        assert pest_rows == 0
        assert eval_rows == 0

    async def test_no_actions_without_grow_cycle(self, db_session, tenant) -> None:
        actions = await propose_vision_drafts(
            db_session,
            tenant_id=tenant["tenant"].id,
            grow_cycle_id=None,
            source="photo",
            source_ref="x",
            image_storage_key=None,
            detections=(_detection("powdery_mildew", 0.92),),
            model_version="v1",
        )
        assert actions == []
        count = (await db_session.execute(select(func.count()).select_from(AgentAction))).scalar_one()
        assert count == 0
