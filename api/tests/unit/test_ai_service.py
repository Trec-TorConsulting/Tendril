"""Unit tests for app.ai.service pure helpers."""

from __future__ import annotations

import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest

from app.ai.service import (
    AGENT_ACTION_STATUS_APPROVED,
    AGENT_ACTION_STATUS_COMPLETED,
    AGENT_ACTION_STATUS_EXECUTING,
    AGENT_ACTION_STATUS_PENDING_APPROVAL,
    AGENT_ACTION_STATUS_PROPOSED,
    AGENT_ACTION_STATUS_VERIFIED,
    AGENT_APPROVAL_STATUS_APPROVED,
    AGENT_APPROVAL_STATUS_PENDING,
    AGENT_APPROVAL_STATUS_REJECTED,
    DEFAULT_DIAGNOSIS_OVERALL_SCORE,
    DEFAULT_DIAGNOSIS_OVERALL_SEVERITY,
    DIAGNOSIS_SYSTEM_PROMPT,
    HEALTH_HISTORY_MAX_LIMIT,
    MAX_DIAGNOSE_IMAGE_BYTES,
    AgentAction,
    AgentActionApproval,
    Conversation,
    DiagnoseImageError,
    InvalidAgentActionTransitionError,
    InvalidAgentApprovalTransitionError,
    build_agent_action_idempotency_key,
    build_diagnosis_prompt,
    build_photo_url_base,
    can_transition_agent_action,
    create_agent_action,
    create_agent_action_approval,
    create_conversation,
    decode_diagnose_image,
    delete_conversation,
    get_conversation,
    get_conversation_with_messages,
    get_health_eval,
    get_treatment,
    list_health_evals_query,
    list_treatments_query,
    list_user_conversations_query,
    normalize_health_action,
    normalize_health_history_action,
    normalize_health_history_issue,
    normalize_health_issue,
    parse_diagnosis_response,
    parse_health_check_json,
    parse_optional_uuid,
    photo_url_for_key,
    record_agent_action_approval_decision,
    search_treatments_query,
    transition_agent_action,
    update_conversation_title,
)


class TestParseOptionalUuid:
    def test_none_returns_none(self):
        assert parse_optional_uuid(None) is None

    def test_empty_string_returns_none(self):
        # The route accepts an absent query param as None and an empty
        # string from form-encoded inputs the same way.
        assert parse_optional_uuid("") is None

    def test_valid_uuid_round_trips(self):
        u = uuid4()
        assert parse_optional_uuid(str(u)) == u

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_optional_uuid("not-a-uuid")

    def test_partial_uuid_raises(self):
        with pytest.raises(ValueError):
            parse_optional_uuid("12345")

    def test_canonical_lowercase_hex(self):
        # Canonical UUID string form is accepted as-is.
        u = UUID("12345678-1234-5678-1234-567812345678")
        assert parse_optional_uuid("12345678-1234-5678-1234-567812345678") == u


# ---------- Diagnose service helpers ----------


class TestDecodeDiagnoseImage:
    def test_valid_image_round_trips(self):
        # Tiny 1x1 PNG-ish payload
        payload = b"\x89PNG\r\n\x1a\nfake"
        b64 = base64.b64encode(payload).decode()
        assert decode_diagnose_image(b64) == payload

    def test_invalid_base64_raises(self):
        with pytest.raises(DiagnoseImageError, match="Invalid base64"):
            decode_diagnose_image("not valid base64!!!")

    def test_oversize_raises(self):
        # Build a payload that bcrypt-style decodes to > MAX bytes
        payload = b"x" * (MAX_DIAGNOSE_IMAGE_BYTES + 1)
        b64 = base64.b64encode(payload).decode()
        with pytest.raises(DiagnoseImageError, match="exceeds"):
            decode_diagnose_image(b64)

    def test_size_cap_documented(self):
        # 10 MiB matches multipart limits across the stack — guard against drift.
        assert MAX_DIAGNOSE_IMAGE_BYTES == 10 * 1024 * 1024


