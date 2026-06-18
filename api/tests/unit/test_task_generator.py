"""Task generator unit tests — intervals, suppression logic, timezone calculations."""

from __future__ import annotations

from datetime import UTC, datetime, time
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from app.scheduler.task_generator import (
    AUTOMATION_SUPPRESSIONS,
    OUTDOOR_TYPES,
    RAIN_SKIP_THRESHOLD_MM,
    TASK_TEMPLATES,
    TaskTemplate,
    _get_grow_automations,
    _get_routine_time,
    _is_suppressed,
    _local_to_utc,
)

# ══════════════════════════════════════════════════════════════════════
# Task Intervals Per Grow Type
# ══════════════════════════════════════════════════════════════════════


class TestTaskIntervalsPerGrowType:
    """Verify task templates have correct intervals for each grow type."""

    def _templates_for(self, category: str, grow_type: str) -> list[TaskTemplate]:
        """Find templates matching a category and grow type."""
        return [
            t for t in TASK_TEMPLATES if t.category == category and (t.grow_types is None or grow_type in t.grow_types)
        ]

    def test_hydro_ph_check_daily(self):
        """Active hydro (DWC, RDWC, NFT) requires daily pH checks."""
        for grow_type in ("dwc", "rdwc", "nft"):
            templates = self._templates_for("ph_check", grow_type)
            assert templates, f"No ph_check template for {grow_type}"
            assert templates[0].interval_days == 1, (
                f"{grow_type} pH check should be daily, got {templates[0].interval_days}"
            )

    def test_soil_ph_check_less_frequent(self):
        """Soil grows check pH every 3+ days (buffered medium)."""
        templates = self._templates_for("ph_check", "soil")
        assert templates
        assert templates[0].interval_days >= 3, f"Soil pH check should be 3+ days, got {templates[0].interval_days}"

    def test_kratky_ph_check_weekly(self):
        """Kratky is passive — pH check is weekly."""
        templates = self._templates_for("ph_check", "kratky")
        assert templates
        assert templates[0].interval_days == 7

    def test_outdoor_soil_ph_check_weekly(self):
        """Outdoor soil pH checks are weekly at most."""
        templates = self._templates_for("ph_check", "outdoor_soil")
        assert templates
        assert templates[0].interval_days >= 7

    def test_hydro_ec_check_daily(self):
        """Active hydro requires daily EC monitoring."""
        for grow_type in ("dwc", "rdwc", "nft", "ebb_flow", "drip", "aeroponics"):
            templates = self._templates_for("ec_check", grow_type)
            assert templates, f"No ec_check template for {grow_type}"
            assert templates[0].interval_days == 1, (
                f"{grow_type} EC check should be daily, got {templates[0].interval_days}"
            )

    def test_kratky_ec_check_weekly(self):
        """Kratky EC naturally rises — only check weekly."""
        templates = self._templates_for("ec_check", "kratky")
        assert templates
        assert templates[0].interval_days == 7

    def test_coco_has_daily_ph_and_ec(self):
        """Coco (inert medium) needs daily pH and EC monitoring."""
        for category in ("ph_check", "ec_check"):
            templates = self._templates_for(category, "coco")
            assert templates, f"No {category} template for coco"
            assert templates[0].interval_days == 1

    def test_all_templates_have_valid_intervals(self):
        """All templates should have a non-negative interval."""
        for t in TASK_TEMPLATES:
            assert t.interval_days >= 0, f"{t.category}/{t.title} has negative interval"

    def test_all_templates_have_valid_routine(self):
        """All templates should have a recognized routine."""
        valid_routines = {"morning", "evening", "weekly", "biweekly", "monthly", "on_demand"}
        for t in TASK_TEMPLATES:
            assert t.routine in valid_routines, f"{t.category}/{t.title} has invalid routine '{t.routine}'"

    def test_all_templates_have_valid_priority(self):
        """All templates should have a recognized priority."""
        valid_priorities = {"low", "medium", "high", "urgent"}
        for t in TASK_TEMPLATES:
            assert t.priority in valid_priorities, f"{t.category}/{t.title} has invalid priority '{t.priority}'"


# ══════════════════════════════════════════════════════════════════════
# Automation Suppression Logic
# ══════════════════════════════════════════════════════════════════════


