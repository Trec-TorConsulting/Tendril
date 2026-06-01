"use client";

import { useCallback } from "react";
import { useCanvasStore } from "./use-canvas-state";

/**
 * Snap a coordinate to the nearest grid point if snap is enabled.
 */
export function useSnapGrid() {
  const snapEnabled = useCanvasStore((s) => s.snapEnabled);
  const snapSize = useCanvasStore((s) => s.snapSize);

  const snap = useCallback(
    (value: number): number => {
      if (!snapEnabled) return value;
      return Math.round(value / snapSize) * snapSize;
    },
    [snapEnabled, snapSize]
  );

  const snapPoint = useCallback(
    (x: number, y: number): { x: number; y: number } => {
      if (!snapEnabled) return { x, y };
      return {
        x: Math.round(x / snapSize) * snapSize,
        y: Math.round(y / snapSize) * snapSize,
      };
    },
    [snapEnabled, snapSize]
  );

  return { snap, snapPoint, snapEnabled, snapSize };
}
