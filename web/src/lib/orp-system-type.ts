export type OrpSystemType = "live_beneficial" | "sterilized";

export interface OrpRange {
  min: number;
  max: number;
  target: number;
}

export const ORP_RANGES: Record<OrpSystemType, OrpRange> = {
  live_beneficial: {
    min: 200,
    max: 300,
    target: 260,
  },
  sterilized: {
    min: 300,
    max: 450,
    target: 375,
  },
};

export function resolveOrpSystemType(
  value: unknown,
  fallback: OrpSystemType = "sterilized",
): OrpSystemType {
  if (value === "live_beneficial" || value === "sterilized") {
    return value;
  }
  return fallback;
}

export function getOrpRange(systemType: OrpSystemType): OrpRange {
  return ORP_RANGES[systemType];
}
