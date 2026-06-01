"use client";

import { useState } from "react";
import { useCanvasStore } from "./hooks/use-canvas-state";
import { PALETTE_ITEMS, type PaletteCategory, type PaletteItem } from "./types";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  ChevronRight,
  Sprout,
  TreePine,
  Droplets,
  Wrench,
  Shapes,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { cn } from "@/lib/utils";

const CATEGORIES: { id: PaletteCategory; label: string; icon: React.ReactNode }[] = [
  { id: "beds", label: "Beds & Planting", icon: <Sprout className="h-4 w-4" /> },
  { id: "trees", label: "Trees & Structures", icon: <TreePine className="h-4 w-4" /> },
  { id: "water", label: "Water & Irrigation", icon: <Droplets className="h-4 w-4" /> },
  { id: "infrastructure", label: "Infrastructure", icon: <Wrench className="h-4 w-4" /> },
  { id: "other", label: "Other", icon: <Shapes className="h-4 w-4" /> },
];

export function PaletteSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [openCategories, setOpenCategories] = useState<Set<PaletteCategory>>(
    new Set(["beds", "water"])
  );
  const { placingItem, setPlacingItem } = useCanvasStore();

  const toggleCategory = (cat: PaletteCategory) => {
    setOpenCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  const handleItemClick = (item: PaletteItem) => {
    if (placingItem?.type === item.type && placingItem?.label === item.label) {
      setPlacingItem(null); // Deselect
    } else {
      setPlacingItem(item);
    }
  };

  const handleDragStart = (e: React.DragEvent, item: PaletteItem) => {
    e.dataTransfer.setData("application/x-field-canvas-item", JSON.stringify(item));
    e.dataTransfer.effectAllowed = "copy";
  };

  if (collapsed) {
    return (
      <div className="flex flex-col items-center border-r bg-background py-2 px-1 w-10">
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setCollapsed(false)}>
          <PanelLeft className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col border-r bg-background w-48 shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <span className="text-sm font-medium">Items</span>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setCollapsed(true)}>
          <PanelLeftClose className="h-4 w-4" />
        </Button>
      </div>

      {/* Categories */}
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {CATEGORIES.map((cat) => {
            const items = PALETTE_ITEMS.filter((p) => p.category === cat.id);
            const isOpen = openCategories.has(cat.id);

            return (
              <Collapsible key={cat.id} open={isOpen} onOpenChange={() => toggleCategory(cat.id)}>
                <CollapsibleTrigger>
                  <button className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm font-medium hover:bg-muted transition-colors">
                    <ChevronRight
                      className={cn("h-3.5 w-3.5 transition-transform", isOpen && "rotate-90")}
                    />
                    {cat.icon}
                    <span>{cat.label}</span>
                    <span className="ml-auto text-xs text-muted-foreground">{items.length}</span>
                  </button>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <div className="ml-4 mt-1 space-y-0.5">
                    {items.map((item, idx) => {
                      const isActive =
                        placingItem?.type === item.type && placingItem?.label === item.label;
                      return (
                        <button
                          key={`${item.type}-${idx}`}
                          draggable
                          onDragStart={(e) => handleDragStart(e, item)}
                          className={cn(
                            "flex w-full items-center gap-2 rounded-md px-2 py-1 text-xs transition-colors cursor-grab active:cursor-grabbing",
                            isActive
                              ? "bg-primary/10 text-primary ring-1 ring-primary/30"
                              : "hover:bg-muted text-foreground"
                          )}
                          onClick={() => handleItemClick(item)}
                        >
                          <span className="truncate">{item.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </CollapsibleContent>
              </Collapsible>
            );
          })}
        </div>
      </ScrollArea>

      {/* Active placement indicator */}
      {placingItem && (
        <div className="border-t px-3 py-2 bg-primary/5">
          <p className="text-xs text-primary font-medium">
            Placing: {placingItem.label}
          </p>
          <p className="text-[10px] text-muted-foreground">
            Click on canvas · Right-click to cancel
          </p>
        </div>
      )}
    </div>
  );
}
