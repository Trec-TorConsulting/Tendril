import {
  Activity,
  Beaker,
  Droplets,
  FlaskConical,
  Gauge,
  Thermometer,
  Waves,
  Wind,
  Zap,
  type LucideIcon,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type MetricStatus = "optimal" | "warning" | "critical" | "unknown";

/** tier controls which personas see the metric: 1 = everyone, 2 = home/standard+, 3 = pro/commercial only */
export interface PreviewMetric {
  key: string;
  label: string;
  value: string;
  status: MetricStatus;
  hint?: string;
  trend?: number[];
  ranges?: { min: number; max: number };
  icon: LucideIcon;
  tier: 1 | 2 | 3;
}

export interface PreviewTask {
  id: string;
  title: string;
  detail?: string;
  priority: "urgent" | "high" | "normal";
}

export interface PreviewCamera {
  id: string;
  label: string;
  status: "live" | "offline";
}

export interface FleetGrow {
  id: string;
  name: string;
  stage: string;
  health: number;
  alert: boolean;
}

export interface AttentionItem {
  id: string;
  title: string;
  detail: string;
  cta: string;
  tone: "critical" | "warning";
}

export interface PreviewGrow {
  name: string;
  strain: string;
  stage: string;
  dayInStage: number;
  cycleDay: number;
  cycleTotal: number;
  harvestInDays: number | null;
  healthScore: number | null;
}

export interface ClimatePoint {
  time: string;
  temperature: number | null;
  humidity: number | null;
  water_temp: number | null;
  ph: number | null;
  ppm: number | null;
}

export interface PreviewData {
  grow: PreviewGrow;
  metrics: PreviewMetric[];
  climate: ClimatePoint[];
  tasks: PreviewTask[];
  cameras: PreviewCamera[];
  fleet: FleetGrow[];
  attention: AttentionItem[];
  aiTip: string;
}

// ─── Deterministic series (no Math.random → no hydration mismatch) ──────────────

function noise(i: number): number {
  const x = Math.sin(i * 12.9898) * 43758.5453;
  return (x - Math.floor(x)) * 2 - 1;
}

function series(base: number, amp: number, driftEnd = 0, n = 24, decimals = 1): number[] {
  return Array.from({ length: n }, (_, i) => {
    const t = i / (n - 1);
    const v = base + Math.sin(i / 2.2) * amp * 0.6 + noise(i) * amp * 0.35 + driftEnd * t;
    return Number(v.toFixed(decimals));
  });
}

const tempArr = series(76, 3);
const humArr = series(54, 5);
const phArr = series(6.05, 0.12, 0.35, 24, 2);
const ppmArr = series(820, 40, 0, 24, 0);
const waterTempArr = series(66, 2);
const vpdArr = series(1.1, 0.12, 0, 24, 2);
const waterLevelArr = series(78, 8, -6, 24, 0);
const ecArr = series(1.6, 0.15, 0, 24, 2);
const orpArr = series(380, 25, 0, 24, 0);

const climate: ClimatePoint[] = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, "0")}:00`,
  temperature: tempArr[i],
  humidity: humArr[i],
  water_temp: waterTempArr[i],
  ph: phArr[i],
  ppm: ppmArr[i],
}));

// ─── Mock dataset (illustrative — a mid-flower photoperiod grow) ─────────────────

export const PREVIEW_DATA: PreviewData = {
  grow: {
    name: "Blue Dream",
    strain: "Blue Dream · Photoperiod",
    stage: "Flowering",
    dayInStage: 46,
    cycleDay: 88,
    cycleTotal: 106,
    harvestInDays: 18,
    healthScore: 82,
  },
  metrics: [
    { key: "temp", label: "Tent Temp", value: "76°F", status: "optimal", tier: 1, icon: Thermometer, trend: tempArr, ranges: { min: 68, max: 82 } },
    { key: "humidity", label: "Humidity", value: "55%", status: "optimal", tier: 1, icon: Droplets, trend: humArr, ranges: { min: 40, max: 60 } },
    { key: "ph", label: "pH", value: "6.4", status: "warning", tier: 1, icon: FlaskConical, trend: phArr, ranges: { min: 5.5, max: 6.2 }, hint: "Drifting high — target 5.8–6.2 in flower" },
    { key: "ppm", label: "PPM", value: "820", status: "optimal", tier: 1, icon: Beaker, trend: ppmArr, ranges: { min: 400, max: 1500 } },
    { key: "water_temp", label: "Water Temp", value: "66°F", status: "optimal", tier: 2, icon: Waves, trend: waterTempArr, ranges: { min: 62, max: 70 } },
    { key: "vpd", label: "VPD", value: "1.1 kPa", status: "optimal", tier: 2, icon: Gauge, trend: vpdArr, ranges: { min: 0.8, max: 1.5 } },
    { key: "water_level", label: "Water Level", value: "72%", status: "optimal", tier: 2, icon: Waves, trend: waterLevelArr, ranges: { min: 20, max: 100 } },
    { key: "ec", label: "EC", value: "1.6", status: "optimal", tier: 3, icon: Zap, trend: ecArr, ranges: { min: 0.8, max: 2.5 } },
    { key: "orp", label: "ORP", value: "380 mV", status: "optimal", tier: 3, icon: Activity, trend: orpArr, ranges: { min: 300, max: 450 } },
    { key: "co2", label: "CO₂", value: "—", status: "unknown", tier: 3, icon: Wind },
  ],
  climate,
  tasks: [
    { id: "t1", title: "Adjust reservoir pH", detail: "pH is 6.4 — dose pH-down to reach ~6.0", priority: "high" },
    { id: "t2", title: "Defoliate lower fan leaves", detail: "Improve airflow entering week 7 of flower", priority: "normal" },
    { id: "t3", title: "Log today's readings", detail: "Keeps AI trend analysis accurate", priority: "normal" },
    { id: "t4", title: "Check trichomes", detail: "Cloudy/amber ratio for harvest timing", priority: "normal" },
  ],
  cameras: [
    { id: "c1", label: "Canopy — Tent A", status: "live" },
    { id: "c2", label: "Reservoir Cam", status: "live" },
  ],
  fleet: [
    { id: "g1", name: "Blue Dream", stage: "Flower", health: 82, alert: true },
    { id: "g2", name: "Gelato #33", stage: "Flower", health: 71, alert: true },
    { id: "g3", name: "Veg Tent A", stage: "Veg", health: 90, alert: false },
    { id: "g4", name: "Wedding Cake", stage: "Late Flower", health: 64, alert: false },
    { id: "g5", name: "Mother Room", stage: "Veg", health: 95, alert: false },
  ],
  attention: [
    {
      id: "a1",
      title: "pH climbing out of range",
      detail: "Reservoir pH reached 6.4 — nutrient lockout risk in flower.",
      cta: "Fix now",
      tone: "warning",
    },
  ],
  aiTip:
    "Your pH has climbed toward 6.5 over the last 8 hours. In flower, hold it at 5.8–6.2 for peak phosphorus and potassium uptake. A small pH-down dose to the reservoir should bring it back into range within an hour.",
};

// ─── Persona helpers ─────────────────────────────────────────────────────────

export type Density = "relaxed" | "normal" | "compact";

/** How many metric tiers each density surfaces. */
export const MAX_TIER: Record<Density, 1 | 2 | 3> = {
  relaxed: 1,
  normal: 2,
  compact: 3,
};

export function metricsForDensity(metrics: PreviewMetric[], density: Density): PreviewMetric[] {
  const max = MAX_TIER[density];
  return metrics.filter((m) => m.tier <= max);
}
