"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import { useCanvasStore } from "./hooks/use-canvas-state";
import { useKeyboard } from "./hooks/use-keyboard";
import { usePersistence } from "./hooks/use-persistence";
import { PaletteSidebar } from "./palette-sidebar";
import { Toolbar } from "./toolbar";
import { LayersPanel } from "./layers-panel";
import { PropertiesPanel } from "./properties-panel";
import { getAccessToken } from "@/lib/auth";
import type { FieldCanvasResponse } from "./types";
import { Loader2 } from "lucide-react";

// Dynamically import CanvasStage to avoid SSR (Konva requires window)
const CanvasStage = dynamic(() => import("./canvas-stage").then((m) => ({ default: m.CanvasStage })), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-muted/30">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  ),
});

interface Props {
  growId: string;
}

export function FieldCanvas({ growId }: Props) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  const loadCanvas = useCanvasStore((s) => s.loadCanvas);

  // Keyboard shortcuts
  useKeyboard();

  // Auto-save
  usePersistence(growId);

  // ─── Load canvas data ──────────────────────────────────────────────────────

  useEffect(() => {
    async function load() {
      try {
        const token = await getAccessToken();
        if (!token) return;

        const resp = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || ""}/v1/grows/${growId}/field-canvas`,
          {
            headers: { Authorization: `Bearer ${token}` },
            credentials: "include",
          }
        );

        if (resp.ok) {
          const data: FieldCanvasResponse = await resp.json();
          loadCanvas(data.canvas_data);
        }
        // 404 = no canvas yet, that's fine — start fresh
      } catch {
        setError("Failed to load canvas");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [growId, loadCanvas]);

  // ─── Resize observer ───────────────────────────────────────────────────────

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height,
        });
      }
    });

    observer.observe(el);
    // Set initial size
    setDimensions({ width: el.clientWidth, height: el.clientHeight });

    return () => observer.disconnect();
  }, []);

  // ─── Render ────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-sm text-destructive">{error}</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-center px-2 py-1.5 border-b bg-muted/30">
        <Toolbar />
      </div>

      {/* Main area */}
      <div className="flex flex-1 min-h-0">
        {/* Palette sidebar (left) */}
        <PaletteSidebar />

        {/* Canvas */}
        <div ref={containerRef} className="flex-1 relative overflow-hidden bg-white dark:bg-stone-950">
          <CanvasStage width={dimensions.width} height={dimensions.height} />
        </div>

        {/* Layers + Properties (right) */}
        <div className="flex flex-col">
          <LayersPanel />
          <PropertiesPanel />
        </div>
      </div>
    </div>
  );
}
