"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SensorsTab } from "./sensors-tab";
import { JournalTab } from "./journal-tab";
import type { BucketResponse, JournalEntryResponse } from "@/lib/api";

interface ActivityTabProps {
  buckets: BucketResponse[];
  journalEntries: JournalEntryResponse[];
  bucketLabelMap: Record<string, string>;
  onRefresh: () => void;
}

export function ActivityTab({ buckets, journalEntries, bucketLabelMap, onRefresh }: ActivityTabProps) {
  const [sub, setSub] = useState("journal");

  return (
    <div className="space-y-4">
      <Tabs value={sub} onValueChange={setSub}>
        <TabsList>
          <TabsTrigger value="journal">Timeline</TabsTrigger>
          <TabsTrigger value="readings">Readings</TabsTrigger>
        </TabsList>
        <TabsContent value="journal" className="mt-4">
          <JournalTab
            buckets={buckets}
            journalEntries={journalEntries}
            bucketLabelMap={bucketLabelMap}
            onRefresh={onRefresh}
          />
        </TabsContent>
        <TabsContent value="readings" className="mt-4">
          <SensorsTab buckets={buckets} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
