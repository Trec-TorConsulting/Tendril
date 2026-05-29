"""Tests for AI plant diagnosis and treatment database.

Run with: python3 -m pytest tests/unit/test_plant_diagnosis.py -p no:asyncio -v
"""

from __future__ import annotations

import json
from dataclasses import asdict

# ═══════════════════════════════════════════════════════════════════════
# Treatment Database (existing Python data)
# ═══════════════════════════════════════════════════════════════════════


class TestTreatmentDatabase:
    """Verify the treatment_db.py has all expected entries with complete data."""

    def test_all_entries_present(self):
        from app.ai.treatment_db import TREATMENT_DATABASE

        assert len(TREATMENT_DATABASE) == 16

    def test_all_entries_have_required_fields(self):
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            assert entry.id, "Entry missing id"
            assert entry.category in ("deficiency", "toxicity", "pest", "disease", "environmental")
            assert entry.name
            assert isinstance(entry.aka, list)
            assert entry.summary
            assert isinstance(entry.symptoms, list) and len(entry.symptoms) > 0
            assert isinstance(entry.identification_tips, list) and len(entry.identification_tips) > 0
            assert isinstance(entry.causes, list) and len(entry.causes) > 0
            assert isinstance(entry.severity_criteria, dict)
            assert all(k in entry.severity_criteria for k in ("low", "medium", "high", "critical"))
            assert isinstance(entry.treatments, dict) and len(entry.treatments) > 0
            assert isinstance(entry.prevention, list) and len(entry.prevention) > 0
            assert entry.recovery_time
            assert isinstance(entry.commonly_confused_with, list)

    def test_treatment_categories_coverage(self):
        from app.ai.treatment_db import TREATMENT_DATABASE

        categories = {e.category for e in TREATMENT_DATABASE}
        assert "deficiency" in categories
        assert "pest" in categories
        assert "disease" in categories
        assert "environmental" in categories

    def test_all_entries_have_hydroponic_treatments(self):
        """Every entry should have at least hydroponic treatment steps."""
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            assert "hydroponic" in entry.treatments, f"{entry.id} missing hydroponic treatments"
            assert len(entry.treatments["hydroponic"]) > 0

    def test_all_entries_have_soil_treatments(self):
        """Every entry should have soil treatment steps."""
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            assert "soil" in entry.treatments, f"{entry.id} missing soil treatments"

    def test_get_treatment_by_id(self):
        from app.ai.treatment_db import get_treatment

        result = get_treatment("nitrogen_deficiency")
        assert result is not None
        assert result.name == "Nitrogen Deficiency"

    def test_get_treatment_not_found(self):
        from app.ai.treatment_db import get_treatment

        assert get_treatment("nonexistent_issue") is None

    def test_search_treatments(self):
        from app.ai.treatment_db import search_treatments

        results = search_treatments("yellow")
        assert len(results) > 0
        # Nitrogen deficiency has "yellow" in symptoms
        ids = [r.id for r in results]
        assert "nitrogen_deficiency" in ids

    def test_list_by_category(self):
        from app.ai.treatment_db import list_by_category

        deficiencies = list_by_category("deficiency")
        assert len(deficiencies) == 6  # N, P, K, Ca, Mg, Fe

        pests = list_by_category("pest")
        assert len(pests) == 3  # spider mites, fungus gnats, thrips

        diseases = list_by_category("disease")
        assert len(diseases) == 3  # PM, botrytis, root rot

        environmental = list_by_category("environmental")
        assert len(environmental) == 4  # light burn, heat stress, overwatering, pH lockout

    def test_get_treatments_for_grow_type(self):
        from app.ai.treatment_db import get_treatments_for_grow_type

        hydro = get_treatments_for_grow_type("dwc")
        assert "nitrogen_deficiency" in hydro
        assert isinstance(hydro["nitrogen_deficiency"], list)
        assert len(hydro["nitrogen_deficiency"]) > 0

        soil = get_treatments_for_grow_type("soil")
        assert "nitrogen_deficiency" in soil
        # Soil treatments should differ from hydro
        assert soil["nitrogen_deficiency"] != hydro["nitrogen_deficiency"]

    def test_entry_serialization(self):
        """Entries should be serializable to dict (for DB seeding)."""
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            d = asdict(entry)
            assert isinstance(d, dict)
            # Should be JSON-serializable
            json.dumps(d)


# ═══════════════════════════════════════════════════════════════════════
# Seed Script
# ═══════════════════════════════════════════════════════════════════════


