"use client";

import { useEffect, useState } from "react";
import { ArrowDown, ArrowUp, GitCompare, Minus } from "lucide-react";
import { toast } from "sonner";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/page-header";
import { apiFetch, type GrowResponse, listGrows } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";

const METRICS = [
  { value: "ph", label: "pH", unit: "" },
  { value: "ec", label: "EC", unit: "mS/cm" },
  { value: "vpd", label: "VPD", unit: "kPa" },
  { value: "temp", label: "Temperature", unit: "°F" },
  { value: "humidity", label: "Humidity", unit: "%" },
  { value: "water_temp", label: "Water Temp", unit: "°F" },
];

const COLORS = ["#8b5cf6", "#22c55e", "#f59e0b", "#ef4444"];

interface TimeSeriesPoint {
  day: number;
  value: number | null;
}

interface GrowTimeSeries {
  grow_id: string;
  grow_name: string;
  data: TimeSeriesPoint[];
}

interface GrowSummary {
  grow_id: string;
  grow_name: string;
  grow_type: string;
  strain_name: string | null;
  stage: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  duration_days: number | null;
  avg_ph: number | null;
  avg_ec: number | null;
  avg_vpd: number | null;
  avg_temp_f: number | null;
  avg_humidity: number | null;
  total_dry_weight_oz: number | null;
  avg_quality: number | null;
}

interface CompareResponse {
  metric: string;
  grows: GrowTimeSeries[];
  summaries: GrowSummary[];
}

