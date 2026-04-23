"use client";

import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ChevronUp, ChevronDown, RotateCcw } from "lucide-react";
import type { WidgetConfig, WidgetId } from "@/hooks/use-widget-layout";

interface CustomizeWidgetsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  widgets: WidgetConfig[];
  toggle: (id: WidgetId) => void;
  moveUp: (id: WidgetId) => void;
  moveDown: (id: WidgetId) => void;
  reset: () => void;
}

export function CustomizeWidgetsDialog({
  open,
  onOpenChange,
  widgets,
  toggle,
  moveUp,
  moveDown,
  reset,
}: CustomizeWidgetsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Customize Dashboard</DialogTitle>
        </DialogHeader>
        <div className="space-y-2">
          {widgets.map((w, i) => (
            <div
              key={w.id}
              className="flex items-center gap-3 rounded-lg border p-3"
            >
              <Switch
                checked={w.visible}
                onCheckedChange={() => toggle(w.id)}
              />
              <span className="flex-1 text-sm font-medium">{w.label}</span>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-7"
                  disabled={i === 0}
                  onClick={() => moveUp(w.id)}
                >
                  <ChevronUp className="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-7"
                  disabled={i === widgets.length - 1}
                  onClick={() => moveDown(w.id)}
                >
                  <ChevronDown className="size-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
        <div className="flex justify-between pt-2">
          <Button variant="ghost" size="sm" onClick={reset}>
            <RotateCcw className="mr-1 size-3" />
            Reset
          </Button>
          <Button size="sm" onClick={() => onOpenChange(false)}>
            Done
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
