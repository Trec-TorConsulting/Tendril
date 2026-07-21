"use client";

import { useMemo, useState, type ComponentType, type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import {
  Activity,
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Bot,
  CalendarIcon,
  CheckCircle2,
  FlaskConical,
  Gauge,
  Loader2,
  Minus,
  Plus,
  RefreshCw,
  Scissors,
  ShieldCheck,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { createTask, getAiInsight, getCoachTip, type InsightType } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useChat } from "@/components/chat-provider";
import { cn } from "@/lib/utils";

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

type InsightCardModel = { key: string; title: string; payload: InsightPayload | undefined };
type IconType = ComponentType<{ className?: string }>;
type Tone = "critical" | "warning" | "good" | "neutral";
type TrendMap = Record<string, number[]>;

export function DashboardAiInsights({
  growId,
  growStage,
  hasSensorData,
  sensorTrends,
}: {
  growId: string;
  growStage?: string;
  hasSensorData: boolean;
  sensorTrends?: TrendMap;
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

    // Severity-first: float a critical anomaly card to the top so it can't be missed.
    const anomalyIdx = cards.findIndex((c) => c.key === "anomaly_scan");
    if (anomalyIdx > 0 && isCriticalAnomaly(cards[anomalyIdx].payload?.result)) {
      const [critical] = cards.splice(anomalyIdx, 1);
      cards.unshift(critical);
    }

    return cards;
  }, [data, showAnomaly, showHarvest]);

  const refresh = async () => {
    setRefreshNonce((v) => v + 1);
    await mutate();
  };

  return (
    <Card className="overflow-hidden border-border/50 backdrop-blur-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-base">
            <span className="inline-flex size-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Bot className="size-4" />
            </span>
            AI Guidance
          </CardTitle>
          <Button type="button" variant="ghost" size="sm" onClick={refresh} className="gap-1 text-xs">
            <RefreshCw className="size-3.5" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Coach tip hero */}
        <div className="relative overflow-hidden rounded-xl border border-primary/20 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent p-4">
          <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
            <Sparkles className="size-3.5" />
            Coach Tip
          </div>
          {isLoading && !data ? (
            <p className="text-sm text-muted-foreground">Generating your latest tip…</p>
          ) : (
            <>
              <p className="text-sm leading-relaxed text-foreground">
                {data?.coachTip ?? "No coach tip available yet. Tap Refresh to generate one."}
              </p>
              {data?.coachGeneratedAt ? (
                <p className="mt-2 text-[11px] text-muted-foreground">
                  Updated {timeAgo(data.coachGeneratedAt)} · {data.coachCached ? "cached" : "fresh"}
                </p>
              ) : null}
            </>
          )}
        </div>

        {/* Insight cards */}
        {isLoading && !data ? (
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <Skeleton key={i} className="h-32 rounded-xl" />
            ))}
          </div>
        ) : insightCards.length > 0 ? (
          <div className="grid items-stretch gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {insightCards.map((card) => (
              <InsightCard key={card.key} card={card} growId={growId} sensorTrends={sensorTrends} />
            ))}
          </div>
        ) : null}
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

// ── Insight card ─────────────────────────────────────────────────────

const TONE_STYLES: Record<Tone, { card: string; icon: string }> = {
  critical: { card: "border-destructive/40 bg-destructive/5", icon: "text-destructive" },
  warning: { card: "border-amber-500/40 bg-amber-500/5", icon: "text-amber-600 dark:text-amber-400" },
  good: { card: "border-emerald-500/30 bg-emerald-500/5", icon: "text-emerald-600 dark:text-emerald-400" },
  neutral: { card: "border-border bg-card", icon: "text-primary" },
};