class TestAutomationSuppression:
    """Verify automation suppression logic correctly hides/replaces tasks."""

    def test_auto_ph_dosing_suppresses_ph_check(self):
        """When auto_ph_dosing is active, ph_check tasks are suppressed."""
        assert _is_suppressed("ph_check", {"auto_ph_dosing"}, AUTOMATION_SUPPRESSIONS)

    def test_auto_ec_dosing_suppresses_ec_check(self):
        """When auto_ec_dosing is active, ec_check tasks are suppressed."""
        assert _is_suppressed("ec_check", {"auto_ec_dosing"}, AUTOMATION_SUPPRESSIONS)

    def test_auto_irrigation_suppresses_watering(self):
        """When auto_irrigation is active, watering tasks are suppressed."""
        assert _is_suppressed("watering", {"auto_irrigation"}, AUTOMATION_SUPPRESSIONS)

    def test_chiller_heater_suppresses_water_temp(self):
        """When chiller_heater is active, water_temp tasks are suppressed."""
        assert _is_suppressed("water_temp", {"chiller_heater"}, AUTOMATION_SUPPRESSIONS)

    def test_inline_monitor_suppresses_ph_and_ec(self):
        """Inline monitor suppresses both ph_check and ec_check."""
        assert _is_suppressed("ph_check", {"inline_monitor"}, AUTOMATION_SUPPRESSIONS)
        assert _is_suppressed("ec_check", {"inline_monitor"}, AUTOMATION_SUPPRESSIONS)

    def test_unrelated_automation_does_not_suppress(self):
        """Auto pH dosing should NOT suppress EC tasks."""
        assert not _is_suppressed("ec_check", {"auto_ph_dosing"}, AUTOMATION_SUPPRESSIONS)
        assert not _is_suppressed("watering", {"auto_ph_dosing"}, AUTOMATION_SUPPRESSIONS)

    def test_no_automations_suppresses_nothing(self):
        """With no automations active, nothing is suppressed."""
        assert not _is_suppressed("ph_check", set(), AUTOMATION_SUPPRESSIONS)
        assert not _is_suppressed("ec_check", set(), AUTOMATION_SUPPRESSIONS)
        assert not _is_suppressed("watering", set(), AUTOMATION_SUPPRESSIONS)

    def test_unknown_category_never_suppressed(self):
        """An unknown category should never be suppressed."""
        all_automations = set(AUTOMATION_SUPPRESSIONS.keys())
        assert not _is_suppressed("nonexistent_category", all_automations, AUTOMATION_SUPPRESSIONS)

    def test_multiple_automations_combined(self):
        """Multiple active automations stack their suppressions."""
        automations = {"auto_ph_dosing", "auto_ec_dosing", "auto_irrigation"}
        assert _is_suppressed("ph_check", automations, AUTOMATION_SUPPRESSIONS)
        assert _is_suppressed("ec_check", automations, AUTOMATION_SUPPRESSIONS)
        assert _is_suppressed("watering", automations, AUTOMATION_SUPPRESSIONS)

    def test_get_grow_automations_from_settings(self):
        """_get_grow_automations extracts automation list from grow settings."""
        grow = MagicMock()
        grow.settings = {"automations": ["auto_ph_dosing", "chiller_heater"]}
        result = _get_grow_automations(grow)
        assert result == {"auto_ph_dosing", "chiller_heater"}

    def test_get_grow_automations_empty_settings(self):
        """Returns empty set when grow has no automation settings."""
        grow = MagicMock()
        grow.settings = {}
        assert _get_grow_automations(grow) == set()

    def test_get_grow_automations_no_settings_attr(self):
        """Returns empty set when grow has no settings attribute."""
        grow = MagicMock(spec=[])  # No attributes
        assert _get_grow_automations(grow) == set()


# ══════════════════════════════════════════════════════════════════════
# Timezone-Aware Due Time Calculation
# ══════════════════════════════════════════════════════════════════════


