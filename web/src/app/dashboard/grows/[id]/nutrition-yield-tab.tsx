"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FeedingTab } from "./feeding-tab";
import { HarvestTab } from "./harvest-tab";
import type { BucketResponse } from "@/lib/api";

interface NutritionYieldTabProps {
  growId: string;
  growStage: string;
  growStartedAt: string;
  milestones: Record<string, string>;
  settings: Record<string, unknown>;
  buckets: BucketResponse[];
  onRefresh: () => void;
}

export function NutritionYieldTab({ growId, growStage, growStartedAt, milestones, settings, buckets, onRefresh }: NutritionYieldTabProps) {
  const [sub, setSub] = useState("feeding");

  return (
    <div className="space-y-4">
      <Tabs value={sub} onValueChange={setSub}>
        <TabsList>
          <TabsTrigger value="feeding">Feeding</TabsTrigger>
          <TabsTrigger value="harvest">Harvest & Yields</TabsTrigger>
        </TabsList>
        <TabsContent value="feeding" className="mt-4">
          <FeedingTab
            growId={growId}
            growStage={growStage}
            growStartedAt={growStartedAt}
            milestones={milestones}
            settings={settings}
            buckets={buckets}
            onRefresh={onRefresh}
          />
        </TabsContent>
        <TabsContent value="harvest" className="mt-4">
          <HarvestTab growId={growId} buckets={buckets} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