class TestBuildDiagnosisPrompt:
    def test_no_context_returns_base_prompt_plus_instruction(self):
        out = build_diagnosis_prompt()
        assert DIAGNOSIS_SYSTEM_PROMPT in out
        assert "Analyze the photo and provide your diagnosis as JSON." in out
        # No context block
        assert "Context:" not in out

    def test_grow_type_only(self):
        out = build_diagnosis_prompt(grow_type="dwc")
        assert "Context:" in out
        assert "Grow method: dwc" in out
        assert "Current stage:" not in out

    def test_all_context_fields(self):
        out = build_diagnosis_prompt(
            grow_type="coco",
            current_stage="flowering",
            observations="Yellow tips on lower fans",
        )
        assert "Grow method: coco" in out
        assert "Current stage: flowering" in out
        assert "Grower observations: Yellow tips on lower fans" in out

    def test_empty_strings_treated_as_falsy(self):
        out = build_diagnosis_prompt(grow_type="", current_stage="", observations="")
        # Empty strings → no context block
        assert "Context:" not in out


class TestParseDiagnosisResponse:
    def test_valid_json_round_trip(self):
        raw = (
            '{"summary": "Plant looks healthy", '
            '"recommended_actions": ["water tomorrow"], '
            '"overall_severity": "low", "overall_score": 95, '
            '"grow_stage_assessment": "Mid veg", "issues": []}'
        )
        parsed = parse_diagnosis_response(raw)
        assert parsed.summary == "Plant looks healthy"
        assert parsed.actions == ["water tomorrow"]
        assert parsed.overall_severity == "low"
        assert parsed.overall_score == 95
        assert parsed.grow_stage_assessment == "Mid veg"
        assert parsed.issues == []

    def test_issues_parsed(self):
        raw = (
            '{"summary": "x", "recommended_actions": [], '
            '"overall_severity": "high", "overall_score": 60, '
            '"grow_stage_assessment": null, '
            '"issues": [{"treatment_id": "nitrogen_deficiency", '
            '"name": "N def", "confidence": 0.92, "severity": "high", '
            '"description": "yellowing", "treatment": "feed N"}]}'
        )
        parsed = parse_diagnosis_response(raw)
        assert len(parsed.issues) == 1
        i = parsed.issues[0]
        assert i.treatment_id == "nitrogen_deficiency"
        assert i.confidence == 0.92
        assert i.severity == "high"

    def test_confidence_clamped_to_0_1(self):
        raw = (
            '{"summary": "x", "recommended_actions": [], '
            '"overall_severity": "low", "overall_score": 100, '
            '"grow_stage_assessment": null, '
            '"issues": [{"treatment_id": "t", "name": "n", '
            '"confidence": 1.5, "severity": "low"}, '
            '{"treatment_id": "u", "name": "m", '
            '"confidence": -0.3, "severity": "low"}]}'
        )
        parsed = parse_diagnosis_response(raw)
        assert parsed.issues[0].confidence == 1.0
        assert parsed.issues[1].confidence == 0.0

    def test_strips_markdown_fence(self):
        raw = '```json\n{"summary": "fenced", "recommended_actions": [], "overall_severity": "low", "overall_score": 50, "grow_stage_assessment": null, "issues": []}\n```'
        parsed = parse_diagnosis_response(raw)
        assert parsed.summary == "fenced"

    def test_invalid_json_falls_back_to_raw_summary(self):
        parsed = parse_diagnosis_response("not json at all")
        assert parsed.summary == "not json at all"
        assert parsed.overall_severity == DEFAULT_DIAGNOSIS_OVERALL_SEVERITY
        assert parsed.overall_score == DEFAULT_DIAGNOSIS_OVERALL_SCORE
        assert parsed.issues == []

    def test_empty_string_falls_back(self):
        parsed = parse_diagnosis_response("")
        # Documented placeholder when there's no raw text either.
        assert parsed.summary == "Diagnosis could not be parsed"

    def test_long_invalid_response_truncated_to_500(self):
        long_raw = "x" * 1000
        parsed = parse_diagnosis_response(long_raw)
        assert len(parsed.summary) == 500


# ---------- Health-check service helpers ----------


