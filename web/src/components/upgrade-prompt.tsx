"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { TrendingUp, X } from "lucide-react";
import Link from "next/link";

interface UsageAlert {
  metric: string;
  current: number;
  limit: number;
  plan: string;
}

const METRIC_LABELS: Record<string, string> = {
  ai_analyses: "AI Analyses",
  grows: "Active Grows",
  devices: "Connected Devices",
  storage_gb: "Storage",
  automations: "Automations",
  integrations: "Integrations",
  team_members: "Team Members",
  journal_entries: "Journal Entries",
};

/**
 * Upgrade prompt banner that shows when a user is at 80%+ of any usage limit.
 * Designed to be placed in the dashboard layout for persistent visibility.
 */
export function UpgradePrompt() {
  const [alerts, setAlerts] = useState<UsageAlert[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  useEffect(() => {
    async function checkLimits() {
      const token = getAccessToken();
      if (!token) return;

      try {
        const data = await apiFetch<{ alerts: UsageAlert[] }>("/billing/usage-alerts", { token });
        setAlerts(data.alerts);
      } catch {
        // Silently fail — this is a non-critical UI enhancement
      }
    }

    checkLimits();
    // Re-check every 5 minutes
    const interval = setInterval(checkLimits, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const visibleAlerts = alerts.filter((a) => !dismissed.has(a.metric));

  if (visibleAlerts.length === 0) return null;

  return (
    <div className="space-y-2">
      {visibleAlerts.map((alert) => {
        const pct = Math.round((alert.current / alert.limit) * 100);
        const label = METRIC_LABELS[alert.metric] || alert.metric;
        const isUrgent = pct >= 95;

        return (
          <div
            key={alert.metric}
            className={`flex items-center justify-between gap-4 rounded-lg border px-4 py-3 ${
              isUrgent
                ? "border-red-800 bg-red-950/50"
                : "border-amber-800 bg-amber-950/30"
            }`}
          >
            <div className="flex items-center gap-3 min-w-0">
              <TrendingUp className={`h-4 w-4 shrink-0 ${isUrgent ? "text-red-400" : "text-amber-400"}`} />
              <div className="min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {isUrgent ? `Limit reached: ${label}` : `Approaching limit: ${label}`}
                </p>
                <p className="text-xs text-neutral-400">
                  {alert.current} / {alert.limit} used ({pct}%) · {alert.plan} plan
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button size="sm" asChild>
                <Link href="/dashboard/billing">Upgrade</Link>
              </Button>
              <button
                onClick={() => setDismissed((prev) => new Set([...prev, alert.metric]))}
                className="text-neutral-500 hover:text-neutral-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
