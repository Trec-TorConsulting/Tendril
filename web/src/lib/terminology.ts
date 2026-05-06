/**
 * Terminology engine — adapts UI labels based on grow type.
 * Each grow type gets vocabulary matching its physical setup.
 */

type TermMap = Record<string, string>;

const DWC_TERMS: TermMap = {
  bucket: "Bucket",
  buckets: "Buckets",
  Bucket: "Bucket",
  Buckets: "Buckets",
  "Add Bucket": "Add Bucket",
  "Add bucket": "Add bucket",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Reservoir",
  reservoir: "reservoir",
  Medium: "Hydroton / Clay pebbles",
  medium: "hydroton / clay pebbles",
  "Bucket Details": "Bucket Details",
};

const RDWC_TERMS: TermMap = {
  bucket: "Site",
  buckets: "Sites",
  Bucket: "Site",
  Buckets: "Sites",
  "Add Bucket": "Add Site",
  "Add bucket": "Add site",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Control Bucket",
  reservoir: "control bucket",
  Medium: "Hydroton / Clay pebbles",
  medium: "hydroton / clay pebbles",
  "No buckets yet": "No sites added yet",
  "Add your first bucket": "Add your first site to the system",
  "Bucket Details": "Site Details",
};

const NFT_TERMS: TermMap = {
  bucket: "Channel",
  buckets: "Channels",
  Bucket: "Channel",
  Buckets: "Channels",
  "Add Bucket": "Add Channel",
  "Add bucket": "Add channel",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Reservoir",
  reservoir: "reservoir",
  Medium: "Rockwool starter cube",
  medium: "rockwool starter cube",
  "No buckets yet": "No channels added yet",
  "Add your first bucket": "Add your first channel",
  "Bucket Details": "Channel Details",
};

const EBB_FLOW_TERMS: TermMap = {
  bucket: "Tray",
  buckets: "Trays",
  Bucket: "Tray",
  Buckets: "Trays",
  "Add Bucket": "Add Tray",
  "Add bucket": "Add tray",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Flood Tray",
  reservoir: "flood tray",
  Medium: "Hydroton / Rockwool / Perlite",
  medium: "hydroton / rockwool / perlite",
  "No buckets yet": "No trays added yet",
  "Add your first bucket": "Add your first tray",
  "Bucket Details": "Tray Details",
};

const DRIP_TERMS: TermMap = {
  bucket: "Pot",
  buckets: "Pots",
  Bucket: "Pot",
  Buckets: "Pots",
  "Add Bucket": "Add Pot",
  "Add bucket": "Add pot",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Reservoir",
  reservoir: "reservoir",
  Medium: "Coco / Rockwool / Perlite",
  medium: "coco / rockwool / perlite",
  "No buckets yet": "No pots added yet",
  "Add your first bucket": "Add your first pot",
  "Bucket Details": "Pot Details",
};

const AEROPONICS_TERMS: TermMap = {
  bucket: "Chamber",
  buckets: "Chambers",
  Bucket: "Chamber",
  Buckets: "Chambers",
  "Add Bucket": "Add Chamber",
  "Add bucket": "Add chamber",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Mist Zone",
  reservoir: "mist zone",
  Medium: "None (bare roots)",
  medium: "none (bare roots)",
  "No buckets yet": "No chambers added yet",
  "Add your first bucket": "Add your first chamber",
  "Bucket Details": "Chamber Details",
};

const KRATKY_TERMS: TermMap = {
  bucket: "Container",
  buckets: "Containers",
  Bucket: "Container",
  Buckets: "Containers",
  "Add Bucket": "Add Container",
  "Add bucket": "Add container",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Nutrient Solution",
  reservoir: "nutrient solution",
  Medium: "Hydroton / Perlite",
  medium: "hydroton / perlite",
  "No buckets yet": "No containers added yet",
  "Add your first bucket": "Add your first container",
  "Bucket Details": "Container Details",
};

const COCO_TERMS: TermMap = {
  bucket: "Pot",
  buckets: "Pots",
  Bucket: "Pot",
  Buckets: "Pots",
  "Add Bucket": "Add Pot",
  "Add bucket": "Add pot",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Media",
  reservoir: "media",
  Medium: "Coco coir",
  medium: "coco coir",
  "No buckets yet": "No pots added yet",
  "Add your first bucket": "Add your first pot",
  "Bucket Details": "Pot Details",
};

