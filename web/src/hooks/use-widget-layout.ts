"use client";

import { useCallback, useEffect, useState } from "react";

export type WidgetId = "stats" | "hero" | "countdown" | "active-grows";

export interface WidgetConfig {
  id: WidgetId;
  label: string;
  visible: boolean;
}

const DEFAULT_LAYOUT: WidgetConfig[] = [
  { id: "stats", label: "Stats Overview", visible: true },
  { id: "hero", label: "Primary Grow Card", visible: true },
  { id: "countdown", label: "Harvest Countdown", visible: true },
  { id: "active-grows", label: "Active Grows", visible: true },
];

const STORAGE_KEY = "tendril-dashboard-layout";

export function useWidgetLayout() {
  const [widgets, setWidgets] = useState<WidgetConfig[]>(DEFAULT_LAYOUT);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as WidgetConfig[];
        // Merge with defaults in case new widgets were added
        const ids = new Set(parsed.map((w) => w.id));
        const merged = [
          ...parsed,
          ...DEFAULT_LAYOUT.filter((d) => !ids.has(d.id)),
        ];
        setWidgets(merged);
      }
    } catch { /* ignore */ }
  }, []);

  const save = useCallback((updated: WidgetConfig[]) => {
    setWidgets(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  }, []);

  const toggle = useCallback((id: WidgetId) => {
    setWidgets((prev) => {
      const next = prev.map((w) => w.id === id ? { ...w, visible: !w.visible } : w);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const moveUp = useCallback((id: WidgetId) => {
    setWidgets((prev) => {
      const idx = prev.findIndex((w) => w.id === id);
      if (idx <= 0) return prev;
      const next = [...prev];
      [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const moveDown = useCallback((id: WidgetId) => {
    setWidgets((prev) => {
      const idx = prev.findIndex((w) => w.id === id);
      if (idx < 0 || idx >= prev.length - 1) return prev;
      const next = [...prev];
      [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    save(DEFAULT_LAYOUT);
  }, [save]);

  const isVisible = useCallback((id: WidgetId) => {
    return widgets.find((w) => w.id === id)?.visible ?? true;
  }, [widgets]);

  return { widgets, toggle, moveUp, moveDown, reset, isVisible };
}
