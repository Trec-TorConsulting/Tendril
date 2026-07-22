"use client";

import { useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { Info, LayoutGrid, Leaf, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";
import { LAYOUT_CONFIGS, type LayoutMode } from "@/lib/layout-config";
import { PREVIEW_DATA } from "@/components/dashboard-preview/preview-data";
import { CommandCenter } from "@/components/dashboard-preview/command-center";
import { BentoGrid } from "@/components/dashboard-preview/bento-grid";

const MODES: LayoutMode[] = ["beginner", "home", "standard", "pro", "commercial"];

/** Which concept each onboarding persona maps to. */
const MODE_LAYOUT: Record<LayoutMode, "command" | "bento"> = {
  beginner: "command",
  home: "command",
  standard: "bento",
  pro: "bento",
  commercial: "bento",
};

/**
 * Public, standalone preview of the reworked Overview dashboard concepts.
 * Renders with illustrative data and requires no authentication or backend —
 * so the layouts can be reviewed at /preview without signing in.
 */
export default function PublicPreviewPage() {
  const [mode, setMode] = useState<LayoutMode>("beginner");
  const config = LAYOUT_CONFIGS[mode];
  const layout = MODE_LAYOUT[mode];

  return (
    <div className="min-h-dvh bg-background">
      {/* Top bar */}
      <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur lg:px-6">
        <div className="flex size-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <Leaf className="size-4" />
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold leading-tight">Tendril — Dashboard Concepts</p>
          <p className="text-[11px] text-muted-foreground">Adaptive Overview preview · illustrative data</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <Link href="/dashboard" className="text-xs text-muted-foreground hover:text-foreground">
            Open app →
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-4 p-4 lg:p-6">
        {/* Explainer */}
        <div className="flex items-start gap-2 rounded-lg border bg-muted/30 p-3 text-sm">
          <Info className="mt-0.5 size-4 shrink-0 text-primary" />
          <p className="text-muted-foreground">
            The Overview adapts to the experience level chosen at onboarding (
            <code className="rounded bg-muted px-1 py-0.5 text-xs">layout_mode</code>). Switch personas below to compare.{" "}
            <span className="font-medium text-foreground">Beginner &amp; Home → Command Center</span>,{" "}
            <span className="font-medium text-foreground">Standard, Pro &amp; Commercial → Bento Grid</span>.
          </p>
        </div>

        {/* Persona switcher */}
        <div className="flex flex-wrap items-stretch gap-2">
          {MODES.map((m) => {
            const c = LAYOUT_CONFIGS[m];
            const isBento = MODE_LAYOUT[m] === "bento";
            const active = m === mode;
            return (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                aria-pressed={active}
                className={cn(
                  "flex min-w-[9rem] flex-1 flex-col items-start rounded-lg border px-3 py-2 text-left transition-colors sm:flex-none",
                  active ? "border-primary bg-primary/5" : "bg-card hover:bg-muted/50",
                )}
              >
                <span className="flex items-center gap-1.5 text-sm font-semibold">
                  {c.label}
                  <Badge variant="outline" className="gap-1 text-[9px]">
                    {isBento ? <LayoutGrid className="size-2.5" /> : <Sparkles className="size-2.5" />}
                    {isBento ? "Bento" : "Command"}
                  </Badge>
                </span>
                <span className="text-[11px] text-muted-foreground">{c.description}</span>
              </button>
            );
          })}
        </div>

        {/* Adaptive dashboard */}
        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            {layout === "command" ? (
              <CommandCenter data={PREVIEW_DATA} density={config.density} />
            ) : (
              <BentoGrid data={PREVIEW_DATA} density={config.density} showFleet={mode === "commercial"} />
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
