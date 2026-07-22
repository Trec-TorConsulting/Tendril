"use client";

import { TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { metricsForDensity, type Density, type PreviewData } from "./preview-data";
import {
  AiCoachTile,
  CameraTile,
  FleetStrip,
  HarvestTile,
  HealthTile,
  MetricTile,
  TasksTile,
  TrendChart,
} from "./preview-parts";

/**
 * Bento Grid — Concept B.
 * Modern tile mosaic used by `standard`, `pro`, and `commercial` personas.
 * `compact` density (pro/commercial) surfaces every metric tier and tightens the grid.
 * Commercial adds a fleet strip across the top.
 */
export function BentoGrid({
  data,
  density = "normal",
  showFleet = false,
}: {
  data: PreviewData;
  density?: Density;
  showFleet?: boolean;
}) {
  const dense = density === "compact";
  const metrics = metricsForDensity(data.metrics, density);

  return (
    <div className="flex flex-col gap-3">
      {showFleet && <FleetStrip grows={data.fleet} activeId={data.fleet[0]?.id} />}

      <div className={cn("grid gap-3", dense ? "grid-cols-2 sm:grid-cols-4 lg:grid-cols-6" : "grid-cols-2 lg:grid-cols-4")}>
        {/* Health + harvest anchor the top-left */}
        <div className="col-span-1">
          <HealthTile score={data.grow.healthScore} />
        </div>
        <div className="col-span-1">
          <HarvestTile grow={data.grow} />
        </div>

        {/* Trend chart spans wide */}
        <div className={cn("col-span-2", dense ? "lg:col-span-4" : "lg:col-span-2")}>
          <Card className="h-full">
            <CardHeader className="pb-1">
              <CardTitle className="flex items-center gap-2 text-sm">
                <TrendingUp className="size-4 text-primary" />
                24h Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart data={data.climate} showWater height={dense ? 150 : 180} />
            </CardContent>
          </Card>
        </div>

        {/* Metric tiles */}
        {metrics.map((m) => (
          <div key={m.key} className="col-span-1">
            <MetricTile metric={m} showSparkline />
          </div>
        ))}

        {/* Camera + AI coach + tasks fill the remaining rows */}
        <div className="col-span-2">
          <CameraTile camera={data.cameras[0]} className="h-full" />
        </div>
        <div className="col-span-2">
          <AiCoachTile tip={data.aiTip} />
        </div>
        <div className={cn("col-span-2", dense ? "lg:col-span-2" : "lg:col-span-4")}>
          <TasksTile tasks={data.tasks} density={density} />
        </div>
      </div>
    </div>
  );
}
