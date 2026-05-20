"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PlotDesigner } from "@/components/outdoor/plot-designer";
import { SoilDashboard } from "@/components/outdoor/soil-dashboard";
import { PestScout } from "@/components/outdoor/pest-scout";
import { OutdoorIntelligence } from "@/components/outdoor/intelligence";
import { SeasonTimeline } from "@/components/outdoor/season-timeline";
import { IrrigationPlanner } from "@/components/outdoor/irrigation-planner";
import ContainerManager from "@/components/outdoor/container-manager";
import RunoffTracker from "@/components/outdoor/runoff-tracker";
import { HarvestTracker } from "@/components/outdoor/harvest-tracker";
import { isOutdoorSoil, isOutdoorContainer } from "@/lib/terminology";
import type { BucketResponse, DeviceResponse } from "@/lib/api";

interface FieldTabProps {
  growId: string;
  growType: string;
  tentId: string;
  buckets: BucketResponse[];
  devices: DeviceResponse[];
  growStartDate: string;
  onRefresh: () => void;
}

export function FieldTab({ growId, growType, tentId, buckets, devices, growStartDate, onRefresh }: FieldTabProps) {
  const isSoil = isOutdoorSoil(growType);
  const isContainer = isOutdoorContainer(growType);

  const defaultSub = isSoil ? "plot" : isContainer ? "containers" : "scouts";
  const [sub, setSub] = useState(defaultSub);

  return (
    <div className="space-y-4">
      <Tabs value={sub} onValueChange={setSub}>
        <TabsList className="flex-wrap">
          {isSoil && <TabsTrigger value="plot">Garden Plot</TabsTrigger>}
          {isContainer && <TabsTrigger value="containers">Containers</TabsTrigger>}
          {isSoil && <TabsTrigger value="soil">Soil Health</TabsTrigger>}
          {isContainer && <TabsTrigger value="runoff">Runoff</TabsTrigger>}
          <TabsTrigger value="scouts">Field Scout</TabsTrigger>
          <TabsTrigger value="yields">Yields</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
          <TabsTrigger value="irrigation">Irrigation</TabsTrigger>
          <TabsTrigger value="season">Season</TabsTrigger>
        </TabsList>

        {isSoil && (
          <TabsContent value="plot" className="mt-4">
            <PlotDesigner growId={growId} buckets={buckets} devices={devices} onBucketCreated={onRefresh} />
          </TabsContent>
        )}

        {isContainer && (
          <TabsContent value="containers" className="mt-4">
            <ContainerManager growId={growId} tentId={tentId} />
          </TabsContent>
        )}

        {isSoil && (
          <TabsContent value="soil" className="mt-4">
            <SoilDashboard growId={growId} />
          </TabsContent>
        )}

        {isContainer && (
          <TabsContent value="runoff" className="mt-4">
            <RunoffTracker growId={growId} tentId={tentId} />
          </TabsContent>
        )}

        <TabsContent value="scouts" className="mt-4">
          <PestScout growId={growId} />
        </TabsContent>

        <TabsContent value="yields" className="mt-4">
          <HarvestTracker growId={growId} buckets={buckets} />
        </TabsContent>

        <TabsContent value="intelligence" className="mt-4">
          <OutdoorIntelligence growId={growId} tentId={tentId} />
        </TabsContent>

        <TabsContent value="irrigation" className="mt-4">
          <IrrigationPlanner growId={growId} />
        </TabsContent>

        <TabsContent value="season" className="mt-4">
          <SeasonTimeline growId={growId} buckets={buckets} growStartDate={growStartDate} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
