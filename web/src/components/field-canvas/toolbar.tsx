"use client";

import { useCanvasStore } from "./hooks/use-canvas-state";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  MousePointer2,
  Hand,
  Cable,
  Grid3X3,
  Magnet,
  ZoomIn,
  ZoomOut,
  Maximize,
  Undo2,
  Redo2,
  Save,
  Trash2,
  Copy,
  PanelRight,
  PanelRightClose,
} from "lucide-react";

interface ToolbarProps {
  onToggleRightPanel: () => void;
  rightPanelOpen: boolean;
}

export function Toolbar({ onToggleRightPanel, rightPanelOpen }: ToolbarProps) {
  const {
    tool,
    setTool,
    snapEnabled,
    toggleSnap,
    showGrid,
    toggleGrid,
    scale,
    setViewport,
    stageX,
    stageY,
    undo,
    redo,
    selectedIds,
    removeElements,
    duplicateElements,
    dirty,
    _historyIndex,
    _history,
  } = useCanvasStore();

  const canUndo = _historyIndex >= 0;
  const canRedo = _historyIndex < _history.length - 1;

  return (
    <TooltipProvider delay={300}>
      <div className="flex items-center gap-1 rounded-lg border bg-background/95 backdrop-blur px-2 py-1 shadow-sm">
        {/* Tool selection */}
        <ToolBtn
          icon={<MousePointer2 className="h-4 w-4" />}
          label="Select (V)"
          active={tool === "select"}
          onClick={() => setTool("select")}
        />
        <ToolBtn
          icon={<Hand className="h-4 w-4" />}
          label="Pan (H)"
          active={tool === "pan"}
          onClick={() => setTool("pan")}
        />
        <ToolBtn
          icon={<Cable className="h-4 w-4" />}
          label="Connect (C)"
          active={tool === "connect"}
          onClick={() => setTool("connect")}
        />

        <Separator orientation="vertical" className="mx-1 h-6" />

        {/* Grid & Snap */}
        <ToolBtn
          icon={<Grid3X3 className="h-4 w-4" />}
          label="Toggle Grid (Ctrl+G)"
          active={showGrid}
          onClick={toggleGrid}
        />
        <ToolBtn
          icon={<Magnet className="h-4 w-4" />}
          label="Toggle Snap (G)"
          active={snapEnabled}
          onClick={toggleSnap}
        />

        <Separator orientation="vertical" className="mx-1 h-6" />

        {/* Zoom */}
        <ToolBtn
          icon={<ZoomOut className="h-4 w-4" />}
          label="Zoom Out (-)"
          onClick={() => setViewport(stageX, stageY, Math.max(scale / 1.2, 0.2))}
        />
        <span className="min-w-[3rem] text-center text-xs text-muted-foreground">
          {Math.round(scale * 100)}%
        </span>
        <ToolBtn
          icon={<ZoomIn className="h-4 w-4" />}
          label="Zoom In (+)"
          onClick={() => setViewport(stageX, stageY, Math.min(scale * 1.2, 4))}
        />
        <ToolBtn
          icon={<Maximize className="h-4 w-4" />}
          label="Fit to Screen (0)"
          onClick={() => setViewport(0, 0, 1)}
        />

        <Separator orientation="vertical" className="mx-1 h-6" />

        {/* Actions */}
        <ToolBtn
          icon={<Undo2 className="h-4 w-4" />}
          label="Undo (Ctrl+Z)"
          onClick={undo}
          disabled={!canUndo}
        />
        <ToolBtn
          icon={<Redo2 className="h-4 w-4" />}
          label="Redo (Ctrl+Shift+Z)"
          onClick={redo}
          disabled={!canRedo}
        />

        {selectedIds.size > 0 && (
          <>
            <Separator orientation="vertical" className="mx-1 h-6" />
            <ToolBtn
              icon={<Copy className="h-4 w-4" />}
              label="Duplicate (Ctrl+D)"
              onClick={() => duplicateElements([...selectedIds])}
            />
            <ToolBtn
              icon={<Trash2 className="h-4 w-4" />}
              label="Delete (Del)"
              onClick={() => removeElements([...selectedIds])}
            />
          </>
        )}

        {/* Save indicator */}
        {dirty && (
          <Badge variant="secondary" className="ml-2 text-xs">
            Unsaved
          </Badge>
        )}

        <Separator orientation="vertical" className="mx-1 h-6" />

        {/* Right panel toggle */}
        <ToolBtn
          icon={rightPanelOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRight className="h-4 w-4" />}
          label="Toggle Properties Panel"
          active={rightPanelOpen}
          onClick={onToggleRightPanel}
        />
      </div>
    </TooltipProvider>
  );
}

// ─── Toolbar Button ──────────────────────────────────────────────────────────

function ToolBtn({
  icon,
  label,
  active,
  disabled,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}) {
  return (
    <Tooltip>
      <TooltipTrigger>
        <Button
          variant={active ? "secondary" : "ghost"}
          size="icon"
          className="h-8 w-8"
          onClick={onClick}
          disabled={disabled}
        >
          {icon}
        </Button>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="text-xs">
        {label}
      </TooltipContent>
    </Tooltip>
  );
}
