"use client";

import { useEffect } from "react";
import { useCanvasStore } from "./use-canvas-state";

/**
 * Global keyboard shortcuts for the field canvas.
 * Attach to a container div via ref, or use at page level.
 */
export function useKeyboard() {
  const {
    tool,
    setTool,
    selectedIds,
    removeElements,
    duplicateElements,
    undo,
    redo,
    toggleSnap,
    toggleGrid,
    scale,
    setViewport,
    stageX,
    stageY,
    clearSelection,
    elements,
    activeLayerId,
    select,
  } = useCanvasStore();

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Don't fire when typing in inputs
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;

      const ctrl = e.ctrlKey || e.metaKey;

      switch (e.key.toLowerCase()) {
        case "v":
          if (!ctrl) setTool("select");
          break;
        case "h":
          if (!ctrl) setTool("pan");
          break;
        case "c":
          if (!ctrl) setTool("connect");
          break;
        case "g":
          if (!ctrl) toggleSnap();
          else toggleGrid();
          break;
        case "delete":
        case "backspace":
          if (selectedIds.size > 0) {
            e.preventDefault();
            removeElements([...selectedIds]);
          }
          break;
        case "d":
          if (ctrl && selectedIds.size > 0) {
            e.preventDefault();
            duplicateElements([...selectedIds]);
          }
          break;
        case "z":
          if (ctrl && e.shiftKey) {
            e.preventDefault();
            redo();
          } else if (ctrl) {
            e.preventDefault();
            undo();
          }
          break;
        case "a":
          if (ctrl) {
            e.preventDefault();
            // Select all visible, unlocked elements in active layer
            const ids = elements
              .filter((el) => el.layerId === activeLayerId && el.visible && !el.locked)
              .map((el) => el.id);
            select(ids);
          }
          break;
        case "=":
        case "+":
          e.preventDefault();
          setViewport(stageX, stageY, Math.min(scale * 1.2, 4));
          break;
        case "-":
          e.preventDefault();
          setViewport(stageX, stageY, Math.max(scale / 1.2, 0.2));
          break;
        case "0":
          if (!ctrl) {
            e.preventDefault();
            setViewport(0, 0, 1);
          }
          break;
        case "escape":
          clearSelection();
          break;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    tool, setTool, selectedIds, removeElements, duplicateElements,
    undo, redo, toggleSnap, toggleGrid, scale, setViewport,
    stageX, stageY, clearSelection, elements, activeLayerId, select,
  ]);
}
