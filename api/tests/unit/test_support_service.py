"""Unit tests for app.support.service — tickets domain."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.support.models import ForumThreadStatus, TicketCategory, TicketPriority, TicketStatus
from app.support.service import (
    SLA_HOURS,
    coerce_category,
    coerce_priority,
    compute_sla_due,
    is_forum_thread_locked,
    is_ticket_closed,
    slugify,
)


class TestCoerceCategory:
    def test_known_category(self):
        assert coerce_category("billing") == TicketCategory.billing

    def test_unknown_category_falls_back_to_general(self):
        assert coerce_category("not-a-real-category") == TicketCategory.general

    def test_empty_falls_back_to_general(self):
        assert coerce_category("") == TicketCategory.general


class TestCoercePriority:
    def test_known_priority(self):
        assert coerce_priority("urgent") == TicketPriority.urgent

    def test_unknown_priority_falls_back_to_medium(self):
        assert coerce_priority("blocker") == TicketPriority.medium

    def test_empty_falls_back_to_medium(self):
        assert coerce_priority("") == TicketPriority.medium


class TestComputeSLADue:
    @pytest.mark.parametrize(
        "priority,expected_hours",
        [
            (TicketPriority.urgent, 1),
            (TicketPriority.high, 4),
            (TicketPriority.medium, 24),
            (TicketPriority.low, 72),
        ],
    )
    def test_each_priority(self, priority, expected_hours):
        now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
        due = compute_sla_due(priority, now=now)
        assert due - now == timedelta(hours=expected_hours)

    def test_sla_hours_table_is_complete(self):
        for priority in TicketPriority:
            assert priority in SLA_HOURS, f"missing SLA for {priority}"

    def test_default_now_is_utc(self):
        # No exception + the returned datetime is at least the right shape.
        due = compute_sla_due(TicketPriority.medium)
        assert due.tzinfo is not None
        # Must be roughly 24h in the future.
        delta = due - datetime.now(UTC)
        assert timedelta(hours=23, minutes=59) < delta < timedelta(hours=24, minutes=1)


class _FakeTicket:
    """Minimal stand-in to exercise the pure ``is_ticket_closed`` helper."""

    def __init__(self, status: TicketStatus) -> None:
        self.status = status


class TestIsTicketClosed:
    def test_closed_is_closed(self):
        assert is_ticket_closed(_FakeTicket(TicketStatus.closed)) is True

    def test_resolved_is_closed(self):
        assert is_ticket_closed(_FakeTicket(TicketStatus.resolved)) is True

    @pytest.mark.parametrize(
        "status",
        [
            TicketStatus.open,
            TicketStatus.in_progress,
            TicketStatus.waiting_on_user,
            TicketStatus.waiting_on_staff,
        ],
    )
    def test_open_states_are_not_closed(self, status):
        assert is_ticket_closed(_FakeTicket(status)) is False


# ---------- KB service helpers ----------


class TestSlugify:
    def test_basic_lowercase(self):
        assert slugify("Hello World") == "hello-world"

    def test_strips_punctuation(self):
        assert slugify("How To: Use the AI! (Beginner's Guide)") == "how-to-use-the-ai-beginners-guide"

    def test_collapses_whitespace_and_underscores(self):
        assert slugify("a  b\t_c") == "a-b-c"

    def test_dedupes_dashes(self):
        assert slugify("a---b---c") == "a-b-c"

    def test_trims_leading_trailing_dashes(self):
        assert slugify("---hello---") == "hello"

    def test_empty_string_stays_empty(self):
        assert slugify("") == ""

    def test_keeps_alphanumeric_and_underscore(self):
        # ``[^\w\s-]`` keeps word chars (alphanumeric + underscore); the next
        # rule collapses them. So "v2_release" becomes "v2-release".
        assert slugify("v2_release") == "v2-release"


# ---------- Forum service helpers ----------


class _FakeThread:
    def __init__(self, status):
        self.status = status


class TestIsForumThreadLocked:
    def test_locked_is_locked(self):
        assert is_forum_thread_locked(_FakeThread(ForumThreadStatus.locked)) is True

    @pytest.mark.parametrize(
        "status",
        [ForumThreadStatus.open, ForumThreadStatus.solved, ForumThreadStatus.pinned],
    )
    def test_other_statuses_not_locked(self, status):
        assert is_forum_thread_locked(_FakeThread(status)) is False