class TestNormalizeHealthIssue:
    def test_string_passes_through(self):
        assert normalize_health_issue("Leaves yellowing") == "Leaves yellowing"

    def test_dict_description(self):
        assert normalize_health_issue({"description": "Nitrogen def"}) == "Nitrogen def"

    def test_dict_message_fallback(self):
        assert normalize_health_issue({"message": "Low EC"}) == "Low EC"

    def test_dict_issue_fallback(self):
        assert normalize_health_issue({"issue": "Light burn"}) == "Light burn"

    def test_dict_with_category_prefix(self):
        out = normalize_health_issue({"description": "Yellowing", "category": "Nutrient"})
        assert out == "[Nutrient] Yellowing"

    def test_dict_no_recognized_keys_str_fallback(self):
        out = normalize_health_issue({"random": "x"})
        # str(dict) — preserves the previous fallback behaviour
        assert "random" in out

    def test_non_string_non_dict_str_fallback(self):
        assert normalize_health_issue(42) == "42"


class TestNormalizeHealthAction:
    def test_string_passes_through(self):
        assert normalize_health_action("Water tomorrow") == "Water tomorrow"

    def test_dict_action_key(self):
        assert normalize_health_action({"action": "Flush"}) == "Flush"

    def test_dict_message_fallback(self):
        assert normalize_health_action({"message": "Check pH"}) == "Check pH"

    def test_dict_description_fallback(self):
        assert normalize_health_action({"description": "Top up"}) == "Top up"

    def test_dict_no_keys_str_fallback(self):
        out = normalize_health_action({"random": "x"})
        assert "random" in out


class TestNormalizeHealthHistoryHelpers:
    """History-listing variants do NOT add the [category] prefix —
    pin that difference."""

    def test_issue_no_category_prefix(self):
        out = normalize_health_history_issue({"message": "Yellowing", "category": "Nutrient"})
        # Category is silently ignored — different from normalize_health_issue
        assert "[" not in out
        assert out == "Yellowing"

    def test_issue_uses_message_or_issue(self):
        assert normalize_health_history_issue({"issue": "Light burn"}) == "Light burn"

    def test_action_uses_message_or_action(self):
        assert normalize_health_history_action({"action": "Flush"}) == "Flush"
        assert normalize_health_history_action({"message": "Check pH"}) == "Check pH"


class TestParseHealthCheckJson:
    def test_valid_json(self):
        raw = (
            '{"score": 85, '
            '"issues": [{"description": "Yellow tips", "category": "Nutrient"}], '
            '"actions": [{"action": "Flush"}]}'
        )
        score, issues, actions = parse_health_check_json(raw)
        assert score == 85
        assert issues == ["[Nutrient] Yellow tips"]
        assert actions == ["Flush"]

    def test_strips_fence(self):
        raw = '```json\n{"score": 90, "issues": [], "actions": []}\n```'
        score, issues, actions = parse_health_check_json(raw)
        assert score == 90
        assert issues == []
        assert actions == []

    def test_invalid_json_returns_empty(self):
        score, issues, actions = parse_health_check_json("not json")
        assert score is None
        assert issues == []
        assert actions == []

    def test_string_lists_pass_through(self):
        raw = '{"score": 70, "issues": ["Low water"], "actions": ["Top up tomorrow"]}'
        score, issues, actions = parse_health_check_json(raw)
        assert score == 70
        assert issues == ["Low water"]
        assert actions == ["Top up tomorrow"]


class TestHealthHistoryMaxLimit:
    def test_cap_is_50(self):
        # The history endpoint silently caps the caller's `limit` here —
        # if this changes, the API contract changes too.
        assert HEALTH_HISTORY_MAX_LIMIT == 50


