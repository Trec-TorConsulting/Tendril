"use client";

import { useState, useEffect, useCallback } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FeedingLogForm } from "@/components/quick-log/feeding-log-form";
import { ManualReadingForm } from "@/components/quick-log/manual-reading-form";
import { QuickNoteForm } from "@/components/quick-log/quick-note-form";
import { Droplets, Thermometer, StickyNote } from "lucide-react";

interface QuickLogSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function QuickLogSheet({ open, onOpenChange }: QuickLogSheetProps) {
  const [activeTab, setActiveTab] = useState("feeding");

  // ⌘L keyboard shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "l") {
        e.preventDefault();
        onOpenChange(!open);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onOpenChange]);

  const handleSuccess = useCallback(() => {
    onOpenChange(false);
  }, [onOpenChange]);

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="h-[85dvh] rounded-t-2xl px-4 pb-safe">
        <SheetHeader className="pb-2">
          <SheetTitle className="text-lg">Quick Log</SheetTitle>
        </SheetHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-1 flex-col">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="feeding" className="gap-1.5">
              <Droplets className="size-4" />
              <span className="hidden sm:inline">Feeding</span>
            </TabsTrigger>
            <TabsTrigger value="reading" className="gap-1.5">
              <Thermometer className="size-4" />
              <span className="hidden sm:inline">Reading</span>
            </TabsTrigger>
            <TabsTrigger value="note" className="gap-1.5">
              <StickyNote className="size-4" />
              <span className="hidden sm:inline">Note</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="feeding" className="flex-1 overflow-y-auto mt-4">
            <FeedingLogForm onSuccess={handleSuccess} />
          </TabsContent>
          <TabsContent value="reading" className="flex-1 overflow-y-auto mt-4">
            <ManualReadingForm onSuccess={handleSuccess} />
          </TabsContent>
          <TabsContent value="note" className="flex-1 overflow-y-auto mt-4">
            <QuickNoteForm onSuccess={handleSuccess} />
          </TabsContent>
        </Tabs>
      </SheetContent>
    </Sheet>
  );
}
