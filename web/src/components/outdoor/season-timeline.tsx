"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { BucketResponse } from "@/lib/api";
import { Calendar, Sprout, Leaf, Scissors, Sun, Snowflake } from "lucide-react";

const STAGE_COLORS: Record<string, string> = {
  germination: "bg-lime-400",
  seedling: "bg-green-300",
  vegetative: "bg-green-500",
  flowering: "bg-purple-400",
  ripening: "bg-amber-400",
  harvest: "bg-orange-500",
  curing: "bg-yellow-700",
  done: "bg-gray-400",
};

const STAGE_ORDER = [
  "germination", "seedling", "vegetative", "flowering",
  "ripening", "harvest", "curing", "done",
];

interface Props {
  growId: string;
  buckets: BucketResponse[];
  growStartDate?: string;
}

export function SeasonTimeline({ growId, buckets, growStartDate }: Props) {
  const startDate = growStartDate ? new Date(growStartDate) : new Date();
  const now = new Date();

  // Calculate season boundary dates (approximate for display)
  const seasonStart = new Date(startDate.getFullYear(), 2, 15); // Mar 15
  const seasonEnd = new Date(startDate.getFullYear(), 10, 1);   // Nov 1
  const totalDays = Math.ceil((seasonEnd.getTime() - seasonStart.getTime()) / (1000 * 60 * 60 * 24));

  const dayOffset = (date: Date) => {
    const diff = Math.ceil((date.getTime() - seasonStart.getTime()) / (1000 * 60 * 60 * 24));
    return Math.max(0, Math.min(totalDays, diff));
  };

  const nowOffset = dayOffset(now);
  const todayPct = (nowOffset / totalDays) * 100;

  const months = useMemo(() => {
    const m: { name: string; startPct: number }[] = [];
    for (let i = 2; i <= 10; i++) {
      const d = new Date(startDate.getFullYear(), i, 1);
      const pct = (dayOffset(d) / totalDays) * 100;
      m.push({ name: d.toLocaleString("default", { month: "short" }), startPct: pct });
    }
    return m;
  }, [startDate, totalDays]);

  // Group buckets by stage
  const stageCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    buckets.forEach((b) => {
      const stage = b.growth_stage || "unknown";
      counts[stage] = (counts[stage] || 0) + 1;
    });
    return counts;
  }, [buckets]);

  return (
    <div className="space-y-4">
      {/* Stage summary */}
      <div className="flex flex-wrap gap-2">
        {STAGE_ORDER.filter((s) => stageCounts[s]).map((stage) => (
          <Badge key={stage} variant="outline" className="gap-1">
            <span className={`inline-block size-2 rounded-full ${STAGE_COLORS[stage] ?? "bg-gray-400"}`} />
            {stage}: {stageCounts[stage]}
          </Badge>
        ))}
      </div>

      {/* Timeline */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Calendar className="size-4" />
            Season Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Month labels */}
          <div className="relative mb-1 h-6 text-xs text-muted-foreground">
            {months.map((m) => (
              <span key={m.name} className="absolute" style={{ left: `${m.startPct}%` }}>
                {m.name}
              </span>
            ))}
          </div>

          {/* Track */}
          <div className="relative">
            {/* Background track */}
            <div className="h-2 w-full rounded bg-muted" />

            {/* Frost zones */}
            <div
              className="absolute top-0 h-2 rounded-l bg-blue-200/50 dark:bg-blue-900/30"
              style={{ left: "0%", width: `${(dayOffset(new Date(startDate.getFullYear(), 3, 15)) / totalDays) * 100}%` }}
              title="Frost risk zone (spring)"
            />
            <div
              className="absolute top-0 h-2 rounded-r bg-blue-200/50 dark:bg-blue-900/30"
              style={{ left: `${(dayOffset(new Date(startDate.getFullYear(), 9, 15)) / totalDays) * 100}%`, width: `${100 - (dayOffset(new Date(startDate.getFullYear(), 9, 15)) / totalDays) * 100}%` }}
              title="Frost risk zone (fall)"
            />

            {/* Today marker */}
            <div
              className="absolute top-0 h-6 w-0.5 bg-primary"
              style={{ left: `${todayPct}%` }}
              title={`Today: ${now.toLocaleDateString()}`}
            />
          </div>

          {/* Grow start marker */}
          <div className="relative mt-1 h-4">
            <div
              className="absolute text-xs font-medium text-green-600"
              style={{ left: `${(dayOffset(startDate) / totalDays) * 100}%` }}
            >
              <Sprout className="inline size-3" /> Start
            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><Snowflake className="size-3 text-blue-400" /> Frost zone</span>
            <span className="flex items-center gap-1"><Sun className="size-3 text-amber-400" /> Peak growing</span>
            <span className="flex items-center gap-1"><div className="h-3 w-0.5 bg-primary" /> Today</span>
          </div>
        </CardContent>
      </Card>

      {/* Per-plant timeline */}
      {buckets.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Plant Progress</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {buckets.map((b) => {
              const stageIdx = STAGE_ORDER.indexOf(b.growth_stage || "");
              const progressPct = stageIdx >= 0 ? ((stageIdx + 1) / STAGE_ORDER.length) * 100 : 0;
              return (
                <div key={b.id} className="flex items-center gap-3">
                  <span className="w-24 truncate text-xs font-medium">
                    {b.strain_name || b.label || `Pos ${b.position}`}
                  </span>
                  <div className="relative h-3 flex-1 rounded-full bg-muted">
                    <div
                      className={`h-3 rounded-full transition-all ${STAGE_COLORS[b.growth_stage || ""] ?? "bg-gray-400"}`}
                      style={{ width: `${progressPct}%` }}
                    />
                  </div>
                  <Badge variant="outline" className="min-w-[70px] justify-center text-xs">
                    {b.growth_stage || "—"}
                  </Badge>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
