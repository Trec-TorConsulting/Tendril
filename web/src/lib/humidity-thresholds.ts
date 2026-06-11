/**
 * Stage-aware humidity thresholds for cannabis grows.
 * Based on cannabis-first research — each stage has different ideal RH ranges.
 */

interface HumidityThreshold {
  min: number;
  max: number;
  status: "optimal" | "warning" | "unknown";
  hint: string | undefined;
}

// Stage-specific humidity ranges (RH %)
const STAGE_HUMIDITY: Record<string, { min: number; max: number; lowHint: string; highHint: string }> = {
  germination: {
    min: 65,
    max: 90,
    lowHint: "Too dry — seedlings need 65–90% RH for germination",
    highHint: "Too humid — damping-off risk above 90%",
  },
  seedling: {
    min: 60,
    max: 80,
    lowHint: "Too dry — target 60–80% RH for seedlings",
    highHint: "Too humid — damping-off risk above 80%",
  },
  vegetative: {
    min: 40,
    max: 70,
    lowHint: "Too dry — target 40–70% in veg",
    highHint: "Too humid — target below 70% in veg",
  },
  flowering: {
    min: 35,
    max: 55,
    lowHint: "Too dry — target 35–55% in flower",
    highHint: "Too humid — botrytis risk above 55% in flower",
  },
  ripening: {
    min: 35,
    max: 50,
    lowHint: "Too dry — target 35–50% in late flower",
    highHint: "Too humid — botrytis risk above 50% in late flower",
  },
  drying: {
    min: 45,
    max: 65,
    lowHint: "Too dry — target 45–65% for drying",
    highHint: "Too humid — mold risk. Target 45–65% for drying",
  },
  curing: {
    min: 55,
    max: 65,
    lowHint: "Too dry — target 55–65% for curing",
    highHint: "Too humid — mold risk. Target 55–65% for curing",
  },
};

// Fallback: generic range if stage is unknown
const DEFAULT_HUMIDITY = {
  min: 40,
  max: 70,
  lowHint: "Too dry — check target for current stage",
  highHint: "Too humid — check target for current stage",
};

/**
 * Returns humidity status and hint based on the grow's current stage.
 */
export function getHumidityThreshold(humidity: number | null | undefined, stage: string | null | undefined): HumidityThreshold {
  if (humidity == null) {
    return { min: 0, max: 100, status: "unknown", hint: undefined };
  }

  const config = (stage && STAGE_HUMIDITY[stage]) || DEFAULT_HUMIDITY;

  const isOptimal = humidity >= config.min && humidity <= config.max;
  const hint = humidity < config.min ? config.lowHint : humidity > config.max ? config.highHint : undefined;

  return {
    min: config.min,
    max: config.max,
    status: isOptimal ? "optimal" : "warning",
    hint,
  };
}