export default function SeasonComparisonPage() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [metric, setMetric] = useState("ph");
  const { data: growsData, isLoading: growsLoading, error: growsError } = useApiSWR(
    ["analytics", "compare", "grows"],
    (token) => listGrows(token),
  );
  const grows: GrowResponse[] = growsData ?? [];

  const {
    data: compareData,
    isLoading: loading,
    error: compareError,
  } = useApiSWR(
    selectedIds.length >= 2
      ? ["analytics", "compare", metric, ...selectedIds]
      : null,
    async (token) => {
      const params = new URLSearchParams();
      selectedIds.forEach((id) => params.append("grow_id", id));
      params.set("metric", metric);
      return apiFetch<CompareResponse>(`/analytics/compare?${params.toString()}`, { token });
    },
  );

  useEffect(() => {
    if (growsError) {
      toast.error("Failed to load grows");
    }
  }, [growsError]);

  useEffect(() => {
    if (compareError) {
      toast.error("Failed to load comparison data");
    }
  }, [compareError]);

  // Build chart data (merge all series into single dataset by day)
  const chartData = compareData
    ? (() => {
        const maxDay = Math.max(...compareData.grows.map((g) => g.data.length), 0);
        const rows: Record<string, number | null>[] = [];
        for (let d = 0; d < maxDay; d++) {
          const row: Record<string, number | null> = { day: d + 1 };
          compareData.grows.forEach((g) => {
            row[g.grow_name] = g.data[d]?.value ?? null;
          });
          rows.push(row);
        }
        return rows;
      })()
    : [];

  const toggleGrow = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 4) {
        toast.error("Maximum 4 grows for comparison");
        return prev;
      }
      return [...prev, id];
    });
  };

  const metricInfo = METRICS.find((m) => m.value === metric);

  return (
    <div className="space-y-6 p-6">
      <PageHeader
        title="Season Comparison"
        description="Compare grows side-by-side with normalized time-series"
      />

      {/* Controls */}
      <div className="flex flex-wrap gap-4">
        <div className="w-48">
          <Select value={metric} onValueChange={(v) => setMetric(v ?? "ph")}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {METRICS.map((m) => (
                <SelectItem key={m.value} value={m.value}>
                  {m.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Grow Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitCompare className="h-5 w-5" />
            Select Grows to Compare (2-4)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {growsLoading ? (
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-14 rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {grows.map((g) => {
                const selected = selectedIds.includes(g.id);
                const colorIdx = selectedIds.indexOf(g.id);
                return (
                  <Button
                    key={g.id}
                    variant={selected ? "default" : "outline"}
                    className="h-auto justify-start py-2 text-left"
                    style={selected ? { backgroundColor: COLORS[colorIdx] } : undefined}
                    onClick={() => toggleGrow(g.id)}
                  >
                    <div>
                      <div className="font-medium">{g.name}</div>
                      <div className="text-xs opacity-75">
                        {g.grow_type} • {g.status} • {g.started_at ? new Date(g.started_at).toLocaleDateString() : ""}
                      </div>
                    </div>
                  </Button>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chart */}
      {selectedIds.length >= 2 && (
        <Card>
          <CardHeader>
            <CardTitle>
              {metricInfo?.label} — Day-in-Grow Comparison
              {metricInfo?.unit && <span className="ml-2 text-sm font-normal text-muted-foreground">({metricInfo.unit})</span>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-72 w-full rounded-lg" />
            ) : chartData.length === 0 ? (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                No data available for the selected grows and metric
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={320} minWidth={0}>
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis
                    dataKey="day"
                    tick={{ fontSize: 11 }}
                    label={{ value: "Day in Grow", position: "insideBottom", offset: -5, style: { fontSize: 11 } }}
                  />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  {compareData?.grows.map((g, i) => (
                    <Line
                      key={g.grow_id}
                      type="monotone"
                      dataKey={g.grow_name}
                      stroke={COLORS[i % COLORS.length]}
                      strokeWidth={2}
                      dot={false}
                      connectNulls
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      )}

      {/* Summary Table */}
      {compareData && compareData.summaries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Summary Statistics</CardTitle>
          </CardHeader>
          <CardContent className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left">
                  <th className="pb-2 pr-4 font-medium">Grow</th>
                  <th className="pb-2 pr-4 font-medium">Duration</th>
                  <th className="pb-2 pr-4 font-medium">Avg pH</th>
                  <th className="pb-2 pr-4 font-medium">Avg EC</th>
                  <th className="pb-2 pr-4 font-medium">Avg VPD</th>
                  <th className="pb-2 pr-4 font-medium">Yield (oz)</th>
                  <th className="pb-2 pr-4 font-medium">Quality</th>
                </tr>
              </thead>
              <tbody>
                {compareData.summaries.map((s, i) => (
                  <tr key={s.grow_id} className="border-b last:border-0">
                    <td className="py-2 pr-4">
                      <div className="flex items-center gap-2">
                        <div
                          className="h-3 w-3 rounded-full"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        <div>
                          <div className="font-medium">{s.grow_name}</div>
                          <div className="text-xs text-muted-foreground">{s.strain_name || s.grow_type}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-2 pr-4">{s.duration_days ? `${s.duration_days}d` : "—"}</td>
                    <td className="py-2 pr-4">{s.avg_ph?.toFixed(2) ?? "—"}</td>
                    <td className="py-2 pr-4">{s.avg_ec?.toFixed(2) ?? "—"}</td>
                    <td className="py-2 pr-4">{s.avg_vpd?.toFixed(2) ?? "—"}</td>
                    <td className="py-2 pr-4">{s.total_dry_weight_oz?.toFixed(1) ?? "—"}</td>
                    <td className="py-2 pr-4">
                      {s.avg_quality ? (
                        <Badge variant="outline">{s.avg_quality.toFixed(1)}/10</Badge>
                      ) : (
                        "—"
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Improvement Indicators */}
            {compareData.summaries.length === 2 && (
              <div className="mt-4 rounded-lg border p-3">
                <h4 className="mb-2 text-sm font-medium">Improvement vs Previous</h4>
                <div className="flex flex-wrap gap-4">
                  {_renderDelta("Yield", compareData.summaries[0].total_dry_weight_oz, compareData.summaries[1].total_dry_weight_oz, "oz", true)}
                  {_renderDelta("pH", compareData.summaries[0].avg_ph, compareData.summaries[1].avg_ph, "", false)}
                  {_renderDelta("EC", compareData.summaries[0].avg_ec, compareData.summaries[1].avg_ec, "", false)}
                  {_renderDelta("VPD", compareData.summaries[0].avg_vpd, compareData.summaries[1].avg_vpd, "kPa", false)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {selectedIds.length < 2 && !growsLoading && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Select at least 2 grows above to see the comparison chart and statistics.
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function _renderDelta(
  label: string,
  newer: number | null | undefined,
  older: number | null | undefined,
  unit: string,
  higherIsBetter: boolean,
) {
  if (newer == null || older == null || older === 0) return null;
  const diff = newer - older;
  const pct = ((diff / Math.abs(older)) * 100).toFixed(0);
  const improved = higherIsBetter ? diff > 0 : Math.abs(diff) < 0.01;
  const regressed = higherIsBetter ? diff < 0 : false;

  return (
    <div className="flex items-center gap-1 text-sm">
      <span className="text-muted-foreground">{label}:</span>
      {diff > 0 ? (
        <ArrowUp className={`h-3 w-3 ${improved ? "text-green-500" : "text-red-500"}`} />
      ) : diff < 0 ? (
        <ArrowDown className={`h-3 w-3 ${regressed ? "text-red-500" : "text-green-500"}`} />
      ) : (
        <Minus className="h-3 w-3 text-muted-foreground" />
      )}
      <span className={improved ? "text-green-600" : regressed ? "text-red-600" : ""}>
        {diff > 0 ? "+" : ""}
        {diff.toFixed(1)}
        {unit} ({pct}%)
      </span>
    </div>
  );
}