@pytest.mark.asyncio(loop_scope="session")
class TestConversationServiceMethods:
    async def test_create_conversation_persists_and_returns_model(self):
        session = AsyncMock()
        session.add = Mock()
        tenant_id = uuid4()
        user_id = uuid4()
        grow_cycle_id = uuid4()

        conv = await create_conversation(
            session,
            tenant_id=tenant_id,
            user_id=user_id,
            grow_cycle_id=grow_cycle_id,
            title="My Run",
        )

        assert isinstance(conv, Conversation)
        assert conv.tenant_id == tenant_id
        assert conv.user_id == user_id
        assert conv.grow_cycle_id == grow_cycle_id
        assert conv.title == "My Run"
        session.add.assert_called_once_with(conv)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(conv)

    async def test_get_conversation_returns_none_for_cross_tenant(self):
        session = AsyncMock()
        conv = Conversation(tenant_id=uuid4(), user_id=uuid4(), grow_cycle_id=None, title="x")
        session.get.return_value = conv

        got = await get_conversation(session, tenant_id=uuid4(), conversation_id=uuid4())
        assert got is None

    async def test_get_conversation_returns_match_for_same_tenant(self):
        session = AsyncMock()
        tenant_id = uuid4()
        conv = Conversation(tenant_id=tenant_id, user_id=uuid4(), grow_cycle_id=None, title="x")
        conv_id = uuid4()
        session.get.return_value = conv

        got = await get_conversation(session, tenant_id=tenant_id, conversation_id=conv_id)
        assert got is conv
        session.get.assert_awaited_once_with(Conversation, conv_id)

    async def test_get_conversation_with_messages_uses_execute_result(self):
        session = AsyncMock()
        result = Mock()
        conv = Conversation(tenant_id=uuid4(), user_id=uuid4(), grow_cycle_id=None, title="chat")
        result.scalar_one_or_none.return_value = conv
        session.execute.return_value = result

        got = await get_conversation_with_messages(session, tenant_id=uuid4(), conversation_id=uuid4())

        assert got is conv
        session.execute.assert_awaited_once()
        result.scalar_one_or_none.assert_called_once_with()

    async def test_update_title_commits_refreshes_and_returns(self):
        session = AsyncMock()
        conv = Conversation(tenant_id=uuid4(), user_id=uuid4(), grow_cycle_id=None, title="old")

        got = await update_conversation_title(session, conv, title="new")

        assert got is conv
        assert conv.title == "new"
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(conv)

    async def test_delete_conversation_deletes_and_commits(self):
        session = AsyncMock()
        conv = Conversation(tenant_id=uuid4(), user_id=uuid4(), grow_cycle_id=None, title=None)

        await delete_conversation(session, conv)

        session.delete.assert_awaited_once_with(conv)
        session.commit.assert_awaited_once()

    async def test_get_health_eval_delegates_to_session_get(self):
        from app.grows.models import HealthEval

        session = AsyncMock()
        eval_id = uuid4()
        expected = object()
        session.get.return_value = expected

        got = await get_health_eval(session, eval_id)

        assert got is expected
        session.get.assert_awaited_once_with(HealthEval, eval_id)

    async def test_get_treatment_delegates_to_session_get(self):
        from app.grows.models import PlantHealthTreatment

        session = AsyncMock()
        expected = object()
        session.get.return_value = expected

        got = await get_treatment(session, "nitrogen_deficiency")

        assert got is expected
        session.get.assert_awaited_once_with(PlantHealthTreatment, "nitrogen_deficiency")


