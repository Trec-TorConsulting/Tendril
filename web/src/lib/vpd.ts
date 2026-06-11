/**
 * VPD (Vapor Pressure Deficit) calculation utilities.
 *
 * VPD measures the "drying power" of air — the difference between how much
 * moisture air can hold at saturation vs. how much it currently holds.
 * Higher VPD = faster transpiration = more nutrient uptake.
 *
 * Cannabis-optimal ranges by stage:
 *   Seedling/Clone: 0.4 - 0.8 kPa
 *   Vegetative:     0.8 - 1.2 kPa
 *   Early Flower:   1.0 - 1.4 kPa
 *   Late Flower:    1.2 - 1.6 kPa
 */

/** VPD zone thresholds by grow stage */
export const VPD_ZONES = {
  seedling: { low: 0.4, optMin: 0.4, optMax: 0.8, high: 1.0, label: "Seedling/Clone" },
  vegetative: { low: 0.6, optMin: 0.8, optMax: 1.2, high: 1.4, label: "Vegetative" },
  early_flower: { low: 0.8, optMin: 1.0, optMax: 1.4, high: 1.6, label: "Early Flower" },
  late_flower: { low: 1.0, optMin: 1.2, optMax: 1.6, high: 1.8, label: "Late Flower" },
} as const;

export type GrowStage = keyof typeof VPD_ZONES;

export interface VpdZone {
  low: number;
  optMin: number;
  optMax: number;
  high: number;
  label: string;
}

export type VpdStatus = "too_low" | "low" | "optimal" | "high" | "too_high";

/**
 * Calculate VPD from temperature and relative humidity.
 *
 * Uses the Tetens formula for saturation vapor pressure:
 *   SVP = 0.6108 × exp(17.27 × T / (T + 237.3))
 *
 * VPD = SVP × (1 - RH/100) adjusted for leaf temperature.
 *
 * @param tempF - Air temperature in Fahrenheit
 * @param humidityPct - Relative humidity (0-100)
 * @param leafOffsetF - Leaf temp offset below ambient (default 2°F / ~1.1°C)
 * @returns VPD in kPa, or null if inputs invalid
 */
export function calculateVpd(
  tempF: number,
  humidityPct: number,
  leafOffsetF: number = 2,
): number | null {
  if (tempF == null || humidityPct == null) return null;
  if (humidityPct < 0 || humidityPct > 100) return null;

  // Convert to Celsius
  const airTempC = (tempF - 32) * (5 / 9);
  const leafTempC = ((tempF - leafOffsetF) - 32) * (5 / 9);

  // Saturation vapor pressure (Tetens formula)
  const svpAir = 0.6108 * Math.exp((17.27 * airTempC) / (airTempC + 237.3));
  const svpLeaf = 0.6108 * Math.exp((17.27 * leafTempC) / (leafTempC + 237.3));

  // Actual vapor pressure
  const avp = svpAir * (humidityPct / 100);

  // VPD = leaf SVP - actual VP
  const vpd = svpLeaf - avp;

  return Math.max(0, Math.round(vpd * 100) / 100);
}

/**
 * Get the VPD status for a given value and grow stage.
 */
export function getVpdStatus(vpd: number, stage: GrowStage): VpdStatus {
  const zone = VPD_ZONES[stage];
  if (vpd < zone.low) return "too_low";
  if (vpd < zone.optMin) return "low";
  if (vpd <= zone.optMax) return "optimal";
  if (vpd <= zone.high) return "high";
  return "too_high";
}

/**
 * Get a human-readable label and color for VPD status.
 */
export function getVpdStatusDisplay(status: VpdStatus): { label: string; color: string } {
  switch (status) {
    case "too_low":
      return { label: "Too Low — risk of mold/edema", color: "#3b82f6" };
    case "low":
      return { label: "Low — slow transpiration", color: "#f59e0b" };
    case "optimal":
      return { label: "Optimal — peak transpiration", color: "#22c55e" };
    case "high":
      return { label: "High — stress risk", color: "#f59e0b" };
    case "too_high":
      return { label: "Too High — stomata closing", color: "#ef4444" };
  }
}

/**
 * Get the zone config for a grow stage, with fallback to vegetative.
 */
export function getVpdZone(stage: string | undefined): VpdZone {
  if (stage && stage in VPD_ZONES) {
    return VPD_ZONES[stage as GrowStage];
  }
  // Map common stage names
  if (stage?.includes("seed") || stage?.includes("clone")) return VPD_ZONES.seedling;
  if (stage?.includes("veg")) return VPD_ZONES.vegetative;
  if (stage?.includes("flower") || stage?.includes("bloom")) {
    if (stage?.includes("late") || stage?.includes("ripen")) return VPD_ZONES.late_flower;
    return VPD_ZONES.early_flower;
  }
  return VPD_ZONES.vegetative;
}

/**
 * Generate zone band data for chart overlays.
 */
export function getVpdChartZones(stage: GrowStage) {
  const zone = VPD_ZONES[stage];
  return [
    { y1: 0, y2: zone.low, color: "#3b82f620", label: "Too Low" },
    { y1: zone.low, y2: zone.optMin, color: "#f59e0b20", label: "Low" },
    { y1: zone.optMin, y2: zone.optMax, color: "#22c55e30", label: "Optimal" },
    { y1: zone.optMax, y2: zone.high, color: "#f59e0b20", label: "High" },
    { y1: zone.high, y2: 2.5, color: "#ef444420", label: "Too High" },
  ];
}
