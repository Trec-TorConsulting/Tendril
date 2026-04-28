"""Grow type stage configurations — per-type A-to-Z grow guides.

Each config module exports a STAGES list and optional metadata.
"""

from __future__ import annotations

from app.grows.grow_type_configs.aeroponics import AERO_CONFIG
from app.grows.grow_type_configs.coco import COCO_CONFIG
from app.grows.grow_type_configs.drip import DRIP_CONFIG
from app.grows.grow_type_configs.dwc import DWC_CONFIG
from app.grows.grow_type_configs.ebb_flow import EBB_FLOW_CONFIG
from app.grows.grow_type_configs.kratky import KRATKY_CONFIG
from app.grows.grow_type_configs.nft import NFT_CONFIG
from app.grows.grow_type_configs.outdoor_container import OUTDOOR_CONTAINER_CONFIG
from app.grows.grow_type_configs.outdoor_soil import OUTDOOR_SOIL_CONFIG
from app.grows.grow_type_configs.rdwc import RDWC_CONFIG
from app.grows.grow_type_configs.rockwool import ROCKWOOL_CONFIG
from app.grows.grow_type_configs.soil import SOIL_CONFIG

# Registry: grow_type_id → full config dict
GROW_TYPE_CONFIGS: dict[str, dict] = {
    "aeroponics": AERO_CONFIG,
    "coco": COCO_CONFIG,
    "drip": DRIP_CONFIG,
    "dwc": DWC_CONFIG,
    "ebb_flow": EBB_FLOW_CONFIG,
    "kratky": KRATKY_CONFIG,
    "nft": NFT_CONFIG,
    "outdoor_container": OUTDOOR_CONTAINER_CONFIG,
    "outdoor_soil": OUTDOOR_SOIL_CONFIG,
    "rdwc": RDWC_CONFIG,
    "rockwool": ROCKWOOL_CONFIG,
    "soil": SOIL_CONFIG,
}


def get_grow_type_config(grow_type_id: str) -> dict | None:
    return GROW_TYPE_CONFIGS.get(grow_type_id)
