"""Unit tests for app.analytics.service pure helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.service import (
    BUCKET_METRICS,
    MAX_SERIES_DAYS,
    TENT_METRICS,
    VALID_METRICS,
    InvalidMetricError,
    compute_duration_days,
    compute_series_day_count,
    rank_comparable_candidates,
    validate_metric,
)


@dataclass
class _FakeGrow:
    started_at: datetime | None = None
    ended_at: datetime | None = None


class TestValidMetrics:
    def test_canonical_set(self):
        # The frontend hard-codes this set in its metric switcher — keep it stable.
        assert frozenset({"ph", "ec", "vpd", "temp", "humidity", "water_temp"}) == VALID_METRICS

    def test_bucket_metrics(self):
        assert frozenset({"ph", "ec", "water_temp"}) == BUCKET_METRICS

    def test_tent_metrics(self):
        assert frozenset({"vpd", "temp", "humidity"}) == TENT_METRICS

    def test_no_overlap(self):
        assert BUCKET_METRICS.isdisjoint(TENT_METRICS)

    def test_union_is_valid(self):
        assert BUCKET_METRICS | TENT_METRICS == VALID_METRICS


class TestValidateMetric:
    @pytest.mark.parametrize("metric", ["ph", "ec", "vpd", "temp", "humidity", "water_temp"])
    def test_accepts_known(self, metric):
        validate_metric(metric)  # no raise

    def test_rejects_unknown(self):
        with pytest.raises(InvalidMetricError) as exc:
            validate_metric("bogus")
        assert exc.value.metric == "bogus"

    def test_empty_rejected(self):
        with pytest.raises(InvalidMetricError):
            validate_metric("")


class TestComputeDurationDays:
    def test_returns_none_for_no_start(self):
        assert compute_duration_days(_FakeGrow()) is None

    def test_uses_ended_at_when_present(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        end = datetime(2026, 1, 30, tzinfo=UTC)
        grow = _FakeGrow(started_at=start, ended_at=end)
        assert compute_duration_days(grow) == 29

    def test_uses_now_when_no_end(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        now = datetime(2026, 1, 11, tzinfo=UTC)
        grow = _FakeGrow(started_at=start)
        assert compute_duration_days(grow, now=now) == 10


class TestComputeSeriesDayCount:
    def test_zero_for_no_start(self):
        assert compute_series_day_count(_FakeGrow()) == 0

    def test_basic(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        end = datetime(2026, 1, 11, tzinfo=UTC)
        grow = _FakeGrow(started_at=start, ended_at=end)
        # 10-day span + 1 = 11 buckets
        assert compute_series_day_count(grow) == 11

    def test_capped_at_max(self):
        start = datetime(2020, 1, 1, tzinfo=UTC)
        end = datetime(2026, 1, 1, tzinfo=UTC)
        grow = _FakeGrow(started_at=start, ended_at=end)
        assert compute_series_day_count(grow) == MAX_SERIES_DAYS

    def test_uses_now_when_no_end(self):
        start = datetime(2026, 1, 1, tzinfo=UTC)
        now = start + timedelta(days=5)
        grow = _FakeGrow(started_at=start)
        assert compute_series_day_count(grow, now=now) == 6  # 5 + 1


class TestRankComparableCandidates:
    def test_same_strain_sorts_first(self):
        rows = [
            {"grow_name": "A", "same_strain": False, "started_at": "2025-01-01"},
            {"grow_name": "B", "same_strain": True, "started_at": "2024-01-01"},
            {"grow_name": "C", "same_strain": False, "started_at": "2025-06-01"},
            {"grow_name": "D", "same_strain": True, "started_at": "2025-03-01"},
        ]
        out = rank_comparable_candidates(rows)
        # Same-strain rows (B, D) sort first (B before D by started_at asc),
        # then non-same-strain by started_at asc.
        assert [r["grow_name"] for r in out] == ["B", "D", "A", "C"]

    def test_caps_at_top(self):
        rows = [{"grow_name": f"G{i}", "same_strain": False, "started_at": f"2025-{i + 1:02d}-01"} for i in range(10)]
        out = rank_comparable_candidates(rows, top=3)
        assert len(out) == 3

    def test_handles_missing_started_at(self):
        rows = [
            {"grow_name": "no-date", "same_strain": False},
            {"grow_name": "dated", "same_strain": False, "started_at": "2025-01-01"},
        ]
        out = rank_comparable_candidates(rows)
        # Missing started_at → empty string → sorts first (alphabetically).
        assert [r["grow_name"] for r in out] == ["no-date", "dated"]

    def test_empty_input(self):
        assert rank_comparable_candidates([]) == []
