"use client";

import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  Beaker,
  CalendarIcon,
  CheckCircle2,
  Droplets,
  FlaskConical,
  Thermometer,
  TrendingUp,
  Waves,
  Wrench,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn, formatCalendarDate } from "@/lib/utils";
import { formatTemp } from "@/lib/units";
import { getHumidityThreshold } from "@/lib/humidity-thresholds";
import type { TaskItem } from "@/lib/api";
import { CameraGrid } from "@/components/camera-grid";
import { DashboardAiInsights } from "@/components/dashboard-ai-insights";
import { NextBestAction } from "@/components/next-best-action";
import {
  HarvestTile,
  HealthTile,
  HeroBanner,
  MetricTile,
  StatChip,
  TrendChart,
} from "@/components/dashboard-preview/preview-parts";
import {
  metricsForDensity,
  type ClimatePoint,
  type Density,
  type PreviewGrow,
  type PreviewMetric,
} from "@/components/dashboard-preview/preview-data";

// ─── Metric derivation ──────────────────────────────────────────────────────────

type SensorTrends = Record<
  "ph" | "ec" | "ppm" | "water_temp" | "water_level" | "orp" | "temp" | "humidity",
  number[]
>;

const lastOf = (a: number[]): number | null => (a.length ? a[a.length - 1] : null);

/** Build the persona-agnostic metric list from live sensor trends. */
export function buildDashboardMetrics({
  trends,
  isHydro,
  stage,
  tempUnit,
}: {
  trends: SensorTrends;
  isHydro: boolean;
  stage?: string;
  tempUnit: "fahrenheit" | "celsius";
}): PreviewMetric[] {
  const temp = lastOf(trends.temp);
  const hum = lastOf(trends.humidity);
  const ph = lastOf(trends.ph);
  const ppm = lastOf(trends.ppm);
  const wtemp = lastOf(trends.water_temp);
  const wlevel = lastOf(trends.water_level);
  const ec = lastOf(trends.ec);
  const orp = lastOf(trends.orp);
  const humT = getHumidityThreshold(hum, stage);

  const metrics: PreviewMetric[] = [
    {
      key: "temp", label: "Tent Temp", icon: Thermometer, tier: 1, trend: trends.temp, ranges: { min: 68, max: 82 },
      value: temp != null ? formatTemp(temp, "f", tempUnit, 0) : "—",
      status: temp == null ? "unknown" : temp >= 68 && temp <= 82 ? "optimal" : "warning",
      hint: temp != null && temp < 68 ? "Too cold — target 68–82°F" : temp != null && temp > 82 ? "Too hot — target 68–82°F" : undefined,
    },
    {
      key: "humidity", label: "Humidity", icon: Droplets, tier: 1, trend: trends.humidity, ranges: { min: 40, max: 60 },
      value: hum != null ? `${hum.toFixed(0)}%` : "—",
      status: humT.status === "optimal" ? "optimal" : humT.status === "warning" ? "warning" : "unknown",
      hint: humT.hint,
    },
    {
      key: "ph", label: "pH", icon: FlaskConical, tier: 1, trend: trends.ph,
      ranges: isHydro ? { min: 5.5, max: 6.2 } : { min: 6.0, max: 7.0 },
      value: ph != null ? ph.toFixed(1) : "—",
      status: ph == null ? "unknown" : isHydro ? (ph >= 5.5 && ph <= 6.2 ? "optimal" : "warning") : (ph >= 6.0 && ph <= 7.0 ? "optimal" : "warning"),
      hint: ph != null && ph < (isHydro ? 5.5 : 6.0) ? "Too acidic" : ph != null && ph > (isHydro ? 6.2 : 7.0) ? "Too alkaline" : undefined,
    },
  ];

  if (isHydro) {
    metrics.push(
      {
        key: "ppm", label: "PPM", icon: Beaker, tier: 1, trend: trends.ppm, ranges: { min: 400, max: 1500 },
        value: ppm != null ? `${Math.round(ppm)}` : "—",
        status: ppm == null ? "unknown" : ppm >= 400 && ppm <= 1500 ? "optimal" : "warning",
        hint: ppm != null && ppm < 400 ? "Nutrients low — target 400–1500" : ppm != null && ppm > 1500 ? "Nutrients high — target 400–1500" : undefined,
      },
      {
        key: "water_temp", label: "Water Temp", icon: Waves, tier: 2, trend: trends.water_temp, ranges: { min: 62, max: 70 },
        value: wtemp != null ? formatTemp(wtemp, "f", tempUnit, 0) : "—",
        status: wtemp == null ? "unknown" : wtemp >= 62 && wtemp <= 70 ? "optimal" : "warning",
        hint: wtemp != null && wtemp > 72 ? "Root-rot risk above 72°F — target 64–70°F" : undefined,
      },
      {
        key: "water_level", label: "Water Level", icon: Waves, tier: 2, trend: trends.water_level, ranges: { min: 20, max: 100 },
        value: wlevel != null ? `${Math.round(wlevel)}%` : "—",
        status: wlevel == null ? "unknown" : wlevel >= 20 ? "optimal" : "warning",
        hint: wlevel != null && wlevel < 20 ? "Reservoir low — refill soon" : undefined,
      },
      {
        key: "ec", label: "EC", icon: Zap, tier: 3, trend: trends.ec, ranges: { min: 0.8, max: 2.5 },
        value: ec != null ? ec.toFixed(2) : "—",
        status: ec == null ? "unknown" : ec >= 0.8 && ec <= 2.5 ? "optimal" : "warning",
        hint: ec != null && ec > 2.5 ? "Nutrient-burn risk — target 0.8–2.5" : undefined,
      },
    );
    if (orp != null) {
      metrics.push({
        key: "orp", label: "ORP", icon: Activity, tier: 3, trend: trends.orp, ranges: { min: 300, max: 450 },
        value: `${Math.round(orp)} mV`,
        status: orp >= 300 && orp <= 450 ? "optimal" : "warning",
        hint: orp < 300 ? "Anaerobic risk — target 300–450 mV" : orp > 450 ? "Too oxidizing — target 300–450 mV" : undefined,
      });
    }
  }

  return metrics;
}

