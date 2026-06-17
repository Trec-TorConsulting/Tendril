"""Unit tests for app.reference.service pure helpers.

These exercise the filter/slug/render functions that don't need a DB.
Route-level integration coverage lives in tests/unit/test_reference.py.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.reference.service import (
    NUTRIENT_KNOWLEDGE_CATEGORIES,
    filter_diy_recipes,
    filter_emergency_substitutions,
    filter_feed_charts_by_medium,
    filter_methodology_guides,
    filter_ph_alternatives,
    render_esphome_yaml,
    slugify_device_name,
)

# ─── Slug ────────────────────────────────────────────────────────────────────


class TestSlugifyDeviceName:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Living Room", "living-room"),
            ("Living_Room", "living-room"),
            ("multi  space  name", "multi--space--name"),  # only single space/_ replaced
            ("UPPER CASE", "upper-case"),
            ("alreadydashed-name", "alreadydashed-name"),
        ],
    )
    def test_cases(self, name, expected):
        assert slugify_device_name(name) == expected


# ─── Feed charts ─────────────────────────────────────────────────────────────


@dataclass
class _FakeChart:
    medium: list[str] | None


class TestFilterFeedChartsByMedium:
    def test_none_returns_all(self):
        charts = [_FakeChart(["soil"]), _FakeChart(["hydro"])]
        assert filter_feed_charts_by_medium(charts, None) == charts

    def test_empty_string_returns_all(self):
        charts = [_FakeChart(["soil"]), _FakeChart(["hydro"])]
        assert filter_feed_charts_by_medium(charts, "") == charts

    def test_matches_case_insensitive(self):
        charts = [_FakeChart(["soil"]), _FakeChart(["hydro"])]
        out = filter_feed_charts_by_medium(charts, "SOIL")
        assert len(out) == 1
        assert out[0].medium == ["soil"]

    def test_none_medium_field_skipped(self):
        charts = [_FakeChart(None), _FakeChart(["hydro"])]
        out = filter_feed_charts_by_medium(charts, "hydro")
        assert len(out) == 1


# ─── Nutrient knowledge filters ──────────────────────────────────────────────


class TestNutrientKnowledgeCategories:
    def test_canonical_four(self):
        # The route layer dereferences these four keys explicitly when
        # building the public /knowledge response — guard against renames.
        assert NUTRIENT_KNOWLEDGE_CATEGORIES == (
            "diy_recipe",
            "emergency_substitution",
            "ph_alternative",
            "methodology_guide",
        )


class TestFilterDIYRecipes:
    @pytest.fixture
    def recipes(self):
        return [
            {"category": "veg", "difficulty": "easy"},
            {"category": "flower", "difficulty": "easy"},
            {"category": "veg", "difficulty": "hard"},
            {"category": "flower"},
        ]

    def test_no_filters(self, recipes):
        assert filter_diy_recipes(recipes, category=None, difficulty=None) == recipes

    def test_by_category(self, recipes):
        out = filter_diy_recipes(recipes, category="veg", difficulty=None)
        assert len(out) == 2
        assert all(r["category"] == "veg" for r in out)

    def test_by_difficulty(self, recipes):
        out = filter_diy_recipes(recipes, category=None, difficulty="easy")
        assert len(out) == 2

    def test_both_filters(self, recipes):
        out = filter_diy_recipes(recipes, category="veg", difficulty="easy")
        assert out == [{"category": "veg", "difficulty": "easy"}]


class TestFilterEmergencySubstitutions:
    @pytest.fixture
    def subs(self):
        return [
            {"id": "nitrogen-deficiency"},
            {"id": "potassium-deficiency"},
            {"id": "calmag"},
        ]

    def test_no_filter(self, subs):
        assert filter_emergency_substitutions(subs, deficiency=None) == subs

    def test_matches_substring_case_insensitive(self, subs):
        out = filter_emergency_substitutions(subs, deficiency="NITROGEN")
        assert out == [{"id": "nitrogen-deficiency"}]

    def test_no_match_returns_empty(self, subs):
        assert filter_emergency_substitutions(subs, deficiency="zinc") == []


class TestFilterPhAlternatives:
    def test_direction_case_insensitive(self):
        alts = [{"direction": "up"}, {"direction": "down"}, {"direction": "up"}]
        out = filter_ph_alternatives(alts, direction="UP")
        assert len(out) == 2

    def test_no_filter(self):
        alts = [{"direction": "up"}, {"direction": "down"}]
        assert filter_ph_alternatives(alts, direction=None) == alts


class TestFilterMethodologyGuides:
    def test_approach_case_insensitive(self):
        guides = [{"approach": "organic"}, {"approach": "sterile"}, {"approach": "organic"}]
        out = filter_methodology_guides(guides, approach="ORGANIC")
        assert len(out) == 2

    def test_no_filter(self):
        guides = [{"approach": "organic"}]
        assert filter_methodology_guides(guides, approach=None) == guides


# ─── ESPHome YAML render ─────────────────────────────────────────────────────


@dataclass
class _FakeTemplate:
    template_id: str
    name: str
    board: str
    sensors: list[str]
    yaml_body: str


class TestRenderEsphomeYaml:
    @pytest.fixture
    def template(self):
        return _FakeTemplate(
            template_id="soil_basic",
            name="Soil Basic",
            board="esp32dev",
            sensors=["soil_moisture", "soil_temp"],
            yaml_body="\nsensor: []\n",
        )

    def test_contains_device_metadata(self, template):
        yaml = render_esphome_yaml(
            template,
            device_name="Tent A",
            mqtt_host="mqtt.example.com",
            mqtt_user="td-1",
            mqtt_password="secret",
            wifi_ssid="MyWifi",
            wifi_password="wifipw",
        )
        assert "name: tent-a" in yaml  # slugified
        assert 'friendly_name: "Tent A"' in yaml
        assert "board: esp32dev" in yaml

    def test_contains_secrets_and_topic_prefix(self, template):
        yaml = render_esphome_yaml(
            template,
            device_name="My_Sensor",
            mqtt_host="mqtt.local",
            mqtt_user="td-x",
            mqtt_password="pw",
            wifi_ssid="ssid",
            wifi_password="wpw",
        )
        assert 'broker: "mqtt.local"' in yaml
        assert 'username: "td-x"' in yaml
        assert 'password: "pw"' in yaml
        assert 'ssid: "ssid"' in yaml
        # Topic prefix uses the slugified name
        assert 'topic_prefix: "tendril/my-sensor"' in yaml

    def test_includes_template_yaml_body(self, template):
        yaml = render_esphome_yaml(
            template,
            device_name="X",
            mqtt_host="h",
            mqtt_user="u",
            mqtt_password="p",
            wifi_ssid="s",
            wifi_password="w",
        )
        assert "sensor: []" in yaml

    def test_lists_sensor_names_in_comment(self, template):
        yaml = render_esphome_yaml(
            template,
            device_name="X",
            mqtt_host="h",
            mqtt_user="u",
            mqtt_password="p",
            wifi_ssid="s",
            wifi_password="w",
        )
        assert "Sensors: soil_moisture, soil_temp" in yaml
