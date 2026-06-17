"""Unit tests for app.support.service — tickets domain."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.support.models import TicketCategory, TicketPriority, TicketStatus
from app.support.service import (
    SLA_HOURS,
    coerce_category,
    coerce_priority,
    compute_sla_due,
    is_ticket_closed,
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