function InsightCard({
  card,
  growId,
  sensorTrends,
}: {
  card: InsightCardModel;
  growId: string;
  sensorTrends?: TrendMap;
}): ReactNode {
  const { openChatWith } = useChat();
  const [taskState, setTaskState] = useState<"idle" | "creating" | "done">("idle");
  const { Icon, tone, body, seed, task } = renderInsight(card.key, card.payload?.result, sensorTrends);
  const styles = TONE_STYLES[tone];

  const handleCreateTask = async () => {
    if (!task || taskState !== "idle") return;
    const token = getAccessToken();
    if (!token) {
      toast.error("Please sign in to create a task.");
      return;
    }
    setTaskState("creating");
    try {
      await createTask(
        {
          title: task.title,
          description: task.description || undefined,
          priority: task.priority,
          category: "alert_response",
          grow_cycle_id: growId,
        },
        token,
      );
      setTaskState("done");
      toast.success("Task added to your list.");
    } catch (e) {
      setTaskState("idle");
      toast.error(e instanceof Error ? e.message : "Failed to create task.");
    }
  };

  const handleAsk = () => {
    if (seed) openChatWith(seed);
  };

  return (
    <div className={cn("flex flex-col rounded-xl border p-3.5 transition-colors", styles.card)}>
      <div className="mb-2 flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-1.5">
          <Icon className={cn("size-4 shrink-0", styles.icon)} />
          <p className="truncate text-sm font-semibold">{card.title}</p>
        </div>
        <FreshnessBadge payload={card.payload} />
      </div>
      <div className="flex-1">{body}</div>
      {seed || task ? (
        <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-border/60 pt-2.5">
          {task ? (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 gap-1 text-xs"
              onClick={handleCreateTask}
              disabled={taskState !== "idle"}
            >
              {taskState === "creating" ? (
                <Loader2 className="size-3 animate-spin" />
              ) : taskState === "done" ? (
                <CheckCircle2 className="size-3" />
              ) : (
                <Plus className="size-3" />
              )}
              {taskState === "done" ? "Task added" : "Create task"}
            </Button>
          ) : null}
          {seed ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 gap-1 text-xs text-muted-foreground"
              onClick={handleAsk}
            >
              <Sparkles className="size-3" />
              Ask
            </Button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function FreshnessBadge({ payload }: { payload: InsightPayload | undefined }): ReactNode {
  if (!payload?.generatedAt) {
    return (
      <Badge variant="outline" className="shrink-0 text-[10px]">
        pending
      </Badge>
    );
  }
  return (
    <Badge variant={payload.cached ? "outline" : "secondary"} className="shrink-0 text-[10px]">
      {timeAgo(payload.generatedAt)} · {payload.cached ? "cached" : "fresh"}
    </Badge>
  );
}

// ── Per-insight renderers ────────────────────────────────────────────

type Rendered = {
  Icon: IconType;
  tone: Tone;
  body: ReactNode;
  seed?: string;
  task?: { title: string; description: string; priority: string };
};

function renderInsight(key: string, value: unknown, sensorTrends?: TrendMap): Rendered {
  const fallbackIcon = iconForKey(key);
  const empty: Rendered = {
    Icon: fallbackIcon,
    tone: "neutral",
    body: <p className="text-xs text-muted-foreground">No insight yet — tap Refresh to generate one.</p>,
  };

  if (value == null || (typeof value === "string" && !value.trim())) return empty;

  const obj = coerceToObject(value);
  if (obj) {
    if (asArray(obj.adjustments)) return renderNutrient(obj, sensorTrends);
    if (asArray(obj.anomalies)) return renderAnomaly(obj, sensorTrends);
    if (obj.days_remaining != null || obj.estimated_date != null || obj.trichome_target != null) {
      return renderHarvest(obj);
    }
    const seed = `Tell me more about this ${labelForKey(key)}.`;
    const summary = firstString(obj, ["summary", "recommendation", "reasoning", "advice", "notes", "message"]);
    if (summary) {
      return { Icon: fallbackIcon, tone: "neutral", seed, body: <p className="text-xs leading-relaxed text-muted-foreground">{summary}</p> };
    }
    return { Icon: fallbackIcon, tone: "neutral", seed, body: <p className="line-clamp-4 text-xs text-muted-foreground">{fallbackText(value)}</p> };
  }

  const prose = typeof value === "string" ? extractProse(value) : "";
  if (prose) {
    return {
      Icon: fallbackIcon,
      tone: "neutral",
      seed: `Tell me more about this ${labelForKey(key)}.`,
      body: (
        <div className="prose prose-sm dark:prose-invert max-w-none text-xs leading-relaxed text-muted-foreground [&_*]:text-xs [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
          <ReactMarkdown>{prose}</ReactMarkdown>
        </div>
      ),
    };
  }

  return { ...empty, body: <p className="line-clamp-4 text-xs text-muted-foreground">{fallbackText(value)}</p> };
}

function labelForKey(key: string): string {
  if (key === "harvest_predict") return "harvest outlook";
  if (key === "nutrient_advice") return "nutrient advice";
  if (key === "anomaly_scan") return "anomaly scan";
  return "insight";
}

function iconForKey(key: string): IconType {
  if (key === "harvest_predict") return Scissors;
  if (key === "nutrient_advice") return FlaskConical;
  if (key === "anomaly_scan") return Activity;
  return Sparkles;
}

function renderHarvest(obj: Record<string, unknown>): Rendered {
  const days = obj.days_remaining;
  const seedParts: string[] = [];
  if (days != null) seedParts.push(`${String(days)} days out`);
  if (obj.trichome_target != null) seedParts.push(`target ${humanize(obj.trichome_target)}`);
  const seed = `Break down my harvest outlook${seedParts.length ? ` (${seedParts.join(", ")})` : ""} and what I should do now for peak quality.`;
  return {
    Icon: Scissors,
    tone: "neutral",
    seed,
    body: (
      <div className="space-y-2">
        {days != null ? (
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-bold leading-none tabular-nums">{String(days)}</span>
            <span className="text-xs text-muted-foreground">days to harvest</span>
          </div>
        ) : null}
        <div className="space-y-1 text-xs text-muted-foreground">
          {obj.estimated_date != null ? (
            <p className="flex items-center gap-1.5">
              <CalendarIcon className="size-3 shrink-0" />
              <span>Window {String(obj.estimated_date)}</span>
            </p>
          ) : null}
          {obj.trichome_target != null ? (
            <p className="flex items-center gap-1.5">
              <Gauge className="size-3 shrink-0" />
              <span>Target {humanize(obj.trichome_target)}</span>
            </p>
          ) : null}
        </div>
        {obj.confidence != null ? (
          <Badge variant="outline" className="text-[10px] capitalize">
            {String(obj.confidence)} confidence
          </Badge>
        ) : null}
        {typeof obj.notes === "string" && obj.notes.trim() ? (
          <p className="line-clamp-3 text-xs text-muted-foreground/80">{obj.notes}</p>
        ) : null}
      </div>
    ),
  };
}

function renderNutrient(obj: Record<string, unknown>, sensorTrends?: TrendMap): Rendered {
  const adjustments = asArray(obj.adjustments) ?? [];
  if (adjustments.length === 0) {
    return {
      Icon: FlaskConical,
      tone: "good",
      seed: "My feed looks on track — anything I can optimize for flower quality?",
      body: (
        <div className="space-y-2">
          <TrendStrip sensorTrends={sensorTrends} />
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <CheckCircle2 className="size-3.5 shrink-0 text-emerald-600 dark:text-emerald-400" />
            No feeding changes needed — hold your current mix.
          </p>
        </div>
      ),
    };
  }

  const seed = `Explain these feeding changes and why they help quality: ${adjustments
    .slice(0, 4)
    .map((raw) => {
      const a = asRecord(raw);
      return `${humanize(a?.nutrient)} ${humanize(a?.action)}`.trim();
    })
    .filter(Boolean)
    .join(", ")}.`;

  return {
    Icon: FlaskConical,
    tone: "neutral",
    seed,
    body: (
      <div className="space-y-2">
        <TrendStrip sensorTrends={sensorTrends} />
        <ul className="space-y-1">
          {adjustments.slice(0, 6).map((raw, i) => {
            const adj = asRecord(raw);
            const action = actionMeta(adj?.action);
            const detail = [humanize(adj?.action), adj?.amount != null ? String(adj.amount) : ""].filter(Boolean).join(" · ");
            return (
              <li key={i} className="flex items-start gap-1.5 rounded-md bg-background/60 px-2 py-1.5 text-xs">
                <action.Icon className={cn("mt-0.5 size-3.5 shrink-0", action.className)} />
                <span className="min-w-0">
                  <span className="font-medium text-foreground">{humanize(adj?.nutrient)}</span>
                  {detail ? <span className="text-muted-foreground"> — {detail}</span> : null}
                </span>
              </li>
            );
          })}
        </ul>
        {typeof obj.reasoning === "string" && obj.reasoning.trim() ? (
          <p className="line-clamp-3 text-[11px] leading-relaxed text-muted-foreground/80">{obj.reasoning}</p>
        ) : null}
      </div>
    ),
  };
}

function renderAnomaly(obj: Record<string, unknown>, sensorTrends?: TrendMap): Rendered {
  const anomalies = asArray(obj.anomalies) ?? [];
  if (anomalies.length === 0) {
    return {
      Icon: ShieldCheck,
      tone: "good",
      seed: "All readings look in range — what should I watch for at this stage?",
      body: (
        <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <ShieldCheck className="size-3.5 shrink-0 text-emerald-600 dark:text-emerald-400" />
          All readings in range — no anomalies detected.
        </p>
      ),
    };
  }

  const hasCritical = anomalies.some((raw) => {
    const sev = String(asRecord(raw)?.severity ?? "").toLowerCase();
    return sev === "high" || sev === "critical";
  });

  const top = pickMostSevere(anomalies);
  const task = {
    title: `Resolve ${humanize(top.sensor) || "sensor"} anomaly`,
    description: [
      top.value != null ? `Current: ${String(top.value)}` : "",
      top.expected_range != null ? `Expected: ${String(top.expected_range)}` : "",
      typeof top.recommendation === "string" ? top.recommendation : "",
    ]
      .filter(Boolean)
      .join(" — "),
    priority: hasCritical ? "high" : "medium",
  };
  const seed = `Help me resolve the anomalies you flagged: ${anomalies
    .slice(0, 4)
    .map((raw) => {
      const a = asRecord(raw);
      return `${humanize(a?.sensor)} ${a?.value != null ? String(a.value) : ""} (${String(a?.severity ?? "")})`
        .replace(/\s+/g, " ")
        .trim();
    })
    .join("; ")}. Give me the exact steps.`;

  return {
    Icon: AlertTriangle,
    tone: hasCritical ? "critical" : "warning",
    seed,
    task,
    body: (
      <ul className="space-y-1.5">
        {anomalies.slice(0, 6).map((raw, i) => {
          const a = asRecord(raw);
          const sev = severityMeta(a?.severity);
          const dir = trendDir(sensorTrends?.[trendKeyForSensor(a?.sensor) ?? ""]);
          return (
            <li key={i} className={cn("border-l-2 pl-2", sev.border)}>
              <div className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-xs">
                <span className="font-medium text-foreground">{humanize(a?.sensor)}</span>
                {a?.value != null ? (
                  <span className="inline-flex items-center gap-0.5 tabular-nums text-muted-foreground">
                    {String(a.value)}
                    <TrendArrow dir={dir} />
                  </span>
                ) : null}
                {a?.severity != null ? (
                  <Badge variant="outline" className={cn("text-[9px] capitalize", sev.text)}>
                    {String(a.severity)}
                  </Badge>
                ) : null}
              </div>
              {a?.expected_range != null ? (
                <p className="text-[11px] text-muted-foreground">Expected {String(a.expected_range)}</p>
              ) : null}
              {typeof a?.recommendation === "string" && a.recommendation ? (
                <p className="text-xs leading-relaxed text-foreground/80">{a.recommendation}</p>
              ) : null}
            </li>
          );
        })}
      </ul>
    ),
  };
}

// ── Action / severity metadata ───────────────────────────────────────

function actionMeta(action: unknown): { Icon: IconType; className: string } {
  const a = String(action ?? "").toLowerCase();
  if (/increase|raise|boost|add|bump|up/.test(a)) return { Icon: ArrowUp, className: "text-sky-600 dark:text-sky-400" };
  if (/decrease|reduce|lower|cut|flush|drop|down/.test(a)) return { Icon: ArrowDown, className: "text-amber-600 dark:text-amber-400" };
  return { Icon: Minus, className: "text-muted-foreground" };
}

function severityMeta(severity: unknown): { border: string; text: string } {
  const s = String(severity ?? "").toLowerCase();
  if (s === "high" || s === "critical") return { border: "border-destructive", text: "text-destructive" };
  if (s === "medium" || s === "moderate") return { border: "border-amber-500", text: "text-amber-600 dark:text-amber-400" };
  return { border: "border-muted-foreground/40", text: "text-muted-foreground" };
}

/** True when the anomaly payload contains at least one high/critical severity item. */
function isCriticalAnomaly(value: unknown): boolean {
  const obj = coerceToObject(value);
  const anomalies = obj ? asArray(obj.anomalies) : null;
  if (!anomalies) return false;
  return anomalies.some((raw) => {
    const sev = String(asRecord(raw)?.severity ?? "").toLowerCase();
    return sev === "high" || sev === "critical";
  });
}

/** Return the single most severe anomaly record. */
function pickMostSevere(anomalies: unknown[]): Record<string, unknown> {
  const rank = (sev: unknown): number => {
    const s = String(sev ?? "").toLowerCase();
    if (s === "high" || s === "critical") return 3;
    if (s === "medium" || s === "moderate") return 2;
    return 1;
  };
  let best = asRecord(anomalies[0]) ?? {};
  for (const raw of anomalies) {
    const a = asRecord(raw);
    if (a && rank(a.severity) > rank(best.severity)) best = a;
  }
  return best;
}

// ── Trends ───────────────────────────────────────────────────────────

type TrendDirection = "up" | "down" | "flat" | null;

/** Compare the latest reading to a short trailing window to detect direction. */
function trendDir(arr?: number[]): TrendDirection {
  if (!arr || arr.length < 3) return null;
  const latest = arr[arr.length - 1];
  const window = arr.slice(Math.max(0, arr.length - 6), arr.length - 1);
  if (window.length === 0) return null;
  const base = window.reduce((sum, v) => sum + v, 0) / window.length;
  if (!Number.isFinite(base) || base === 0) return "flat";
  const pct = (latest - base) / Math.abs(base);
  if (pct > 0.03) return "up";
  if (pct < -0.03) return "down";
  return "flat";
}

/** Map a free-text sensor name to a sensorTrends key. */
function trendKeyForSensor(name: unknown): string | null {
  const s = String(name ?? "").toLowerCase();
  if (s.includes("ph")) return "ph";
  if (s.includes("ec") || s.includes("conductivity")) return "ec";
  if (s.includes("ppm") || s.includes("tds")) return "ppm";
  if (s.includes("orp")) return "orp";
  if (s.includes("level")) return "water_level";
  if (s.includes("water") || s.includes("reservoir") || s.includes("res ")) return "water_temp";
  if (s.includes("humid") || s.includes("rh")) return "humidity";
  if (s.includes("temp")) return "temp";
  return null;
}

function TrendArrow({ dir }: { dir: TrendDirection }): ReactNode {
  if (!dir || dir === "flat") return null;
  const Icon = dir === "up" ? TrendingUp : TrendingDown;
  return <Icon className="size-3 text-muted-foreground" />;
}

function TrendStrip({ sensorTrends }: { sensorTrends?: TrendMap }): ReactNode {
  if (!sensorTrends) return null;
  const items = (
    [
      { label: "pH", dir: trendDir(sensorTrends.ph) },
      { label: "EC", dir: trendDir(sensorTrends.ec) },
    ] as const
  ).filter((it) => it.dir && it.dir !== "flat");
  if (items.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1.5 text-[11px] text-muted-foreground">
      {items.map((it) => (
        <span key={it.label} className="inline-flex items-center gap-0.5 rounded bg-background/60 px-1.5 py-0.5">
          {it.label}
          <TrendArrow dir={it.dir} />
          <span className="text-muted-foreground/70">{it.dir === "up" ? "rising" : "falling"}</span>
        </span>
      ))}
    </div>
  );
}

// ── Parsing helpers ──────────────────────────────────────────────────

/** Return a plain object from a value that is already an object, or a (possibly loose) JSON string the LLM may have wrapped in prose/markdown. */
function coerceToObject(value: unknown): Record<string, unknown> | null {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  if (typeof value !== "string") return null;

  const trimmed = value.trim();
  if (!trimmed) return null;

  const candidates: string[] = [];
  const fence = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fence) candidates.push(fence[1]);
  const brace = trimmed.match(/\{[\s\S]*\}/);
  if (brace) candidates.push(brace[0]);
  candidates.push(trimmed);

  for (const candidate of candidates) {
    const parsed = parseLoose(candidate);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  }
  return null;
}

/** Parse strict JSON, then fall back to a best-effort repair of common LLM mistakes (bare keys, trailing commas). */
function parseLoose(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    // fall through to repair
  }
  try {
    return JSON.parse(repairJson(text));
  } catch {
    return null;
  }
}

/** Quote unquoted object keys and strip trailing commas so LLM "JSON" with bare keys parses. */
function repairJson(text: string): string {
  return text
    .replace(/([{,]\s*)([A-Za-z_$][\w$]*)\s*:/g, '$1"$2":')
    .replace(/,\s*([}\]])/g, "$1");
}

/** Strip markdown fences and any trailing JSON-object blob so only readable prose remains. */
function extractProse(text: string): string {
  const withoutFences = text.replace(/```[\s\S]*?```/g, " ").replace(/```[\s\S]*$/g, " ");
  const jsonStart = withoutFences.search(/\{\s*(?:"[^"]*"|[A-Za-z_$][\w$]*)\s*:/);
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

function firstString(obj: Record<string, unknown>, keys: string[]): string | null {
  for (const key of keys) {
    const v = obj[key];
    if (typeof v === "string" && v.trim()) return v.trim();
  }
  return null;
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
