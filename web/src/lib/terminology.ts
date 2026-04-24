/**
 * Terminology engine — adapts UI labels based on grow type.
 * Outdoor soil uses garden/plant vocabulary instead of indoor hydro terms.
 */

type TermMap = Record<string, string>;

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
  Position: "Pot Location",
  position: "pot location",
  Reservoir: "Media",
  reservoir: "media",
  "No buckets yet": "No pots added yet",
  "Add your first bucket": "Add your first pot",
  "Bucket Details": "Pot Details",
};

const TERM_MAPS: Record<string, TermMap> = {
  outdoor_soil: OUTDOOR_SOIL_TERMS,
  outdoor_container: OUTDOOR_CONTAINER_TERMS,
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
