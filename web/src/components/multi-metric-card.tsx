"use client";

import { Card, CardContent } from "@/components/ui/card";

export interface MetricRow {
  label: string;
  value: string;
  status: "optimal" | "warning" | "unknown";
}

export function MultiMetricCard({
  title,
  icon,
  metrics,
  updatedAgo,
}: {
  title: string;
  icon: React.ReactNode;
  metrics: MetricRow[];
  updatedAgo?: string | null;
}) {
  const overallStatus = metrics.some((m) => m.status === "warning")
    ? "warning"
    : metrics.every((m) => m.status === "optimal")
      ? "optimal"
      : "unknown";

  const statusColor = {
    optimal: "bg-primary/10 text-primary border-primary/20",
    warning: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    unknown: "bg-muted text-muted-foreground border-border",
  }[overallStatus];

  return (
    <Card className={`border ${statusColor.split(" ").find((c) => c.startsWith("border-")) || "border-border"} backdrop-blur-sm`}>
      <CardContent className="flex gap-4 py-4">
        <div className={`flex size-10 shrink-0 items-center justify-center rounded-lg ${statusColor.split(" ").slice(0, 2).join(" ")}`}>
          {icon}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-muted-foreground mb-1">{title}</p>
          <div className="space-y-0.5">
            {metrics.map((m) => (
              <div key={m.label} className="flex items-baseline justify-between gap-2">
                <span className="text-[11px] text-muted-foreground">{m.label}</span>
                <span className={`text-sm font-bold ${m.status === "warning" ? "text-orange-500" : m.status === "optimal" ? "text-foreground" : "text-muted-foreground"}`}>
                  {m.value}
                </span>
              </div>
            ))}
          </div>
          {updatedAgo && <p className="text-[10px] text-muted-foreground mt-1">{updatedAgo}</p>}
        </div>
      </CardContent>
    </Card>
  );
}