class TestTimezoneDueTimeCalculation:
    """Verify timezone-aware task scheduling produces correct UTC times."""

    def test_morning_routine_time(self):
        """Morning routine should be 7:00 local time."""
        tz = ZoneInfo("America/New_York")
        result = _get_routine_time("morning", tz)
        assert result == time(7, 0)

    def test_evening_routine_time(self):
        """Evening routine should be 19:00 local time."""
        tz = ZoneInfo("America/New_York")
        result = _get_routine_time("evening", tz)
        assert result == time(19, 0)

    def test_weekly_routine_time(self):
        """Weekly routine should be 9:00 local time."""
        tz = ZoneInfo("US/Pacific")
        result = _get_routine_time("weekly", tz)
        assert result == time(9, 0)

    def test_unknown_routine_defaults_to_9am(self):
        """Unknown routine falls back to 9:00."""
        tz = ZoneInfo("UTC")
        result = _get_routine_time("unknown_routine", tz)
        assert result == time(9, 0)

    def test_local_to_utc_eastern_summer(self):
        """Eastern summer (UTC-4) — 7:00 local → 11:00 UTC."""
        tz = ZoneInfo("America/New_York")
        date = datetime(2025, 7, 15, tzinfo=UTC)  # Summer (EDT, UTC-4)
        local_time = time(7, 0)
        result = _local_to_utc(local_time, date, tz)
        assert result.tzinfo is not None
        utc_result = result.astimezone(UTC)
        assert utc_result.hour == 11
        assert utc_result.minute == 0

    def test_local_to_utc_eastern_winter(self):
        """Eastern winter (UTC-5) — 7:00 local → 12:00 UTC."""
        tz = ZoneInfo("America/New_York")
        date = datetime(2025, 1, 15, tzinfo=UTC)  # Winter (EST, UTC-5)
        local_time = time(7, 0)
        result = _local_to_utc(local_time, date, tz)
        utc_result = result.astimezone(UTC)
        assert utc_result.hour == 12
        assert utc_result.minute == 0

    def test_local_to_utc_pacific(self):
        """Pacific summer (UTC-7) — 9:00 local → 16:00 UTC."""
        tz = ZoneInfo("US/Pacific")
        date = datetime(2025, 7, 15, tzinfo=UTC)
        local_time = time(9, 0)
        result = _local_to_utc(local_time, date, tz)
        utc_result = result.astimezone(UTC)
        assert utc_result.hour == 16

    def test_local_to_utc_utc_timezone(self):
        """UTC timezone — local time equals UTC time."""
        tz = ZoneInfo("UTC")
        date = datetime(2025, 6, 1, tzinfo=UTC)
        local_time = time(19, 0)
        result = _local_to_utc(local_time, date, tz)
        utc_result = result.astimezone(UTC)
        assert utc_result.hour == 19

    def test_local_to_utc_positive_offset(self):
        """Positive UTC offset — 7:00 in UTC+9 (Tokyo) → 22:00 UTC previous day."""
        tz = ZoneInfo("Asia/Tokyo")
        date = datetime(2025, 6, 15, tzinfo=UTC)
        local_time = time(7, 0)
        result = _local_to_utc(local_time, date, tz)
        utc_result = result.astimezone(UTC)
        # 7:00 JST (UTC+9) = 22:00 UTC previous day
        assert utc_result.hour == 22
        assert utc_result.day == 14  # Previous day

    def test_local_to_utc_preserves_date_for_late_times(self):
        """Evening time in positive-offset timezone stays same UTC date."""
        tz = ZoneInfo("Asia/Tokyo")
        date = datetime(2025, 6, 15, tzinfo=UTC)
        local_time = time(19, 0)  # 19:00 JST = 10:00 UTC same day
        result = _local_to_utc(local_time, date, tz)
        utc_result = result.astimezone(UTC)
        assert utc_result.hour == 10
        assert utc_result.day == 15

    def test_all_routines_produce_valid_utc(self):
        """All routine types produce valid UTC datetimes in any timezone."""
        timezones = [
            ZoneInfo("America/New_York"),
            ZoneInfo("US/Pacific"),
            ZoneInfo("Europe/London"),
            ZoneInfo("Asia/Tokyo"),
            ZoneInfo("Australia/Sydney"),
        ]
        routines = ["morning", "evening", "weekly", "biweekly", "monthly", "on_demand"]
        date = datetime(2025, 6, 15, tzinfo=UTC)

        for tz in timezones:
            for routine in routines:
                local_time = _get_routine_time(routine, tz)
                result = _local_to_utc(local_time, date, tz)
                assert result.tzinfo is not None, f"No tzinfo for {routine} in {tz}"
                utc_result = result.astimezone(UTC)
                assert 0 <= utc_result.hour <= 23


# ══════════════════════════════════════════════════════════════════════
# Rain-Skip Logic
# ══════════════════════════════════════════════════════════════════════


class TestRainSkipLogic:
    """Verify rain-skip suppresses outdoor watering tasks when rain is forecast."""

    def test_rain_skip_threshold_is_half_inch(self):
        """Rain-skip threshold should be ~0.5 inches (12.7mm)."""
        assert pytest.approx(12.7, abs=0.1) == RAIN_SKIP_THRESHOLD_MM

    def test_outdoor_types_include_soil_and_container(self):
        """OUTDOOR_TYPES should include outdoor_soil and outdoor_container."""
        assert "outdoor_soil" in OUTDOOR_TYPES
        assert "outdoor_container" in OUTDOOR_TYPES

    def test_watering_templates_exist_for_outdoor(self):
        """Watering task templates exist for outdoor grow types."""
        outdoor_watering = [
            t for t in TASK_TEMPLATES if t.category == "watering" and t.grow_types and t.grow_types & OUTDOOR_TYPES
        ]
        assert len(outdoor_watering) > 0, "No watering templates for outdoor types"