@pytest.mark.asyncio(loop_scope="session")
class TestAgentActionServiceMethods:
    async def test_create_agent_action_persists_and_returns_model(self):
        session = AsyncMock()
        session.add = Mock()
        tenant_id = uuid4()
        conversation_id = uuid4()
        grow_cycle_id = uuid4()
        user_id = uuid4()
        key = build_agent_action_idempotency_key(
            tenant_id=tenant_id,
            source="health_check",
            action_type="create_task",
            grow_cycle_id=grow_cycle_id,
            conversation_id=conversation_id,
        )

        action = await create_agent_action(
            session,
            tenant_id=tenant_id,
            source="health_check",
            action_type="create_task",
            title="Create a flush task",
            idempotency_key=key,
            conversation_id=conversation_id,
            grow_cycle_id=grow_cycle_id,
            created_by_user_id=user_id,
            requires_approval=True,
        )

        assert isinstance(action, AgentAction)
        assert action.tenant_id == tenant_id
        assert action.status == AGENT_ACTION_STATUS_PROPOSED
        assert action.idempotency_key == key
        session.add.assert_called_once_with(action)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(action)

    async def test_create_agent_action_approval_persists_pending_record(self):
        session = AsyncMock()
        session.add = Mock()
        tenant_id = uuid4()
        action_id = uuid4()
        requester = uuid4()

        approval = await create_agent_action_approval(
            session,
            tenant_id=tenant_id,
            action_id=action_id,
            requested_by_user_id=requester,
        )

        assert isinstance(approval, AgentActionApproval)
        assert approval.status == AGENT_APPROVAL_STATUS_PENDING
        assert approval.action_id == action_id
        session.add.assert_called_once_with(approval)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(approval)

    async def test_transition_agent_action_updates_status_and_timestamps(self):
        session = AsyncMock()
        action = AgentAction(
            tenant_id=uuid4(),
            source="health_check",
            action_type="create_task",
            title="Task",
            status=AGENT_ACTION_STATUS_PENDING_APPROVAL,
            risk_level="low",
            idempotency_key="k" * 64,
        )

        approved = await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_APPROVED)
        assert approved.status == AGENT_ACTION_STATUS_APPROVED
        assert approved.approved_at is not None

        executing = await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_EXECUTING)
        assert executing.status == AGENT_ACTION_STATUS_EXECUTING
        assert executing.executed_at is not None

        completed = await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_COMPLETED)
        assert completed.status == AGENT_ACTION_STATUS_COMPLETED

        verified = await transition_agent_action(
            session,
            action,
            next_status=AGENT_ACTION_STATUS_VERIFIED,
            verification_json={"result": "ok"},
        )
        assert verified.status == AGENT_ACTION_STATUS_VERIFIED
        assert verified.verified_at is not None
        assert verified.verification_json == {"result": "ok"}
        assert session.commit.await_count == 4
        assert session.refresh.await_count == 4

    async def test_transition_agent_action_rejects_invalid_transition(self):
        session = AsyncMock()
        action = AgentAction(
            tenant_id=uuid4(),
            source="health_check",
            action_type="create_task",
            title="Task",
            status=AGENT_ACTION_STATUS_PROPOSED,
            risk_level="low",
            idempotency_key="k" * 64,
        )

        with pytest.raises(InvalidAgentActionTransitionError, match="proposed -> verified"):
            await transition_agent_action(session, action, next_status=AGENT_ACTION_STATUS_VERIFIED)

    async def test_record_agent_action_approval_decision_updates_review_fields(self):
        session = AsyncMock()
        reviewer = uuid4()
        approval = AgentActionApproval(
            tenant_id=uuid4(),
            action_id=uuid4(),
            status=AGENT_APPROVAL_STATUS_PENDING,
        )

        updated = await record_agent_action_approval_decision(
            session,
            approval,
            decision_status=AGENT_APPROVAL_STATUS_APPROVED,
            reviewed_by_user_id=reviewer,
            reason="Safe action",
        )

        assert updated.status == AGENT_APPROVAL_STATUS_APPROVED
        assert updated.reviewed_by_user_id == reviewer
        assert updated.reviewed_at is not None
        assert updated.reason == "Safe action"
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(approval)

    async def test_record_agent_action_approval_decision_rejects_non_pending(self):
        session = AsyncMock()
        approval = AgentActionApproval(
            tenant_id=uuid4(),
            action_id=uuid4(),
            status=AGENT_APPROVAL_STATUS_REJECTED,
        )

        with pytest.raises(InvalidAgentApprovalTransitionError, match="rejected -> approved"):
            await record_agent_action_approval_decision(
                session,
                approval,
                decision_status=AGENT_APPROVAL_STATUS_APPROVED,
                reviewed_by_user_id=uuid4(),
            )


