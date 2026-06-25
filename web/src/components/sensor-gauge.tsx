"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface SensorGaugeProps {
  label: string;
  value: number | null;
  unit: string;
  min: number;
  max: number;
  zones: readonly { start: number; end: number; color: string }[];
  className?: string;
  systemType?: "live_beneficial" | "sterilized";  // For ORP gauge variants
}

export function SensorGauge({ label, value, unit, min, max, zones, className }: SensorGaugeProps) {
  const range = max - min;
  const normalizedValue = value != null ? Math.max(0, Math.min(1, (value - min) / range)) : 0;

  // SVG arc parameters — 240° sweep (from -120° to +120°)
  const startAngle = -120;
  const endAngle = 120;
  const sweepAngle = endAngle - startAngle;
  const radius = 42;
  const cx = 50;
  const cy = 50;

  function polarToCartesian(angle: number) {
    const rad = ((angle - 90) * Math.PI) / 180;
    return {
      x: cx + radius * Math.cos(rad),
      y: cy + radius * Math.sin(rad),
    };
  }

  function describeArc(startA: number, endA: number) {
    const start = polarToCartesian(endA);
    const end = polarToCartesian(startA);
    const largeArc = endA - startA > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 0 ${end.x} ${end.y}`;
  }

  // Current value status
  const currentZone = zones.find((z) => value != null && value >= z.start && value <= z.end);
  const needleAngle = startAngle + normalizedValue * sweepAngle;
  const needleEnd = polarToCartesian(needleAngle);

  return (
    <div className={cn("flex flex-col items-center", className)}>
      <svg viewBox="0 0 100 65" className="w-full max-w-[140px]">
        {/* Background track */}
        <path
          d={describeArc(startAngle, endAngle)}
          fill="none"
          stroke="currentColor"
          strokeWidth={8}
          className="text-muted/40"
          strokeLinecap="round"
        />
        {/* Zone arcs */}
        {zones.map((zone, i) => {
          const zoneStart = startAngle + ((zone.start - min) / range) * sweepAngle;
          const zoneEnd = startAngle + ((zone.end - min) / range) * sweepAngle;
          const clampedStart = Math.max(startAngle, Math.min(endAngle, zoneStart));
          const clampedEnd = Math.max(startAngle, Math.min(endAngle, zoneEnd));
          if (clampedEnd <= clampedStart) return null;
          return (
            <path
              key={i}
              d={describeArc(clampedStart, clampedEnd)}
              fill="none"
              stroke={zone.color}
              strokeWidth={8}
              strokeLinecap="round"
              opacity={0.7}
            />
          );
        })}
        {/* Needle */}
        {value != null && (
          <motion.line
            x1={cx}
            y1={cy}
            x2={needleEnd.x}
            y2={needleEnd.y}
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            className="text-foreground"
            initial={{ x2: cx, y2: cy }}
            animate={{ x2: needleEnd.x, y2: needleEnd.y }}
            transition={{ type: "spring", stiffness: 60, damping: 15 }}
          />
        )}
        {/* Center dot */}
        <circle cx={cx} cy={cy} r={3} className="fill-foreground" />
      </svg>
      {/* Value display */}
      <div className="text-center -mt-1">
        <span className={cn(
          "text-lg font-bold tabular-nums",
          currentZone?.color === "#22c55e" || currentZone?.color === "var(--color-emerald-500)" ? "text-emerald-500" :
          currentZone?.color === "#f59e0b" || currentZone?.color === "var(--color-amber-500)" ? "text-amber-500" :
          currentZone?.color === "#ef4444" || currentZone?.color === "var(--color-red-500)" ? "text-red-500" :
          "text-foreground",
        )}>
          {value != null ? value.toFixed(1) : "—"}
        </span>
        <span className="text-xs text-muted-foreground ml-0.5">{unit}</span>
      </div>
      <span className="text-[11px] text-muted-foreground">{label}</span>
    </div>
  );
}

// Predefined gauge configs for common cannabis sensors
export const GAUGE_PRESETS = {
  ph: {
    label: "pH",
    unit: "",
    min: 4,
    max: 8,
    zones: [
      { start: 4, end: 5.4, color: "#ef4444" },    // red — too acidic
      { start: 5.4, end: 5.8, color: "#f59e0b" },   // amber — low
      { start: 5.8, end: 6.2, color: "#22c55e" },   // green — optimal
      { start: 6.2, end: 6.6, color: "#f59e0b" },   // amber — high
      { start: 6.6, end: 8, color: "#ef4444" },     // red — too alkaline
    ],
  },
  ec: {
    label: "EC",
    unit: "mS",
    min: 0,
    max: 3.5,
    zones: [
      { start: 0, end: 0.6, color: "#f59e0b" },     // amber — too low
      { start: 0.6, end: 2.2, color: "#22c55e" },   // green — optimal
      { start: 2.2, end: 2.8, color: "#f59e0b" },   // amber — high
      { start: 2.8, end: 3.5, color: "#ef4444" },   // red — burning
    ],
  },
  temp: {
    label: "Temp",
    unit: "°F",
    min: 55,
    max: 95,
    zones: [
      { start: 55, end: 65, color: "#3b82f6" },     // blue — too cold
      { start: 65, end: 68, color: "#f59e0b" },     // amber — cool
      { start: 68, end: 82, color: "#22c55e" },     // green — optimal
      { start: 82, end: 88, color: "#f59e0b" },     // amber — warm
      { start: 88, end: 95, color: "#ef4444" },     // red — too hot
    ],
  },
  humidity: {
    label: "RH",
    unit: "%",
    min: 20,
    max: 90,
    zones: [
      { start: 20, end: 35, color: "#f59e0b" },     // amber — too dry
      { start: 35, end: 60, color: "#22c55e" },     // green — optimal (flower)
      { start: 60, end: 75, color: "#f59e0b" },     // amber — high
      { start: 75, end: 90, color: "#ef4444" },     // red — mold risk
    ],
  },
  vpd: {
    label: "VPD",
    unit: "kPa",
    min: 0,
    max: 2.5,
    zones: [
      { start: 0, end: 0.4, color: "#3b82f6" },     // blue — low transpiration
      { start: 0.4, end: 0.8, color: "#f59e0b" },   // amber — seedling zone
      { start: 0.8, end: 1.4, color: "#22c55e" },   // green — sweet spot
      { start: 1.4, end: 1.8, color: "#f59e0b" },   // amber — high
      { start: 1.8, end: 2.5, color: "#ef4444" },   // red — stress
    ],
  },
  waterTemp: {
    label: "Water",
    unit: "°F",
    min: 55,
    max: 80,
    zones: [
      { start: 55, end: 62, color: "#3b82f6" },     // blue — too cold
      { start: 62, end: 70, color: "#22c55e" },     // green — optimal
      { start: 70, end: 74, color: "#f59e0b" },     // amber — warm
      { start: 74, end: 80, color: "#ef4444" },     // red — root rot risk
    ],
  },
  orp: {
    label: "ORP",
    unit: "mV",
    min: 0,
    max: 600,
    zones: [
      // Default (sterilized system H2O2) — zones defined dynamically by getOrpZones()
      { start: 0, end: 200, color: "#ef4444" },     // red — anaerobic / root rot risk
      { start: 200, end: 300, color: "#f59e0b" },   // amber — low oxidation
      { start: 300, end: 450, color: "#22c55e" },   // green — optimal (sterilized)
      { start: 450, end: 500, color: "#f59e0b" },   // amber — high (H2O2 excess)
      { start: 500, end: 600, color: "#ef4444" },   // red — too oxidizing
    ],
  },
} as const;

/**
 * Get ORP gauge zones based on system type (Live/Beneficial vs Sterilized).
 * Call this when rendering an ORP gauge to get the correct zones for the system type.
 */
export function getOrpZones(systemType: "live_beneficial" | "sterilized" = "sterilized") {
  if (systemType === "live_beneficial") {
    // Live system with Hydroguard/beneficial bacteria: lower ORP range 150-250
    return [
      { start: 0, end: 100, color: "#ef4444" },      // red — too anaerobic / too low
      { start: 100, end: 150, color: "#f59e0b" },    // amber — slightly low
      { start: 150, end: 250, color: "#22c55e" },    // green — optimal (beneficial system)
      { start: 250, end: 350, color: "#f59e0b" },    // amber — slightly high
      { start: 350, end: 600, color: "#ef4444" },    // red — too oxidizing for beneficial
    ] as const;
  } else {
    // Sterilized system with H2O2: higher ORP range 300-450
    return [
      { start: 0, end: 200, color: "#ef4444" },      // red — anaerobic / root rot risk
      { start: 200, end: 300, color: "#f59e0b" },    // amber — low oxidation
      { start: 300, end: 450, color: "#22c55e" },    // green — optimal (sterilized)
      { start: 450, end: 500, color: "#f59e0b" },    // amber — high (H2O2 excess)
      { start: 500, end: 600, color: "#ef4444" },    // red — too oxidizing
    ] as const;
  }
}
