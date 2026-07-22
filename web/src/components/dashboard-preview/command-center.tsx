"use client";

import { TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { metricsForDensity, type Density, type PreviewData } from "./preview-data";
import {
  AiCoachTile,
  AttentionBar,
  CameraTile,
  HeroBanner,
  StatChip,
  TasksTile,
  TrendChart,
} from "./preview-parts";

/**
 * Command Center — Concept A.
 * Focused, single-grow layout used by the `beginner` and `home` personas.
 * `relaxed` density (beginner) uses plain language, hides jargon, shows one camera.
 */
export function CommandCenter({ data, density = "normal" }: { data: PreviewData; density?: Density }) {
  const plain = density === "relaxed";
  const metrics = metricsForDensity(data.metrics, density);
  const cameras = plain ? data.cameras.slice(0, 1) : data.cameras.slice(0, 2);

  return (
    <div className="flex flex-col gap-4">
      <HeroBanner grow={data.grow} density={density} />

      <AttentionBar items={data.attention} />

      <div className={plain ? "grid grid-cols-2 gap-3 sm:grid-cols-4" : "grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4"}>
        {metrics.map((m) => (
          <StatChip key={m.key} metric={m} plainLanguage={plain} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="size-4 text-primary" />
                24-Hour Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart data={data.climate} showWater={!plain} height={plain ? 200 : 260} />
            </CardContent>
          </Card>

          <div className={cameras.length > 1 ? "grid gap-4 sm:grid-cols-2" : "grid gap-4"}>
            {cameras.map((c) => (
              <CameraTile key={c.id} camera={c} />
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <AiCoachTile tip={data.aiTip} />
          <TasksTile tasks={data.tasks} density={density} />
        </div>
      </div>
    </div>
  );
}
