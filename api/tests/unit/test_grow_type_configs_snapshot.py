"""Snapshot test for grow-type configs.

Locks in the fully-merged config structure (including enhancements) for
every registered grow type. Any change to the configs — refactor or
otherwise — must either produce byte-identical output or update the
committed snapshot deliberately.

Snapshot file: ``api/tests/snapshots/grow_type_configs.json``

To regenerate snapshots intentionally (after a real behavior change):
    pytest tests/unit/test_grow_type_configs_snapshot.py --snapshot-update
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import pytest_asyncio

from app.grows.grow_type_configs import GROW_TYPE_CONFIGS

SNAPSHOT_PATH = Path(__file__).parent.parent / "snapshots" / "grow_type_configs.json"


# Override the autouse DB-cleaning fixture from conftest — these are pure
# unit tests that don't touch the DB.
@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    yield


def _normalize(obj):
    """Recursively normalize dict ordering for stable hashing."""
    if isinstance(obj, dict):
        return {k: _normalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [_normalize(x) for x in obj]
    if isinstance(obj, tuple):
        return [_normalize(x) for x in obj]
    return obj


def _serialize_configs() -> str:
    # Trailing newline keeps end-of-file-fixer pre-commit hook happy.
    return json.dumps(_normalize(GROW_TYPE_CONFIGS), indent=2, default=str, sort_keys=False) + "\n"


def pytest_addoption(parser):
    # No-op — pytest plugin hook is only respected from conftest, but
    # declaring locally documents the intent. Actual --snapshot-update is
    # handled via env var below to avoid plugin-registration complexity.
    pass


def test_grow_type_configs_snapshot(monkeypatch):
    """Fail if any grow-type config has drifted from the committed snapshot."""
    current = _serialize_configs()

    import os

    if os.environ.get("SNAPSHOT_UPDATE") == "1":
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(current)
        pytest.skip("Snapshot updated (SNAPSHOT_UPDATE=1)")

    if not SNAPSHOT_PATH.exists():
        SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(current)
        pytest.fail(
            f"No snapshot existed at {SNAPSHOT_PATH}. One has been written; review the diff and commit it, then re-run."
        )

    expected = SNAPSHOT_PATH.read_text()
    if current != expected:
        # Write the new output to a sibling file so developers can diff.
        actual_path = SNAPSHOT_PATH.with_suffix(".actual.json")
        actual_path.write_text(current)
        pytest.fail(
            f"Grow-type configs drifted from snapshot.\n"
            f"  Expected: {SNAPSHOT_PATH}\n"
            f"  Actual:   {actual_path}\n"
            f"Diff with: diff -u {SNAPSHOT_PATH} {actual_path}\n"
            f"If the change is intentional, regenerate with "
            f"SNAPSHOT_UPDATE=1 pytest {Path(__file__).name}"
        )


def test_all_grow_types_registered():
    """Lock in the set of supported grow types so accidental removal fails."""
    expected = {
        "aeroponics",
        "aquaponics",
        "coco",
        "drip",
        "dutch_bucket",
        "dwc",
        "ebb_flow",
        "kratky",
        "living_soil",
        "nft",
        "outdoor_container",
        "outdoor_soil",
        "rdwc",
        "rockwool",
        "soil",
        "vertical_tower",
        "wicking",
    }
    assert set(GROW_TYPE_CONFIGS.keys()) == expected
