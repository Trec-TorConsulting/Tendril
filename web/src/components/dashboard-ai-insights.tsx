"use client";

import { useMemo, useState, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import { getAiInsight, getCoachTip, type InsightType } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Bot, RefreshCw, Sparkles } from "lucide-react";

const FLOWER_STAGES = new Set(["flowering", "ripening", "harvesting"]);

type InsightPayload = {
  result: unknown;
  generatedAt: string;
  cached: boolean;
};

type DashboardAiPayload = {
  coachTip: string | null;
  coachGeneratedAt: string | null;
  coachCached: boolean;
  insights: Partial<Record<InsightType, InsightPayload>>;
};

export function DashboardAiInsights({
  growId,
  growStage,
  hasSensorData,
}: {
  growId: string;
  growStage?: string;
  hasSensorData: boolean;
}) {
  const [refreshNonce, setRefreshNonce] = useState(0);

  const showHarvest = growStage ? FLOWER_STAGES.has(growStage) : false;
  const showAnomaly = hasSensorData;
  const forceRefresh = refreshNonce > 0;

  const { data, isLoading, mutate } = useApiSWR(
    ["dashboard", "ai-insights", growId, growStage ?? "unknown", hasSensorData, refreshNonce],
    async (token) => {
      const insights: Partial<Record<InsightType, InsightPayload>> = {};

      const coachRes = await getCoachTip(token, growId, forceRefresh);

      if (showHarvest) {
        insights.harvest_predict = await loadInsight(token, growId, "harvest_predict", forceRefresh);
      }

      insights.nutrient_advice = await loadInsight(token, growId, "nutrient_advice", forceRefresh);

      if (showAnomaly) {
        insights.anomaly_scan = await loadInsight(token, growId, "anomaly_scan", forceRefresh);
      }

      return {
        coachTip: coachRes.tip,
        coachGeneratedAt: coachRes.generated_at,
        coachCached: coachRes.cached,
        insights,
      } satisfies DashboardAiPayload;
    },
  );

  const insightCards = useMemo(() => {
    if (!data) return [] as Array<{ key: string; title: string; payload: InsightPayload | undefined }>;
    const cards: Array<{ key: string; title: string; payload: InsightPayload | undefined }> = [];

    if (showHarvest) {
      cards.push({ key: "harvest_predict", title: "Harvest Outlook", payload: data.insights.harvest_predict });
    }

    cards.push({ key: "nutrient_advice", title: "Nutrient Advice", payload: data.insights.nutrient_advice });

    if (showAnomaly) {
      cards.push({ key: "anomaly_scan", title: "Anomaly Scan", payload: data.insights.anomaly_scan });
    }

    return cards;
  }, [data, showAnomaly, showHarvest]);

  const refresh = async () => {
    setRefreshNonce((v) => v + 1);
    await mutate();
  };

  return (
    <Card className="border-border/50 backdrop-blur-sm">
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <Bot className="size-4 text-primary" />
            AI Guidance
          </CardTitle>
          <Button type="button" variant="ghost" size="sm" onClick={refresh} className="gap-1 text-xs">
            <RefreshCw className="size-3.5" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-lg border border-primary/20 bg-primary/5 p-3">
          <div className="mb-1 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-primary">
            <Sparkles className="size-3.5" />
            Coach Tip
          </div>
          {isLoading && !data ? (
            <p className="text-sm text-muted-foreground">Generating your latest tip...</p>
          ) : (
            <>
              <p className="text-sm leading-relaxed">
                {data?.coachTip ?? "No coach tip available yet. Refresh to generate one."}
              </p>
              {data?.coachGeneratedAt ? (
                <p className="mt-2 text-[11px] text-muted-foreground">
                  Updated {timeAgo(data.coachGeneratedAt)} {data.coachCached ? "(cached)" : "(fresh)"}
                </p>
              ) : null}
            </>
          )}
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {insightCards.map((card) => (
            <div key={card.key} className="rounded-lg border bg-card p-3">
              <div className="mb-1.5 flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{card.title}</p>
                <Badge variant="outline" className="text-[10px]">
                  {card.payload?.generatedAt ? `${timeAgo(card.payload.generatedAt)} ${card.payload.cached ? "cached" : "fresh"}` : "pending"}
                </Badge>
              </div>
              <InsightBody value={card.payload?.result} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

async function loadInsight(
  token: string,
  growId: string,
  type: InsightType,
  forceRefresh: boolean,
): Promise<InsightPayload> {
  const response = await getAiInsight(token, growId, type, forceRefresh);
  return {
    result: response.result,
    generatedAt: response.generated_at,
    cached: response.cached,
  };
}

function InsightBody({ value }: { value: unknown }): ReactNode {
  if (value == null || (typeof value === "string" && !value.trim())) {
    return <p className="text-xs text-muted-foreground">No insight available yet.</p>;
  }

  const obj = coerceToObject(value);
  if (obj) {
    const structured = formatStructured(obj);
    if (structured) return structured;
  }

  const prose = typeof value === "string" ? extractProse(value) : "";
  if (prose) {
    return (
      <div className="prose prose-sm dark:prose-invert max-h-28 max-w-none overflow-hidden text-xs leading-relaxed text-muted-foreground [&_*]:text-xs [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
        <ReactMarkdown>{prose}</ReactMarkdown>
      </div>
    );
  }

  return <p className="line-clamp-4 text-xs text-muted-foreground">{fallbackText(value)}</p>;
}

function formatStructured(obj: Record<string, unknown>): ReactNode | null {
  const adjustments = asArray(obj.adjustments);
  if (adjustments) {
    if (adjustments.length === 0) {
      return <p className="text-xs text-muted-foreground">No feeding adjustments needed right now.</p>;
    }
    return (
      <div className="space-y-1.5">
        <ul className="space-y-1">
          {adjustments.slice(0, 4).map((raw, i) => {
            const adj = asRecord(raw);
            return (
              <li key={i} className="flex flex-wrap items-baseline gap-x-1 text-xs">
                <span className="font-medium text-foreground">{humanize(adj?.nutrient)}</span>
                {adj?.action != null ? <span className="text-muted-foreground">— {humanize(adj.action)}</span> : null}
                {adj?.amount != null ? <span className="text-muted-foreground">({String(adj.amount)})</span> : null}
              </li>
            );
          })}
        </ul>
        {typeof obj.reasoning === "string" && obj.reasoning.trim() ? (
          <p className="line-clamp-2 text-[11px] text-muted-foreground/80">{obj.reasoning}</p>
        ) : null}
      </div>
    );
  }

  const anomalies = asArray(obj.anomalies);
  if (anomalies) {
    if (anomalies.length === 0) {
      return <p className="text-xs text-muted-foreground">No anomalies detected.</p>;
    }
    return (
      <ul className="space-y-1">
        {anomalies.slice(0, 4).map((raw, i) => {
          const a = asRecord(raw);
          return (
            <li key={i} className="text-xs">
              <span className="font-medium text-foreground">{humanize(a?.sensor)}</span>
              {a?.value != null ? <span className="text-muted-foreground"> · {String(a.value)}</span> : null}
              {a?.severity != null ? <span className={severityClass(String(a.severity))}> · {String(a.severity)}</span> : null}
              {typeof a?.recommendation === "string" && a.recommendation ? (
                <span className="text-muted-foreground"> — {a.recommendation}</span>
              ) : null}
            </li>
          );
        })}
      </ul>
    );
  }

  if (obj.estimated_date != null || obj.days_remaining != null || obj.trichome_target != null) {
    return (
      <div className="space-y-0.5 text-xs">
        {obj.days_remaining != null ? (
          <p>
            <span className="font-medium text-foreground">{String(obj.days_remaining)} days</span>{" "}
            <span className="text-muted-foreground">remaining</span>
          </p>
        ) : null}
        {obj.estimated_date != null ? <p className="text-muted-foreground">Est. harvest {String(obj.estimated_date)}</p> : null}
        {obj.trichome_target != null ? <p className="text-muted-foreground">Target: {humanize(obj.trichome_target)}</p> : null}
        {typeof obj.notes === "string" && obj.notes.trim() ? (
          <p className="line-clamp-2 text-muted-foreground/80">{obj.notes}</p>
        ) : null}
      </div>
    );
  }

  for (const key of ["summary", "recommendation", "reasoning", "notes"] as const) {
    const v = obj[key];
    if (typeof v === "string" && v.trim()) {
      return <p className="line-clamp-4 text-xs text-muted-foreground">{v}</p>;
    }
  }

  return null;
}

/** Return a plain object from a value that is already an object, or a JSON string the LLM may have wrapped in prose/markdown. */
function coerceToObject(value: unknown): Record<string, unknown> | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  if (typeof value !== "string") return null;

  const trimmed = value.trim();
  const candidates = [trimmed];
  const fence = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) candidates.push(fence[1]);
  const brace = trimmed.match(/\{[\s\S]*\}/);
  if (brace) candidates.push(brace[0]);

  for (const candidate of candidates) {
    try {
      const parsed = JSON.parse(candidate);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        return parsed as Record<string, unknown>;
      }
    } catch {
      // Not valid JSON — try the next candidate.
    }
  }
  return null;
}

/** Strip markdown code fences and any trailing raw JSON blob so only readable prose remains. */
function extractProse(text: string): string {
  const withoutFences = text.replace(/```[\s\S]*?```/g, " ").replace(/```[\s\S]*$/g, " ");
  const jsonStart = withoutFences.search(/\{\s*"/);
  const prose = jsonStart === -1 ? withoutFences : withoutFences.slice(0, jsonStart);
  return prose.replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
}

function fallbackText(value: unknown): string {
  const obj = coerceToObject(value);
  if (obj) {
    const parts = Object.entries(obj)
      .filter(([, v]) => v != null && typeof v !== "object")
      .map(([k, v]) => `${humanize(k)}: ${String(v)}`);
    if (parts.length) return parts.join(" · ");
  }
  return typeof value === "string" ? value.trim() : "No insight available yet.";
}

function asArray(value: unknown): unknown[] | null {
  return Array.isArray(value) ? value : null;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function humanize(value: unknown): string {
  if (value == null) return "";
  const s = String(value).replace(/_/g, " ").trim();
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
}

function severityClass(severity: string): string {
  const s = severity.toLowerCase();
  if (s === "high" || s === "critical") return "font-medium text-destructive";
  if (s === "medium" || s === "moderate") return "font-medium text-yellow-700 dark:text-yellow-400";
  return "text-muted-foreground";
}

function timeAgo(timestamp: string): string {
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
