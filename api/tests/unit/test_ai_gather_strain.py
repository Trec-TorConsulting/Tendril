"""Strain-library resolution in AI data gathering.

Verifies the strain library is the source of truth for strain facts fed to AI
prompts: a bucket's strain profile is resolved from the tenant/global strain
library first, then from the global reference-strain database — even when the
bucket only carries a free-text ``strain_name`` with no explicit link.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.ai.gather import gather_grow_data
from app.grows.models import Bucket, GrowCycle, ReferenceStrain, Strain, Tent
from app.reference.strain_sync import SEED_STRAINS

pytestmark = pytest.mark.asyncio(loop_scope="session")

# Full field set every curated strain must carry (last_verified is applied by the sync writer).
_REQUIRED_KEYS = {
    "name",
    "breeder",
    "genetics",
    "strain_type",
    "indica_pct",
    "sativa_pct",
    "thc_pct",
    "thc_min",
    "thc_max",
    "cbd_pct",
    "cbd_min",
    "cbd_max",
    "terpenes",
    "effects",
    "flavors",
    "flowering_min_weeks",
    "flowering_max_weeks",
    "yield_indoor",
    "yield_outdoor",
    "description",
    "sources",
}


async def test_seed_library_entries_are_complete():
    """Every curated strain carries a complete, self-consistent, sourced profile."""
    assert len(SEED_STRAINS) >= 21
    for entry in SEED_STRAINS:
        missing = _REQUIRED_KEYS - entry.keys()
        assert not missing, f"{entry.get('name')} missing {missing}"
        assert entry["indica_pct"] + entry["sativa_pct"] == 100, entry["name"]
        assert entry["thc_min"] <= entry["thc_pct"] <= entry["thc_max"], entry["name"]
        assert entry["cbd_min"] <= entry["cbd_pct"] <= entry["cbd_max"], entry["name"]
        assert entry["flowering_min_weeks"] <= entry["flowering_max_weeks"], entry["name"]
        assert entry["terpenes"] and entry["effects"] and entry["flavors"], entry["name"]
        assert entry["sources"], entry["name"]


async def test_citrus_mistress_in_seed_library():
    """Citrus Mistress is present with correct, sourced lineage data."""
    by_name = {s["name"]: s for s in SEED_STRAINS}
    assert "Citrus Mistress" in by_name
    entry = by_name["Citrus Mistress"]
    assert entry["genetics"] == "Haze x Skunk #1 x Northern Lights #5"
    assert entry["strain_type"] == "Sativa-dominant hybrid"
    assert entry["sativa_pct"] == 90
    assert (entry["thc_min"], entry["thc_max"]) == (20.0, 26.0)
    assert "citrus" in entry["flavors"]
    assert "AllBud" in entry["sources"]


@pytest_asyncio.fixture
async def grow_with_bucket(db_session, db_tenant):
    """A grow with a single bucket whose strain is free-text only (no link)."""
    tenant = db_tenant["tenant"]
    tent = Tent(tenant_id=tenant.id, name="T1")
    db_session.add(tent)
    await db_session.flush()
    grow = GrowCycle(tenant_id=tenant.id, tent_id=tent.id, name="G1", grow_type="dwc")
    db_session.add(grow)
    await db_session.flush()
    bucket = Bucket(tenant_id=tenant.id, grow_cycle_id=grow.id, position=1, strain_name="Citrus Mistress")
    db_session.add(bucket)
    await db_session.commit()
    return grow


async def test_gather_resolves_reference_strain_by_name(db_session, grow_with_bucket):
    """Free-text strain_name resolves to the full global reference-library profile."""
    db_session.add(
        ReferenceStrain(
            name="Citrus Mistress",
            breeder="Unknown",
            genetics="Haze x Skunk #1 x Northern Lights #5",
            strain_type="Sativa-dominant hybrid",
            indica_pct=10,
            sativa_pct=90,
            thc_pct=23.0,
            thc_min=20.0,
            thc_max=26.0,
            cbd_pct=0.2,
            cbd_min=0.0,
            cbd_max=1.0,
            terpenes=["terpinolene", "limonene", "caryophyllene"],
            effects=["energetic", "euphoric"],
            flavors=["citrus", "sour", "spicy"],
            flowering_min_weeks=10.0,
            flowering_max_weeks=11.0,
            yield_indoor="~450 g/m²",
            yield_outdoor="~550 g/plant",
            description="Sativa-dominant hybrid.",
            sources=["AllBud"],
            external_id="seed:citrus-mistress",
        )
    )
    await db_session.commit()

    data = await gather_grow_data(db_session, grow_with_bucket, include_camera=False)

    buckets = data["buckets"]
    assert len(buckets) == 1
    sp = buckets[0]["strain_profile"]
    assert sp["genetics"] == "Haze x Skunk #1 x Northern Lights #5"
    assert sp["strain_type"] == "Sativa-dominant hybrid"
    assert (sp["thc_min"], sp["thc_max"]) == (20.0, 26.0)
    assert sp["terpenes"] == ["terpinolene", "limonene", "caryophyllene"]
    assert sp["effects"] == ["energetic", "euphoric"]
    assert sp["flavors"] == ["citrus", "sour", "spicy"]
    assert sp["flowering_min_weeks"] == 10.0
    assert sp["yield_indoor"] == "~450 g/m²"
    assert sp["sources"] == ["AllBud"]
    assert sp["notes"] == "Sativa-dominant hybrid."
    assert sp["breeder"] == "Unknown"


async def test_gather_prefers_strain_library_over_reference(db_session, grow_with_bucket):
    """The tenant/global strain library takes priority over the reference DB."""
    db_session.add(
        Strain(
            tenant_id=None,
            name="Citrus Mistress",
            genetics="Library genetics",
            flowering_days=70,
            thc_pct=24.0,
        )
    )
    db_session.add(
        ReferenceStrain(
            name="Citrus Mistress",
            genetics="Reference genetics",
            external_id="seed:citrus-mistress",
        )
    )
    await db_session.commit()

    data = await gather_grow_data(db_session, grow_with_bucket, include_camera=False)

    sp = data["buckets"][0]["strain_profile"]
    assert sp["genetics"] == "Library genetics"
    assert sp["flowering_days"] == 70


async def test_gather_omits_profile_for_unknown_strain(db_session, grow_with_bucket):
    """Unknown strains yield no profile (nothing to fabricate)."""
    data = await gather_grow_data(db_session, grow_with_bucket, include_camera=False)
    assert "strain_profile" not in data["buckets"][0]


async def test_sync_seed_strains_persists_rich_profile(db_session):
    """The seed sync writes the full profile + provenance to reference_strains."""
    from app.reference.strain_sync import LAST_VERIFIED, sync_seed_strains

    await sync_seed_strains(db_session)

    row = (
        await db_session.execute(select(ReferenceStrain).where(ReferenceStrain.name == "Citrus Mistress"))
    ).scalar_one()
    assert row.strain_type == "Sativa-dominant hybrid"
    assert (row.thc_min, row.thc_max) == (20.0, 26.0)
    assert row.terpenes and row.effects and row.flavors
    assert row.sources == ["AllBud"]
    assert row.last_verified == LAST_VERIFIED


async def test_prompt_renders_ranges_terpenes_and_sources():
    """The AI renderer surfaces ranges, terpenes, flowering, yield, and provenance."""
    from app.ai.context import _fmt_strain_profile

    text = _fmt_strain_profile(
        {
            "strain_type": "Sativa-dominant hybrid",
            "thc_pct": 23.0,
            "thc_min": 20.0,
            "thc_max": 26.0,
            "terpenes": ["terpinolene", "limonene"],
            "effects": ["energetic"],
            "flavors": ["citrus"],
            "flowering_min_weeks": 10.0,
            "flowering_max_weeks": 11.0,
            "yield_indoor": "~450 g/m²",
            "sources": ["AllBud"],
        }
    )
    assert "Type: Sativa-dominant hybrid" in text
    assert "THC: ~23.0% (typical range" in text
    assert "Terpenes: terpinolene, limonene" in text
    assert "Effects: energetic" in text
    assert "Flavors: citrus" in text
    assert "Flowering:" in text and "weeks" in text
    assert "Yield: indoor ~450 g/m²" in text
    assert "Sources: AllBud" in text


async def test_library_directive_includes_accuracy_caveat():
    """The source-of-truth directive carries the honest variability caveat."""
    from app.ai.context import STRAIN_LIBRARY_DIRECTIVE
    from app.reference.strain_sync import STRAIN_DATA_CAVEAT

    assert STRAIN_DATA_CAVEAT in STRAIN_LIBRARY_DIRECTIVE
