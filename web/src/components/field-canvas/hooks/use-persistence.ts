"use client";

import { useEffect, useRef } from "react";
import { useCanvasStore } from "./use-canvas-state";
import { getAccessToken } from "@/lib/auth";

const SAVE_DEBOUNCE_MS = 2000;

/**
 * Auto-saves canvas data when dirty flag is set.
 * Debounces by 2s of inactivity.
 */
export function usePersistence(growId: string) {
  const dirty = useCanvasStore((s) => s.dirty);
  const getCanvasData = useCanvasStore((s) => s.getCanvasData);
  const markClean = useCanvasStore((s) => s.markClean);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const savingRef = useRef(false);

  useEffect(() => {
    if (!dirty) return;

    if (timerRef.current) clearTimeout(timerRef.current);

    timerRef.current = setTimeout(async () => {
      if (savingRef.current) return;
      savingRef.current = true;

      try {
        const token = await getAccessToken();
        if (!token) return;

        const data = getCanvasData();
        const resp = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || ""}/v1/grows/${growId}/field-canvas`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            credentials: "include",
            body: JSON.stringify({ canvas_data: data }),
          }
        );

        if (resp.ok) {
          markClean();
        }
      } catch {
        // Will retry on next dirty cycle
      } finally {
        savingRef.current = false;
      }
    }, SAVE_DEBOUNCE_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [dirty, getCanvasData, markClean, growId]);
}