const ROCKWOOL_TERMS: TermMap = {
  bucket: "Slab",
  buckets: "Slabs",
  Bucket: "Slab",
  Buckets: "Slabs",
  "Add Bucket": "Add Slab",
  "Add bucket": "Add slab",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Slab",
  reservoir: "slab",
  Medium: "Rockwool",
  medium: "rockwool",
  "No buckets yet": "No slabs added yet",
  "Add your first bucket": "Add your first slab",
  "Bucket Details": "Slab Details",
};

const SOIL_TERMS: TermMap = {
  bucket: "Pot",
  buckets: "Pots",
  Bucket: "Pot",
  Buckets: "Pots",
  "Add Bucket": "Add Pot",
  "Add bucket": "Add pot",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Soil",
  reservoir: "soil",
  Medium: "Soil / Living soil",
  medium: "soil / living soil",
  "No buckets yet": "No pots added yet",
  "Add your first bucket": "Add your first pot",
  "Bucket Details": "Pot Details",
};

const OUTDOOR_SOIL_TERMS: TermMap = {
  bucket: "Plant",
  buckets: "Plants",
  Bucket: "Plant",
  Buckets: "Plants",
  "Add Bucket": "Add Plant",
  "Add bucket": "Add plant",
  tent: "Garden",
  Tent: "Garden",
  tents: "Gardens",
  Tents: "Gardens",
  Position: "Plot Location",
  position: "plot location",
  "Volume (gallons)": "Bed Size (sq ft)",
  Reservoir: "Soil",
  reservoir: "soil",
  Medium: "Native soil / Amended soil",
  medium: "native soil / amended soil",
  "No buckets yet": "No plants added yet",
  "Add your first bucket": "Add your first plant to the garden",
  "Bucket Details": "Plant Details",
};

const OUTDOOR_CONTAINER_TERMS: TermMap = {
  bucket: "Pot",
  buckets: "Pots",
  Bucket: "Pot",
  Buckets: "Pots",
  "Add Bucket": "Add Pot",
  "Add bucket": "Add pot",
  tent: "Patio",
  Tent: "Patio",
  tents: "Patios",
  Tents: "Patios",
  Position: "Pot Location",
  position: "pot location",
  Reservoir: "Media",
  reservoir: "media",
  Medium: "Soil / Coco-perlite",
  medium: "soil / coco-perlite",
  "No buckets yet": "No pots added yet",
  "Add your first bucket": "Add your first pot",
  "Bucket Details": "Pot Details",
};

const AQUAPONICS_TERMS: TermMap = {
  bucket: "Grow Bed",
  buckets: "Grow Beds",
  Bucket: "Grow Bed",
  Buckets: "Grow Beds",
  "Add Bucket": "Add Grow Bed",
  "Add bucket": "Add grow bed",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Fish Tank",
  reservoir: "fish tank",
  Medium: "Expanded clay / Gravel",
  medium: "expanded clay / gravel",
  "No buckets yet": "No grow beds added yet",
  "Add your first bucket": "Add your first grow bed",
  "Bucket Details": "Grow Bed Details",
};

const LIVING_SOIL_TERMS: TermMap = {
  bucket: "Bed",
  buckets: "Beds",
  Bucket: "Bed",
  Buckets: "Beds",
  "Add Bucket": "Add Bed",
  "Add bucket": "Add bed",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Living Soil",
  reservoir: "living soil",
  Medium: "Living soil / Super soil",
  medium: "living soil / super soil",
  "No buckets yet": "No beds added yet",
  "Add your first bucket": "Add your first bed",
  "Bucket Details": "Bed Details",
};

const DUTCH_BUCKET_TERMS: TermMap = {
  bucket: "Bato Bucket",
  buckets: "Bato Buckets",
  Bucket: "Bato Bucket",
  Buckets: "Bato Buckets",
  "Add Bucket": "Add Bato Bucket",
  "Add bucket": "Add bato bucket",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Reservoir",
  reservoir: "reservoir",
  Medium: "Perlite / Hydroton",
  medium: "perlite / hydroton",
  "No buckets yet": "No bato buckets added yet",
  "Add your first bucket": "Add your first bato bucket",
  "Bucket Details": "Bato Bucket Details",
};

