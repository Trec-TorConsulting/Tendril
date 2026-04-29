"use client";

import { Badge } from "@/components/ui/badge";
import { Droplets, Thermometer, Wind, Zap } from "lucide-react";

interface SensorSummaryStripProps {
  ph?: number | null;
  ec?: number | null;
  tempF?: number | null;
  humidity?: number | null;
}

export function SensorSummaryStrip({ ph, ec, tempF, humidity }: SensorSummaryStripProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {ph != null && (
        <Badge variant="outline" className="gap-1 text-xs font-normal">
          <Droplets className="size-3 text-blue-500" />
          pH {ph.toFixed(1)}
        </Badge>
      )}
      {ec != null && (
        <Badge variant="outline" className="gap-1 text-xs font-normal">
          <Zap className="size-3 text-yellow-500" />
          EC {ec.toFixed(1)}
        </Badge>
      )}
      {tempF != null && (
        <Badge variant="outline" className="gap-1 text-xs font-normal">
          <Thermometer className="size-3 text-orange-500" />
          {tempF.toFixed(0)}°F
        </Badge>
      )}
      {humidity != null && (
        <Badge variant="outline" className="gap-1 text-xs font-normal">
          <Wind className="size-3 text-cyan-500" />
          {humidity.toFixed(0)}%
        </Badge>
      )}
    </div>
  );
}
