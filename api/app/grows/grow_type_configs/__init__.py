"""Grow type stage configurations — per-type A-to-Z grow guides.

Each config module exports a STAGES list and optional metadata.
"""
from __future__ import annotations

from app.grows.grow_type_configs.dwc import DWC_CONFIG
from app.grows.grow_type_configs.kratky import KRATKY_CONFIG

# Registry: grow_type_id → full config dict
GROW_TYPE_CONFIGS: dict[str, dict] = {
    "dwc": DWC_CONFIG,
    "kratky": KRATKY_CONFIG,
}


def get_grow_type_config(grow_type_id: str) -> dict | None:
    return GROW_TYPE_CONFIGS.get(grow_type_id)
