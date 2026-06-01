"use client";

import { useCanvasStore } from "./hooks/use-canvas-state";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Eye, EyeOff, Lock, Unlock } from "lucide-react";

export function LayersPanel() {
  const { layers, activeLayerId, setActiveLayer, setLayerVisibility, setLayerLocked } =
    useCanvasStore();

  const sorted = [...layers].sort((a, b) => a.order - b.order);

  return (
    <div className="flex flex-col border-l bg-background w-48 shrink-0">
      <div className="px-3 py-2 border-b">
        <span className="text-sm font-medium">Layers</span>
      </div>
      <div className="flex-1 p-2 space-y-0.5">
        {sorted.map((layer) => (
          <div
            key={layer.id}
            className={cn(
              "flex items-center gap-1 rounded-md px-2 py-1 text-xs cursor-pointer transition-colors",
              activeLayerId === layer.id
                ? "bg-primary/10 ring-1 ring-primary/30"
                : "hover:bg-muted"
            )}
            onClick={() => setActiveLayer(layer.id)}
          >
            {/* Color dot */}
            <span
              className="h-2.5 w-2.5 rounded-full shrink-0"
              style={{ backgroundColor: layer.color }}
            />
            <span className="flex-1 truncate">{layer.name}</span>
            {/* Visibility toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="h-5 w-5"
              onClick={(e) => {
                e.stopPropagation();
                setLayerVisibility(layer.id, !layer.visible);
              }}
            >
              {layer.visible ? (
                <Eye className="h-3 w-3" />
              ) : (
                <EyeOff className="h-3 w-3 text-muted-foreground" />
              )}
            </Button>
            {/* Lock toggle */}
            <Button
              variant="ghost"
              size="icon"
              className="h-5 w-5"
              onClick={(e) => {
                e.stopPropagation();
                setLayerLocked(layer.id, !layer.locked);
              }}
            >
              {layer.locked ? (
                <Lock className="h-3 w-3 text-muted-foreground" />
              ) : (
                <Unlock className="h-3 w-3" />
              )}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
