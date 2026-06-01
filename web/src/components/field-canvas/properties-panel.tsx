"use client";

import { useCanvasStore } from "./hooks/use-canvas-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function PropertiesPanel() {
  const { elements, connectors, selectedIds, updateElement, layers } = useCanvasStore();

  const selectedElements = elements.filter((el) => selectedIds.has(el.id));
  const selectedConnectors = connectors.filter((c) => selectedIds.has(c.id));

  if (selectedElements.length === 0 && selectedConnectors.length === 0) {
    return (
      <div className="border-t px-3 py-2">
        <p className="text-xs text-muted-foreground">Select an element to edit properties</p>
      </div>
    );
  }

  if (selectedElements.length > 1) {
    return (
      <div className="border-t px-3 py-2">
        <p className="text-xs text-muted-foreground">
          {selectedElements.length} elements selected
        </p>
      </div>
    );
  }

  const el = selectedElements[0];
  if (!el) return null;

  return (
    <div className="border-t px-3 py-2 space-y-3">
      <p className="text-xs font-medium">
        {el.type.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
      </p>

      {/* Position */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label className="text-[10px]">X</Label>
          <Input
            type="number"
            className="h-7 text-xs"
            value={Math.round(el.x)}
            onChange={(e) => updateElement(el.id, { x: Number(e.target.value) })}
          />
        </div>
        <div>
          <Label className="text-[10px]">Y</Label>
          <Input
            type="number"
            className="h-7 text-xs"
            value={Math.round(el.y)}
            onChange={(e) => updateElement(el.id, { y: Number(e.target.value) })}
          />
        </div>
      </div>

      {/* Size */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label className="text-[10px]">Width</Label>
          <Input
            type="number"
            className="h-7 text-xs"
            value={Math.round(el.width)}
            onChange={(e) => updateElement(el.id, { width: Math.max(10, Number(e.target.value)) })}
          />
        </div>
        <div>
          <Label className="text-[10px]">Height</Label>
          <Input
            type="number"
            className="h-7 text-xs"
            value={Math.round(el.height)}
            onChange={(e) => updateElement(el.id, { height: Math.max(10, Number(e.target.value)) })}
          />
        </div>
      </div>

      {/* Rotation */}
      <div>
        <Label className="text-[10px]">Rotation</Label>
        <Input
          type="number"
          className="h-7 text-xs"
          value={Math.round(el.rotation)}
          onChange={(e) => updateElement(el.id, { rotation: Number(e.target.value) % 360 })}
        />
      </div>

      {/* Layer */}
      <div>
        <Label className="text-[10px]">Layer</Label>
        <Select value={el.layerId} onValueChange={(v) => v && updateElement(el.id, { layerId: v })}>
          <SelectTrigger className="h-7 text-xs">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {layers.map((l) => (
              <SelectItem key={l.id} value={l.id}>
                {l.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Custom label */}
      <div>
        <Label className="text-[10px]">Label</Label>
        <Input
          className="h-7 text-xs"
          value={(el.props?.label as string) || ""}
          placeholder={el.type.replace(/_/g, " ")}
          onChange={(e) =>
            updateElement(el.id, { props: { ...el.props, label: e.target.value } })
          }
        />
      </div>

      {/* Text content for text_label */}
      {el.type === "text_label" && (
        <div>
          <Label className="text-[10px]">Text</Label>
          <Input
            className="h-7 text-xs"
            value={(el.props?.text as string) || ""}
            onChange={(e) =>
              updateElement(el.id, { props: { ...el.props, text: e.target.value } })
            }
          />
        </div>
      )}
    </div>
  );
}