class TestAiServiceQueries:
    def test_build_agent_action_idempotency_key_is_deterministic(self):
        tenant_id = uuid4()
        grow_id = uuid4()
        conversation_id = uuid4()

        a = build_agent_action_idempotency_key(
            tenant_id=tenant_id,
            source="health_check",
            action_type="create_task",
            grow_cycle_id=grow_id,
            conversation_id=conversation_id,
            dedupe_token="flush",
        )
        b = build_agent_action_idempotency_key(
            tenant_id=tenant_id,
            source="health_check",
            action_type="create_task",
            grow_cycle_id=grow_id,
            conversation_id=conversation_id,
            dedupe_token="flush",
        )
        c = build_agent_action_idempotency_key(
            tenant_id=tenant_id,
            source="health_check",
            action_type="create_task",
            grow_cycle_id=grow_id,
            conversation_id=conversation_id,
            dedupe_token="different",
        )

        assert a == b
        assert a != c
        assert len(a) == 64

    def test_can_transition_agent_action_allows_and_blocks_expected_paths(self):
        assert can_transition_agent_action(AGENT_ACTION_STATUS_PROPOSED, AGENT_ACTION_STATUS_PENDING_APPROVAL)
        assert can_transition_agent_action(AGENT_ACTION_STATUS_PENDING_APPROVAL, AGENT_ACTION_STATUS_APPROVED)
        assert can_transition_agent_action(AGENT_ACTION_STATUS_COMPLETED, AGENT_ACTION_STATUS_VERIFIED)
        assert not can_transition_agent_action(AGENT_ACTION_STATUS_PROPOSED, AGENT_ACTION_STATUS_VERIFIED)

    def test_list_user_conversations_query_filters_by_tenant_user_and_optional_grow(self):
        tenant_id = uuid4()
        user_id = uuid4()
        grow_id = uuid4()

        q_no_grow = list_user_conversations_query(tenant_id=tenant_id, user_id=user_id)
        params_no_grow = q_no_grow.compile().params
        assert tenant_id in params_no_grow.values()
        assert user_id in params_no_grow.values()
        assert grow_id not in params_no_grow.values()

        q_with_grow = list_user_conversations_query(
            tenant_id=tenant_id,
            user_id=user_id,
            grow_cycle_id=grow_id,
        )
        params_with_grow = q_with_grow.compile().params
        assert tenant_id in params_with_grow.values()
        assert user_id in params_with_grow.values()
        assert grow_id in params_with_grow.values()

    def test_list_health_evals_query_caps_limit(self):
        grow_id = uuid4()

        capped = list_health_evals_query(grow_id=grow_id, limit=999)
        small = list_health_evals_query(grow_id=grow_id, limit=7)

        capped_params = capped.compile().params
        small_params = small.compile().params
        assert grow_id in capped_params.values()
        assert grow_id in small_params.values()
        assert HEALTH_HISTORY_MAX_LIMIT in capped_params.values()
        assert 7 in small_params.values()

    def test_list_treatments_query_optionally_filters_category(self):
        all_q = list_treatments_query()
        all_params = all_q.compile().params
        assert all_params == {}

        filtered_q = list_treatments_query(category="deficiency")
        filtered_params = filtered_q.compile().params
        assert "deficiency" in filtered_params.values()

    def test_search_treatments_query_sets_ilike_term(self):
        q = search_treatments_query(query_text="Yellow")
        params = q.compile().params
        assert "%yellow%" in params.values()


class TestAiServicePhotoUrls:
    def test_build_photo_url_base_prod_domain(self, monkeypatch):
        monkeypatch.setattr("app.config.get_settings", lambda: SimpleNamespace(domain="tendril.dev"))
        assert build_photo_url_base() == "https://api.tendril.dev/v1"

    def test_build_photo_url_base_dev_default(self, monkeypatch):
        monkeypatch.setattr("app.config.get_settings", lambda: SimpleNamespace(domain=""))
        assert build_photo_url_base() == "http://localhost:8000/v1"

    def test_photo_url_for_key_handles_none_and_value(self, monkeypatch):
        monkeypatch.setattr("app.config.get_settings", lambda: SimpleNamespace(domain="tendril.dev"))
        assert photo_url_for_key(None) is None
        assert photo_url_for_key("") is None
        assert photo_url_for_key("photos/abc.jpg") == "https://api.tendril.dev/v1/photos/grow/key/photos/abc.jpg"
