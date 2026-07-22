"use client";

import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  Plus,
  Scissors,
  Sparkles,
  Sprout,
  TrendingUp,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SensorSparkline } from "@/components/sparkline";
import { cn } from "@/lib/utils";
import type {
  AttentionItem,
  ClimatePoint,
  Density,
  FleetGrow,
  MetricStatus,
  PreviewCamera,
  PreviewGrow,
  PreviewMetric,
  PreviewTask,
} from "./preview-data";

// ─── Status helpers ────────────────────────────────────────────────────────────

interface StatusStyle {
  text: string;
  bg: string;
  border: string;
  dot: string;
  ring: string;
  label: string;
}

export function statusStyle(status: MetricStatus): StatusStyle {
  switch (status) {
    case "optimal":
      return { text: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30", dot: "bg-emerald-500", ring: "var(--color-primary)", label: "Good" };
    case "warning":
      return { text: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30", dot: "bg-amber-500", ring: "#f59e0b", label: "Check" };
    case "critical":
      return { text: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/40", dot: "bg-red-500", ring: "#ef4444", label: "Alert" };
    default:
      return { text: "text-muted-foreground", bg: "bg-muted", border: "border-border", dot: "bg-muted-foreground", ring: "var(--color-muted-foreground)", label: "No data" };
  }
}

function healthColor(score: number): string {
  return score >= 80 ? "var(--color-primary)" : score >= 50 ? "#f59e0b" : "#ef4444";
}

// ─── Health ring ────────────────────────────────────────────────────────────────

export function HealthRing({ score, size = 72, stroke = 7 }: { score: number | null; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2;
  const circumference = 2 * Math.PI * r;
  const pct = score == null ? 0 : Math.max(0, Math.min(100, score));
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} strokeWidth={stroke} fill="none" style={{ stroke: "var(--color-muted)" }} />
        {score != null && (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={r}
            strokeWidth={stroke}
            strokeLinecap="round"
            fill="none"
            style={{ stroke: healthColor(score), strokeDasharray: circumference, strokeDashoffset: offset, transition: "stroke-dashoffset 0.6s ease" }}
          />
        )}
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-bold leading-none tabular-nums">{score ?? "—"}</span>
        {score != null && <span className="text-[9px] text-muted-foreground">/ 100</span>}
      </div>
    </div>
  );
}

// ─── Hero banner (Command Center) ───────────────────────────────────────────────

export function HeroBanner({ grow, density = "normal" }: { grow: PreviewGrow; density?: Density }) {
  const hasCycle = grow.cycleTotal > 0;
  const cyclePct = hasCycle ? Math.max(0, Math.min(100, Math.round((grow.cycleDay / grow.cycleTotal) * 100))) : 0;
  const ringSize = density === "relaxed" ? 92 : 76;

  return (
    <div className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-primary/10 via-card to-card p-5 lg:p-6">
      <div className="flex flex-wrap items-center gap-5">
        <HealthRing score={grow.healthScore} size={ringSize} stroke={8} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Sprout className="size-4 text-primary" />
            <span className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{grow.stage}</span>
            <Badge variant="secondary" className="text-[10px]">Day {grow.dayInStage}</Badge>
          </div>
          <h2 className="mt-1 truncate text-2xl font-bold">{grow.name}</h2>
          {grow.strain && <p className="truncate text-sm text-muted-foreground">{grow.strain}</p>}
        </div>
        {grow.harvestInDays != null && (
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Harvest in</p>
            <p className="text-3xl font-bold text-primary">
              {grow.harvestInDays}
              <span className="ml-1 text-sm font-medium text-muted-foreground">days</span>
            </p>
          </div>
        )}
      </div>
      {hasCycle && (
        <div className="mt-5">
          <div className="mb-1 flex justify-between text-[11px] text-muted-foreground">
            <span>Cycle progress</span>
            <span>{cyclePct}%</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-muted">
            <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${cyclePct}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Attention bar ───────────────────────────────────────────────────────────────

export function AttentionBar({ items }: { items: AttentionItem[] }) {
  if (items.length === 0) return null;
  const top = items[0];
  const critical = top.tone === "critical";

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-3 rounded-xl border p-3",
        critical ? "border-red-500/40 bg-red-500/5" : "border-amber-500/40 bg-amber-500/5",
      )}
    >
      <AlertTriangle className={cn("size-5 shrink-0", critical ? "text-red-500" : "text-amber-500")} />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold">{top.title}</p>
        <p className="text-xs text-muted-foreground">{top.detail}</p>
      </div>
      {items.length > 1 && (
        <Badge variant="outline" className="text-[10px]">+{items.length - 1} more</Badge>
      )}
      <Button size="sm" variant="outline" className={cn(critical ? "border-red-500/40 text-red-600" : "border-amber-500/40 text-amber-600")}>
        {top.cta}
      </Button>
    </div>
  );
}

// ─── Stat chip (Command Center compact metric) ──────────────────────────────────

export function StatChip({ metric, plainLanguage }: { metric: PreviewMetric; plainLanguage?: boolean }) {
  const s = statusStyle(metric.status);
  const Icon = metric.icon;

  return (
    <div className={cn("flex items-center gap-3 rounded-xl border bg-card p-3", s.border)}>
      <div className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg", s.bg, s.text)}>
        <Icon className="size-4" />
      </div>
      <div className="min-w-0">
        <p className="truncate text-[11px] text-muted-foreground">{metric.label}</p>
        <p className="text-lg font-bold leading-tight">{metric.value}</p>
        {metric.updatedAgo && <p className="text-[10px] text-muted-foreground">{metric.updatedAgo}</p>}
      </div>
      <div className="ml-auto flex flex-col items-end gap-1">
        <span className={cn("size-2 rounded-full", s.dot)} aria-hidden />
        {plainLanguage && metric.status !== "unknown" && (
          <span className={cn("text-[10px] font-medium", s.text)}>{s.label}</span>
        )}
      </div>
    </div>
  );
}

// ─── Metric tile (Bento) ─────────────────────────────────────────────────────────

export function MetricTile({ metric, showSparkline }: { metric: PreviewMetric; showSparkline?: boolean }) {
  const s = statusStyle(metric.status);
  const Icon = metric.icon;
  const statusLabel = metric.status === "optimal" ? "Optimal" : metric.status === "warning" ? "Attention" : metric.status === "critical" ? "Alert" : null;

  return (
    <Card className={cn("h-full border", s.border)}>
      <CardContent className="flex h-full flex-col gap-2 p-4">
        <div className="flex items-center justify-between">
          <div className={cn("flex size-8 items-center justify-center rounded-lg", s.bg, s.text)}>
            <Icon className="size-4" />
          </div>
          {statusLabel && (
            <Badge variant="outline" className={cn("text-[10px]", s.text, s.border)}>{statusLabel}</Badge>
          )}
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{metric.label}</p>
          <p className="text-2xl font-bold leading-tight">{metric.value}</p>
          {metric.updatedAgo && <p className="text-[10px] text-muted-foreground">{metric.updatedAgo}</p>}
        </div>
        {showSparkline && metric.trend && metric.trend.length > 1 && (
          <div className="mt-auto pt-1">
            <SensorSparkline data={metric.trend} ranges={metric.ranges} height={28} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Trend chart ─────────────────────────────────────────────────────────────────

export function TrendChart({ data, showWater = false, height = 240 }: { data: ClimatePoint[]; showWater?: boolean; height?: number }) {
  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <LineChart data={data} margin={{ top: 5, right: 16, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.5} />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }} tickLine={false} axisLine={false} interval={5} />
          <YAxis yAxisId="temp" tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }} tickLine={false} axisLine={false} domain={["dataMin - 5", "dataMax + 5"]} />
          <YAxis yAxisId="pct" orientation="right" tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }} tickLine={false} axisLine={false} domain={[0, 100]} />
          <RechartsTooltip contentStyle={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)", borderRadius: "8px", fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
          <Line yAxisId="temp" type="monotone" dataKey="temperature" stroke="oklch(0.65 0.15 30)" strokeWidth={2} dot={false} name="Tent Temp (°F)" connectNulls />
          <Line yAxisId="pct" type="monotone" dataKey="humidity" stroke="oklch(0.65 0.14 200)" strokeWidth={2} dot={false} name="Humidity (%)" connectNulls />
          {showWater && (
            <>
              <Line yAxisId="temp" type="monotone" dataKey="water_temp" stroke="#f97316" strokeWidth={2} dot={false} name="Water Temp (°F)" connectNulls />
              <Line yAxisId="temp" type="monotone" dataKey="ph" stroke="#10b981" strokeWidth={2} dot={false} name="pH" connectNulls />
              <Line yAxisId="temp" type="monotone" dataKey="ppm" stroke="#3b82f6" strokeWidth={1.5} strokeDasharray="4 2" dot={false} name="PPM" connectNulls />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── Camera tile ─────────────────────────────────────────────────────────────────

export function CameraTile({ camera, className }: { camera: PreviewCamera; className?: string }) {
  return (
    <Card className={cn("overflow-hidden p-0", className)}>
      <div className="relative flex aspect-video items-center justify-center bg-gradient-to-br from-muted to-muted/40">
        <Camera className="size-8 text-muted-foreground/40" />
        <div className="absolute left-2 top-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] font-medium text-white">
          <span className={cn("size-1.5 rounded-full", camera.status === "live" ? "animate-pulse bg-emerald-400" : "bg-muted-foreground")} />
          {camera.status === "live" ? "LIVE" : "OFFLINE"}
        </div>
        <div className="absolute bottom-2 left-2 text-xs font-medium text-white drop-shadow">{camera.label}</div>
      </div>
    </Card>
  );
}

// ─── Tasks tile ──────────────────────────────────────────────────────────────────

export function TasksTile({ tasks, density = "normal", className }: { tasks: PreviewTask[]; density?: Density; className?: string }) {
  return (
    <Card className={cn("h-full", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <CheckCircle2 className="size-4 text-primary" />
          Tasks
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {tasks.length === 0 && <p className="py-4 text-center text-sm text-muted-foreground">All caught up.</p>}
        {tasks.map((t) => (
          <div key={t.id} className="flex items-start gap-2.5 rounded-lg border p-2.5">
            <span className="mt-0.5 flex size-4 shrink-0 rounded-full border-2 border-primary/40" aria-hidden />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium leading-tight">{t.title}</p>
              {t.detail && density !== "compact" && (
                <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{t.detail}</p>
              )}
            </div>
            {t.priority === "urgent" && <Badge variant="destructive" className="text-[10px]">Urgent</Badge>}
            {t.priority === "high" && <Badge variant="outline" className="border-amber-500/40 text-[10px] text-amber-600">High</Badge>}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// ─── AI coach tile ───────────────────────────────────────────────────────────────

export function AiCoachTile({ tip, className }: { tip: string; className?: string }) {
  return (
    <Card className={cn("h-full border-primary/20 bg-primary/5", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="size-4 text-primary" />
          AI Coach
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{tip}</p>
      </CardContent>
    </Card>
  );
}

// ─── Harvest tile (Bento) ────────────────────────────────────────────────────────

export function HarvestTile({ grow }: { grow: PreviewGrow }) {
  const hasCycle = grow.cycleTotal > 0;
  const pct = hasCycle ? Math.max(0, Math.min(100, Math.round((grow.cycleDay / grow.cycleTotal) * 100))) : 0;
  return (
    <Card className="h-full">
      <CardContent className="flex h-full flex-col justify-between gap-3 p-4">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Scissors className="size-4" />
          <span className="text-xs font-medium">Harvest</span>
        </div>
        <div>
          {grow.harvestInDays != null ? (
            <p className="text-3xl font-bold text-primary">
              {grow.harvestInDays}
              <span className="ml-1 text-sm font-medium text-muted-foreground">days</span>
            </p>
          ) : (
            <p className="text-lg font-semibold capitalize text-muted-foreground">{grow.stage}</p>
          )}
          <p className="text-xs text-muted-foreground">{grow.stage} · Day {grow.dayInStage}</p>
        </div>
        {hasCycle && (
          <div className="h-1.5 overflow-hidden rounded-full bg-muted">
            <div className="h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ─── Health tile (Bento) ─────────────────────────────────────────────────────────

export function HealthTile({ score }: { score: number | null }) {
  return (
    <Card className="h-full">
      <CardContent className="flex h-full flex-col items-center justify-center gap-2 p-4 text-center">
        <HealthRing score={score} size={84} stroke={8} />
        <div>
          <p className="text-xs font-medium">Plant Health</p>
          <p className="text-[11px] text-muted-foreground">
            {score == null ? "No data" : score >= 80 ? "Thriving" : score >= 50 ? "Needs attention" : "Critical"}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Fleet strip (Commercial) ────────────────────────────────────────────────────

export function FleetStrip({ grows, activeId }: { grows: FleetGrow[]; activeId?: string }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      {grows.map((g) => {
        const dot = g.health >= 80 ? "bg-emerald-500" : g.health >= 50 ? "bg-amber-500" : "bg-red-500";
        return (
          <button
            key={g.id}
            className={cn(
              "flex shrink-0 items-center gap-2 rounded-xl border px-3 py-2 transition-colors",
              g.id === activeId ? "border-primary bg-primary/5" : "bg-card hover:bg-muted/50",
            )}
          >
            <span className={cn("size-2 rounded-full", dot)} aria-hidden />
            <div className="text-left">
              <p className="text-xs font-semibold leading-tight">{g.name}</p>
              <p className="text-[10px] text-muted-foreground">{g.stage} · {g.health}</p>
            </div>
            {g.alert && <AlertTriangle className="size-3.5 text-amber-500" />}
          </button>
        );
      })}
      <button className="flex shrink-0 items-center gap-1 rounded-xl border border-dashed px-3 py-2 text-xs text-muted-foreground hover:bg-muted/50">
        <Plus className="size-3.5" />
        Add grow
      </button>
    </div>
  );
}

// ─── Section title helper ────────────────────────────────────────────────────────

export function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <CardTitle className="flex items-center gap-2 text-sm">
      <TrendingUp className="size-4 text-primary" />
      {children}
    </CardTitle>
  );
}