// ─── Shared props ────────────────────────────────────────────────────────────────

export interface AdaptiveDashboardProps {
  grow: PreviewGrow;
  metrics: PreviewMetric[];
  climate: ClimatePoint[];
  tasks: TaskItem[];
  onCompleteTask: (id: string) => void;
  growId: string;
  growStage?: string;
  tentId: string;
  hasSensorData: boolean;
  sensorTrends: Record<string, number[]>;
  healthScore: number | null;
  density: Density;
}

// ─── Interactive tasks panel ─────────────────────────────────────────────────────

function TasksPanel({
  tasks,
  onComplete,
  density,
}: {
  tasks: TaskItem[];
  onComplete: (id: string) => void;
  density: Density;
}) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <CheckCircle2 className="size-4 text-primary" />
            Tasks
          </CardTitle>
          <Button variant="ghost" size="sm" className="text-xs text-muted-foreground" render={<Link href="/dashboard/tasks" />}>
            View all
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {tasks.length === 0 && (
          <p className="py-4 text-center text-sm text-muted-foreground">No issues detected. Your grow is on track.</p>
        )}
        {tasks.map((task) => {
          const isAlert = task.category === "alert_response";
          const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "completed";
          return (
            <div
              key={task.id}
              className={cn(
                "flex items-start gap-3 rounded-lg border p-3",
                isAlert ? "border-red-500/60 bg-red-500/5" : "border-amber-500/40 bg-amber-500/5",
              )}
            >
              <button
                onClick={() => onComplete(task.id)}
                className={cn(
                  "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition",
                  isAlert ? "border-red-500/60 hover:bg-red-500/10" : "border-amber-500/60 hover:bg-amber-500/10",
                )}
                aria-label={`Complete task: ${task.title}`}
              >
                <CheckCircle2 className="size-3 text-transparent" />
              </button>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-1.5">
                  {isAlert ? <AlertTriangle className="size-3.5 shrink-0 text-red-500" /> : <Wrench className="size-3 shrink-0 text-amber-500" />}
                  <p className={cn("truncate text-sm leading-tight", isAlert ? "font-semibold" : "font-medium")}>{task.title}</p>
                </div>
                {task.description && density !== "compact" && (
                  <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{task.description}</p>
                )}
                {task.due_date && (
                  <span className={cn("mt-1 flex items-center gap-0.5 text-[10px]", isOverdue ? "font-medium text-red-500" : "text-muted-foreground")}>
                    <CalendarIcon className="size-2.5" />
                    {isOverdue ? "Overdue" : formatCalendarDate(task.due_date)}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

// ─── Command Center (beginner / home) ────────────────────────────────────────────

export function CommandCenterView(props: AdaptiveDashboardProps) {
  const { grow, metrics, climate, tasks, onCompleteTask, growId, growStage, tentId, hasSensorData, sensorTrends, healthScore, density } = props;
  const plain = density === "relaxed";
  const shown = metricsForDensity(metrics, density);

  return (
    <div className="flex flex-col gap-4">
      <HeroBanner grow={grow} density={density} />

      <NextBestAction growId={growId} growStage={growStage} tasks={tasks} healthScore={healthScore} />

      <div className={plain ? "grid grid-cols-2 gap-3 sm:grid-cols-4" : "grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4"}>
        {shown.map((m) => (
          <StatChip key={m.key} metric={m} plainLanguage={plain} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
        <div className="flex flex-col gap-4">
          {climate.length >= 2 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="size-4 text-primary" />
                  24-Hour Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <TrendChart data={climate} showWater={!plain} height={plain ? 200 : 260} />
              </CardContent>
            </Card>
          )}
          <CameraGrid key={tentId} tentId={tentId} hideEmpty />
        </div>

        <div className="flex flex-col gap-4">
          <DashboardAiInsights growId={growId} growStage={growStage} hasSensorData={hasSensorData} sensorTrends={sensorTrends} />
          <TasksPanel tasks={tasks} onComplete={onCompleteTask} density={density} />
        </div>
      </div>
    </div>
  );
}

// ─── Bento Grid (standard / pro / commercial) ────────────────────────────────────

export function BentoView(props: AdaptiveDashboardProps) {
  const { grow, metrics, climate, tasks, onCompleteTask, growId, growStage, tentId, hasSensorData, sensorTrends, healthScore, density } = props;
  const dense = density === "compact";
  const shown = metricsForDensity(metrics, density);

  return (
    <div className="flex flex-col gap-3">
      <NextBestAction growId={growId} growStage={growStage} tasks={tasks} healthScore={healthScore} />

      <div className={cn("grid gap-3", dense ? "grid-cols-2 sm:grid-cols-4 lg:grid-cols-6" : "grid-cols-2 lg:grid-cols-4")}>
        <div className="col-span-1">
          <HealthTile score={healthScore} />
        </div>
        <div className="col-span-1">
          <HarvestTile grow={grow} />
        </div>

        {climate.length >= 2 && (
          <div className={cn("col-span-2", dense ? "lg:col-span-4" : "lg:col-span-2")}>
            <Card className="h-full">
              <CardHeader className="pb-1">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <TrendingUp className="size-4 text-primary" />
                  24h Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <TrendChart data={climate} showWater height={dense ? 150 : 180} />
              </CardContent>
            </Card>
          </div>
        )}

        {shown.map((m) => (
          <div key={m.key} className="col-span-1">
            <MetricTile metric={m} showSparkline />
          </div>
        ))}
      </div>

      <div className={cn("grid gap-3", dense ? "lg:grid-cols-3" : "lg:grid-cols-2")}>
        <CameraGrid key={tentId} tentId={tentId} hideEmpty />
        <DashboardAiInsights growId={growId} growStage={growStage} hasSensorData={hasSensorData} sensorTrends={sensorTrends} />
        <div className={dense ? undefined : "lg:col-span-2"}>
          <TasksPanel tasks={tasks} onComplete={onCompleteTask} density={density} />
        </div>
      </div>
    </div>
  );
}
