"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Info, LayoutGrid, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
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

export default function DashboardPreviewPage() {
  const [mode, setMode] = useState<LayoutMode>("beginner");
  const config = LAYOUT_CONFIGS[mode];
  const layout = MODE_LAYOUT[mode];

  return (
    <>
      <PageHeader
        title="Dashboard Rework — Preview"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Preview" }]}
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {/* Explainer */}
        <div className="flex items-start gap-2 rounded-lg border bg-muted/30 p-3 text-sm">
          <Info className="mt-0.5 size-4 shrink-0 text-primary" />
          <p className="text-muted-foreground">
            The Overview adapts to the experience level chosen at onboarding (
            <code className="rounded bg-muted px-1 py-0.5 text-xs">layout_mode</code>). Switch personas below to compare.{" "}
            <span className="font-medium text-foreground">Beginner &amp; Home → Command Center</span>,{" "}
            <span className="font-medium text-foreground">Standard, Pro &amp; Commercial → Bento Grid</span>. Data shown is
            illustrative.
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
      </div>
    </>
  );
}
