"use client";

import { useEffect, useMemo, useState } from "react";
import {
  listTreatments,
  getTreatmentDetail,
  type TreatmentSummary,
  type TreatmentDetail,
} from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { getAccessToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Bug,
  Leaf,
  Thermometer,
  FlaskConical,
  AlertTriangle,
  ChevronRight,
  Shield,
  Clock,
  Loader2,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const CATEGORY_CONFIG: Record<string, { label: string; icon: typeof Bug; color: string }> = {
  deficiency: { label: "Deficiencies", icon: Leaf, color: "text-yellow-500" },
  toxicity: { label: "Toxicities", icon: FlaskConical, color: "text-purple-500" },
  pest: { label: "Pests", icon: Bug, color: "text-red-500" },
  disease: { label: "Diseases", icon: AlertTriangle, color: "text-orange-500" },
  environmental: { label: "Environmental", icon: Thermometer, color: "text-blue-500" },
};

const SEVERITY_COLORS: Record<string, string> = {
  low: "bg-blue-500/10 text-blue-600 border-blue-500/30",
  medium: "bg-yellow-500/10 text-yellow-600 border-yellow-500/30",
  high: "bg-orange-500/10 text-orange-600 border-orange-500/30",
  critical: "bg-red-500/10 text-red-600 border-red-500/30",
};

interface TreatmentDatabaseProps {
  growType?: string;
}

export function TreatmentDatabase({ growType }: TreatmentDatabaseProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<TreatmentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(searchQuery.trim()), 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const {
    data,
    isLoading: loading,
  } = useApiSWR<{ items: TreatmentSummary[] }>(
    ["treatments", activeCategory, debouncedQuery],
    (token) => {
      const params: { category?: string; query?: string } = {};
      if (activeCategory !== "all") params.category = activeCategory;
      if (debouncedQuery) params.query = debouncedQuery;
      return listTreatments(token, params);
    },
  );

  const openDetail = async (id: string) => {
    setSelectedId(id);
    setDetailLoading(true);
    const token = getAccessToken();
    if (!token) return;
    try {
      const res = await getTreatmentDetail(token, id, growType);
      setDetail(res);
    } catch {
      // ignore
    }
    setDetailLoading(false);
  };

  const filteredTreatments = useMemo(() => data?.items ?? [], [data]);

  return (
    <div className="space-y-4">
      {/* Search & Filter */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search issues (e.g. yellow leaves, mites, pH)..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Category Tabs */}
      <Tabs value={activeCategory} onValueChange={setActiveCategory}>
        <TabsList className="flex-wrap h-auto gap-1">
          <TabsTrigger value="all" className="gap-1.5">
            <Zap className="size-3.5" />
            All
          </TabsTrigger>
          {Object.entries(CATEGORY_CONFIG).map(([key, cfg]) => (
            <TabsTrigger key={key} value={key} className="gap-1.5">
              <cfg.icon className={cn("size-3.5", cfg.color)} />
              {cfg.label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent value={activeCategory} className="mt-4">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="size-6 animate-spin text-muted-foreground" />
            </div>
          ) : filteredTreatments.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No treatments found. Try a different search.
            </div>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {filteredTreatments.map((t) => {
                const cfg = CATEGORY_CONFIG[t.category];
                const Icon = cfg?.icon ?? AlertTriangle;
                return (
                  <Card
                    key={t.id}
                    className="cursor-pointer hover:border-primary/50 transition-colors"
                    onClick={() => openDetail(t.id)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <div className={cn("mt-0.5", cfg?.color ?? "text-muted-foreground")}>
                          <Icon className="size-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-medium text-sm truncate">{t.name}</h3>
                            <ChevronRight className="size-3.5 text-muted-foreground shrink-0" />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{t.summary}</p>
                          <Badge variant="outline" className="mt-2 text-[10px]">
                            {cfg?.label ?? t.category}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Detail Dialog */}
      <Dialog open={!!selectedId} onOpenChange={(open) => { if (!open) { setSelectedId(null); setDetail(null); } }}>
        <DialogContent className="max-w-2xl max-h-[85dvh] overflow-y-auto">
          {detailLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="size-6 animate-spin" />
            </div>
          ) : detail ? (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  {(() => {
                    const cfg = CATEGORY_CONFIG[detail.category];
                    const Icon = cfg?.icon ?? AlertTriangle;
                    return <Icon className={cn("size-5", cfg?.color)} />;
                  })()}
                  {detail.name}
                </DialogTitle>
                {detail.aka.length > 0 && (
                  <p className="text-sm text-muted-foreground">
                    Also known as: {detail.aka.join(", ")}
                  </p>
                )}
              </DialogHeader>

              <div className="space-y-5 mt-2">
                {/* Summary */}
                <p className="text-sm">{detail.summary}</p>

                {/* Symptoms */}
                <section>
                  <h4 className="font-semibold text-sm mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="size-4 text-yellow-500" />
                    Symptoms
                  </h4>
                  <ul className="space-y-1">
                    {detail.symptoms.map((s, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex gap-2">
                        <span className="text-yellow-500 shrink-0">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </section>

                {/* Identification Tips */}
                <section>
                  <h4 className="font-semibold text-sm mb-2 flex items-center gap-1.5">
                    <Search className="size-4 text-primary" />
                    How to Identify
                  </h4>
                  <ul className="space-y-1">
                    {detail.identification_tips.map((tip, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex gap-2">
                        <span className="text-primary shrink-0">→</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </section>

                {/* Severity Scale */}
                <section>
                  <h4 className="font-semibold text-sm mb-2">Severity Scale</h4>
                  <div className="grid gap-2">
                    {Object.entries(detail.severity_criteria).map(([level, desc]) => (
                      <div key={level} className="flex items-start gap-2">
                        <Badge variant="outline" className={cn("shrink-0 text-[10px] uppercase", SEVERITY_COLORS[level])}>
                          {level}
                        </Badge>
                        <span className="text-sm text-muted-foreground">{desc}</span>
                      </div>
                    ))}
                  </div>
                </section>

                {/* Treatments */}
                <section>
                  <h4 className="font-semibold text-sm mb-2 flex items-center gap-1.5">
                    <Zap className="size-4 text-green-500" />
                    Treatment
                    {growType && <Badge variant="outline" className="text-[10px] ml-1">for your grow type</Badge>}
                  </h4>
                  {Object.entries(detail.treatments).map(([type, steps]) => (
                    <div key={type} className="mb-3">
                      <p className="text-xs font-medium text-muted-foreground uppercase mb-1">
                        {type.replace(/_/g, " ")}
                      </p>
                      <ol className="space-y-1">
                        {steps.map((step, i) => (
                          <li key={i} className="text-sm flex gap-2">
                            <span className="text-green-500 font-medium shrink-0">{i + 1}.</span>
                            {step}
                          </li>
                        ))}
                      </ol>
                    </div>
                  ))}
                </section>

                {/* Prevention */}
                <section>
                  <h4 className="font-semibold text-sm mb-2 flex items-center gap-1.5">
                    <Shield className="size-4 text-blue-500" />
                    Prevention
                  </h4>
                  <ul className="space-y-1">
                    {detail.prevention.map((p, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex gap-2">
                        <span className="text-blue-500 shrink-0">✓</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </section>

                {/* Recovery & Confusion */}
                <div className="grid gap-3 sm:grid-cols-2">
                  <Card>
                    <CardContent className="p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <Clock className="size-3.5 text-muted-foreground" />
                        <span className="text-xs font-medium">Recovery Time</span>
                      </div>
                      <p className="text-sm text-muted-foreground">{detail.recovery_time}</p>
                    </CardContent>
                  </Card>
                  {detail.commonly_confused_with.length > 0 && (
                    <Card>
                      <CardContent className="p-3">
                        <span className="text-xs font-medium">Often Confused With</span>
                        <ul className="mt-1">
                          {detail.commonly_confused_with.map((c, i) => (
                            <li key={i} className="text-sm text-muted-foreground">• {c}</li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Causes */}
                <section>
                  <h4 className="font-semibold text-sm mb-2">Common Causes</h4>
                  <ul className="space-y-1">
                    {detail.causes.map((c, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex gap-2">
                        <span className="shrink-0">•</span>
                        {c}
                      </li>
                    ))}
                  </ul>
                </section>
              </div>
            </>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}