const VERTICAL_TOWER_TERMS: TermMap = {
  bucket: "Tower",
  buckets: "Towers",
  Bucket: "Tower",
  Buckets: "Towers",
  "Add Bucket": "Add Tower",
  "Add bucket": "Add tower",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Reservoir",
  reservoir: "reservoir",
  Medium: "Rockwool / Felt / Hydroton",
  medium: "rockwool / felt / hydroton",
  "No buckets yet": "No towers added yet",
  "Add your first bucket": "Add your first tower",
  "Bucket Details": "Tower Details",
};

const WICKING_TERMS: TermMap = {
  bucket: "Wicking Bed",
  buckets: "Wicking Beds",
  Bucket: "Wicking Bed",
  Buckets: "Wicking Beds",
  "Add Bucket": "Add Wicking Bed",
  "Add bucket": "Add wicking bed",
  tent: "Space",
  Tent: "Space",
  tents: "Spaces",
  Tents: "Spaces",
  Reservoir: "Sub-Reservoir",
  reservoir: "sub-reservoir",
  Medium: "Soil-perlite mix",
  medium: "soil-perlite mix",
  "No buckets yet": "No wicking beds added yet",
  "Add your first bucket": "Add your first wicking bed",
  "Bucket Details": "Wicking Bed Details",
};

const TERM_MAPS: Record<string, TermMap> = {
  dwc: DWC_TERMS,
  rdwc: RDWC_TERMS,
  nft: NFT_TERMS,
  ebb_flow: EBB_FLOW_TERMS,
  drip: DRIP_TERMS,
  aeroponics: AEROPONICS_TERMS,
  kratky: KRATKY_TERMS,
  coco: COCO_TERMS,
  rockwool: ROCKWOOL_TERMS,
  soil: SOIL_TERMS,
  outdoor_soil: OUTDOOR_SOIL_TERMS,
  outdoor_container: OUTDOOR_CONTAINER_TERMS,
  aquaponics: AQUAPONICS_TERMS,
  living_soil: LIVING_SOIL_TERMS,
  dutch_bucket: DUTCH_BUCKET_TERMS,
  vertical_tower: VERTICAL_TOWER_TERMS,
  wicking: WICKING_TERMS,
};

/** Return the grow-type-specific label for a term, or the original if no mapping exists. */
export function t(growType: string | undefined | null, term: string): string {
  if (!growType) return term;
  return TERM_MAPS[growType]?.[term] ?? term;
}

/** Check if a grow type is an outdoor type. */
export function isOutdoor(growType: string | undefined | null): boolean {
  return growType === "outdoor_soil" || growType === "outdoor_container";
}

/** Check if a grow type specifically outdoor soil (for plot grid / soil health features). */
export function isOutdoorSoil(growType: string | undefined | null): boolean {
  return growType === "outdoor_soil";
}

/** Check if a grow type is specifically outdoor container. */
export function isOutdoorContainer(growType: string | undefined | null): boolean {
  return growType === "outdoor_container";
}

/** Check if a grow type is an active hydroponic system. */
export function isActiveHydro(growType: string | undefined | null): boolean {
  return (
    growType === "dwc" ||
    growType === "rdwc" ||
    growType === "nft" ||
    growType === "ebb_flow" ||
    growType === "drip" ||
    growType === "aeroponics" ||
    growType === "aquaponics" ||
    growType === "dutch_bucket" ||
    growType === "vertical_tower"
  );
}

/** Check if a grow type is soilless media (coco/rockwool). */
export function isSoilless(growType: string | undefined | null): boolean {
  return growType === "coco" || growType === "rockwool";
}

/** Check if a grow type is traditional soil (indoor or outdoor). */
export function isSoil(growType: string | undefined | null): boolean {
  return (
    growType === "soil" ||
    growType === "outdoor_soil" ||
    growType === "outdoor_container" ||
    growType === "living_soil"
  );
}

/** Check if a grow type is passive hydro. */
export function isPassiveHydro(growType: string | undefined | null): boolean {
  return growType === "kratky" || growType === "wicking";
}
