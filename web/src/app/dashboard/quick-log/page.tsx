"use client";

import { useState } from "react";
import { QuickLogSheet } from "@/components/quick-log/quick-log-sheet";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Droplets, Thermometer, StickyNote } from "lucide-react";

export default function QuickLogPage() {
  const [sheetOpen, setSheetOpen] = useState(true);

  return (
    <>
      <PageHeader title="Quick Log" />
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-6">
        <div className="grid w-full max-w-sm gap-3">
          <Button
            variant="outline"
            size="lg"
            className="h-16 justify-start gap-3"
            onClick={() => setSheetOpen(true)}
          >
            <Droplets className="size-5 text-blue-500" />
            <div className="text-left">
              <div className="font-medium">Log Feeding</div>
              <div className="text-xs text-muted-foreground">pH, EC, volume for one or more buckets</div>
            </div>
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="h-16 justify-start gap-3"
            onClick={() => setSheetOpen(true)}
          >
            <Thermometer className="size-5 text-orange-500" />
            <div className="text-left">
              <div className="font-medium">Log Environment</div>
              <div className="text-xs text-muted-foreground">Temperature, humidity, VPD</div>
            </div>
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="h-16 justify-start gap-3"
            onClick={() => setSheetOpen(true)}
          >
            <StickyNote className="size-5 text-yellow-500" />
            <div className="text-left">
              <div className="font-medium">Quick Note</div>
              <div className="text-xs text-muted-foreground">Observations, training, events</div>
            </div>
          </Button>
        </div>
      </div>
      <QuickLogSheet open={sheetOpen} onOpenChange={setSheetOpen} />
    </>
  );
}