class TestSeedScript:
    """Verify the seed_treatments module can be imported and structured correctly."""

    def test_import_seed_module(self):
        from app.data.seed_treatments import seed_treatments

        assert callable(seed_treatments)

    def test_treatment_data_json_serializable(self):
        """All treatment entries must be JSON-serializable for DB insertion."""
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            d = asdict(entry)
            for key in (
                "aka",
                "symptoms",
                "identification_tips",
                "causes",
                "severity_criteria",
                "treatments",
                "prevention",
                "commonly_confused_with",
            ):
                # Each JSON field should serialize without error
                serialized = json.dumps(d[key])
                assert serialized


# ═══════════════════════════════════════════════════════════════════════
# Diagnosis Prompt
# ═══════════════════════════════════════════════════════════════════════


class TestDiagnosisPrompt:
    """Verify the diagnosis prompt builder works correctly."""

    def test_basic_prompt(self):
        from app.ai.diagnose_routes import _build_diagnosis_prompt

        prompt = _build_diagnosis_prompt()
        assert "Tendril" in prompt
        assert "treatment_id" in prompt
        assert "nitrogen_deficiency" in prompt

    def test_prompt_with_context(self):
        from app.ai.diagnose_routes import _build_diagnosis_prompt

        prompt = _build_diagnosis_prompt(
            grow_type="dwc",
            current_stage="flowering",
            observations="Lower leaves turning yellow",
        )
        assert "Grow method: dwc" in prompt
        assert "Current stage: flowering" in prompt
        assert "Lower leaves turning yellow" in prompt

    def test_prompt_valid_treatment_ids_listed(self):
        """Prompt should list all valid treatment IDs."""
        from app.ai.diagnose_routes import DIAGNOSIS_SYSTEM_PROMPT
        from app.ai.treatment_db import TREATMENT_DATABASE

        for entry in TREATMENT_DATABASE:
            assert entry.id in DIAGNOSIS_SYSTEM_PROMPT, f"{entry.id} not listed in diagnosis prompt"


# ═══════════════════════════════════════════════════════════════════════
# PlantHealthTreatment Model
# ═══════════════════════════════════════════════════════════════════════


class TestPlantHealthTreatmentModel:
    """Verify the SQLAlchemy model is properly defined."""

    def test_model_exists(self):
        from app.grows.models import PlantHealthTreatment

        assert PlantHealthTreatment.__tablename__ == "plant_health_treatments"

    def test_model_columns(self):
        from app.grows.models import PlantHealthTreatment

        cols = {c.name for c in PlantHealthTreatment.__table__.columns}
        expected = {
            "id",
            "category",
            "name",
            "aka",
            "summary",
            "symptoms",
            "identification_tips",
            "causes",
            "severity_criteria",
            "treatments",
            "prevention",
            "recovery_time",
            "commonly_confused_with",
            "created_at",
            "updated_at",
        }
        assert expected.issubset(cols)


# ═══════════════════════════════════════════════════════════════════════
# HealthEval Model Updates
# ═══════════════════════════════════════════════════════════════════════


class TestHealthEvalModel:
    """Verify HealthEval has the new diagnosis fields."""

    def test_new_columns_exist(self):
        from app.grows.models import HealthEval

        cols = {c.name for c in HealthEval.__table__.columns}
        assert "diagnosis_treatment_ids" in cols
        assert "confidence_scores" in cols
        assert "severity" in cols
        assert "model_used" in cols


# ═══════════════════════════════════════════════════════════════════════
# Config
# ═══════════════════════════════════════════════════════════════════════


class TestVisionConfig:
    """Verify the vision model config is present."""

    def test_ollama_vision_model_config(self):
        from app.config import get_settings

        settings = get_settings()
        assert hasattr(settings, "ollama_vision_model")
        assert settings.ollama_vision_model  # not empty

    def test_ollama_vision_model_default(self):
        from app.config import get_settings

        settings = get_settings()
        assert "llava" in settings.ollama_vision_model


# ═══════════════════════════════════════════════════════════════════════
# Ollama Vision Client
# ═══════════════════════════════════════════════════════════════════════


class TestOllamaVisionClient:
    """Verify the vision_diagnose function signature and behavior."""

    def test_vision_diagnose_importable(self):
        from app.ai.ollama import vision_diagnose

        assert callable(vision_diagnose)

    def test_vision_analysis_importable(self):
        from app.ai.ollama import vision_analysis

        assert callable(vision_analysis)
