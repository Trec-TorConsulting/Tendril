"use client";

import { useMemo, useState } from "react";
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
          {insightCards.map((card) => {
            const summary = summarizeInsight(card.payload?.result);
            return (
              <div key={card.key} className="rounded-lg border bg-card p-3">
                <div className="mb-1.5 flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">{card.title}</p>
                  <Badge variant="outline" className="text-[10px]">
                    {card.payload?.generatedAt ? `${timeAgo(card.payload.generatedAt)} ${card.payload.cached ? "cached" : "fresh"}` : "pending"}
                  </Badge>
                </div>
                <p className="line-clamp-4 text-xs text-muted-foreground">{summary}</p>
              </div>
            );
          })}
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

function summarizeInsight(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  if (value && typeof value === "object") {
    const v = value as Record<string, unknown>;
    if (typeof v.summary === "string") {
      return v.summary;
    }
    if (typeof v.recommendation === "string") {
      return v.recommendation;
    }
    return JSON.stringify(v);
  }

  return "No insight available yet.";
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
