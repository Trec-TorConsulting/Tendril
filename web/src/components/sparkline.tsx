"use client";

import { Area, AreaChart, ResponsiveContainer } from "recharts";

interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
  className?: string;
}

function getColor(data: number[], ranges?: { min: number; max: number }) {
  if (!ranges || data.length < 2) return "var(--color-primary)";
  const last = data[data.length - 1];
  if (last < ranges.min || last > ranges.max) return "oklch(0.637 0.237 25.331)"; // red
  // Check drift — if std dev > 15% of range, it's drifting
  const mean = data.reduce((a, b) => a + b, 0) / data.length;
  const variance = data.reduce((s, v) => s + (v - mean) ** 2, 0) / data.length;
  const std = Math.sqrt(variance);
  const rangeSize = ranges.max - ranges.min;
  if (std > rangeSize * 0.15) return "oklch(0.795 0.184 86.047)"; // amber/yellow
  return "oklch(0.723 0.219 149.579)"; // green
}

export function Sparkline({ data, color, height = 32, className }: SparklineProps) {
  if (!data || data.length < 2) return null;

  const chartData = data.map((value, i) => ({ i, v: value }));
  const lineColor = color || "var(--color-primary)";

  return (
    <div className={className} style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
          <defs>
            <linearGradient id={`spark-${lineColor.replace(/[^a-z0-9]/gi, "")}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={lineColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="v"
            stroke={lineColor}
            strokeWidth={1.5}
            fill={`url(#spark-${lineColor.replace(/[^a-z0-9]/gi, "")})`}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

/** Sparkline with auto-coloring based on value ranges */
export function SensorSparkline({
  data,
  ranges,
  height = 32,
  className,
}: {
  data: number[];
  ranges?: { min: number; max: number };
  height?: number;
  className?: string;
}) {
  const lineColor = getColor(data, ranges);
  return <Sparkline data={data} color={lineColor} height={height} className={className} />;
}
