"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HealthTab } from "./health-tab";
import { PhotosTab } from "./photos-tab";
import type { GrowResponse, BucketResponse } from "@/lib/api";

interface HealthPhotosTabProps {
  grow: GrowResponse;
  growId: string;
  buckets: BucketResponse[];
  onRefresh: () => void;
}

export function HealthPhotosTab({ grow, growId, buckets, onRefresh }: HealthPhotosTabProps) {
  const [sub, setSub] = useState("health");

  return (
    <div className="space-y-4">
      <Tabs value={sub} onValueChange={setSub}>
        <TabsList>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="photos">Photos</TabsTrigger>
        </TabsList>
        <TabsContent value="health" className="mt-4">
          <HealthTab grow={grow} onRefresh={onRefresh} />
        </TabsContent>
        <TabsContent value="photos" className="mt-4">
          <PhotosTab growId={growId} buckets={buckets} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
