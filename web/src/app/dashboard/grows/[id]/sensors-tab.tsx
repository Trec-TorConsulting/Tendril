"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { formatShortDateTime } from "@/lib/utils";
import { listSensorReadings, deleteSensorReading, getSensorDrift, type SensorReadingResponse, type BucketResponse } from "@/lib/api";
import { useConfirm } from "@/components/confirm-dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Activity, TrendingUp, TrendingDown, Minus, Trash2 } from "lucide-react";
import { usePreferences } from "@/hooks/use-preferences";
import { tempUnitLabel } from "@/lib/units";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useApiSWR } from "@/lib/swr";

function getMetrics(tu: string) {
  return [
    { key: "ph", label: "pH", color: "#22c55e", unit: "" },
    { key: "ec", label: "EC", color: "#3b82f6", unit: " mS" },
    { key: "ppm", label: "PPM", color: "#f59e0b", unit: "" },
    { key: "water_temp_f", label: "Water Temp", color: "#ef4444", unit: tu },
    { key: "dissolved_oxygen", label: "DO", color: "#8b5cf6", unit: " mg/L" },
    { key: "orp", label: "ORP", color: "#06b6d4", unit: " mV" },
    { key: "water_level_pct", label: "Water Level", color: "#64748b", unit: "%" },
    { key: "soil_moisture", label: "Soil Moisture", color: "#84cc16", unit: "%" },
    { key: "soil_temp", label: "Soil Temp", color: "#d946ef", unit: tu },
    { key: "runoff_ph", label: "Runoff pH", color: "#14b8a6", unit: "" },
    { key: "runoff_ec", label: "Runoff EC", color: "#0ea5e9", unit: " mS" },
  ] as const;
}

const TIME_RANGES = [
  { label: "24h", limit: 96 },
  { label: "7d", limit: 672 },
  { label: "30d", limit: 2880 },
  { label: "All", limit: 10000 },
];

type DriftSnapshot = {
  min: number;
  max: number;
  first: number;
  last: number;
  delta: number;
  count: number;
};

type DriftData = {
  bucket_id: string;
  hours: number;
  ph: DriftSnapshot | null;
  ec: DriftSnapshot | null;
  orp: DriftSnapshot | null;
};

interface SensorsTabProps {
  buckets: BucketResponse[];
}

export function SensorsTab({ buckets }: SensorsTabProps) {
  const confirm = useConfirm();
  const { prefs } = usePreferences();
  const METRICS = getMetrics(tempUnitLabel(prefs.temp_unit));
  const [selectedBucket, setSelectedBucket] = useState<string>(buckets[0]?.id || "");
  const [timeRange, setTimeRange] = useState(0); // index into TIME_RANGES
  const {
    data: rawData,
    isLoading: loading,
    mutate,
  } = useApiSWR(
    selectedBucket
      ? ["grow", "sensors", selectedBucket, TIME_RANGES[timeRange].limit, timeRange]
      : null,
    async (token) => {
      const [data, driftData] = await Promise.all([
        listSensorReadings(token, selectedBucket, TIME_RANGES[timeRange].limit),
        getSensorDrift(token, selectedBucket, [24, 168, 720, 720][timeRange]).catch(() => null),
      ]);
      return { readings: data, drift: driftData };
    },
  );
  const readings: SensorReadingResponse[] = rawData?.readings ?? [];
  const drift = (rawData?.drift as DriftData | null | undefined) ?? null;
  const loadReadings = mutate;

  // Helper to get metric value from reading
  const getMetricValue = (r: SensorReadingResponse, key: string): number | null => {
    return (r as unknown as Record<string, number | null>)[key] ?? null;
  };

  // Determine which metrics have data
  const metricsWithData = METRICS.filter((m) =>
    readings.some((r) => getMetricValue(r, m.key) != null),
  );

  // Build chart data (sorted oldest first)
  const chartData = [...readings].reverse().map((r) => {
    const point: Record<string, unknown> = {
      time: formatShortDateTime(r.recorded_at),
    };
    for (const m of metricsWithData) {
      point[m.key] = getMetricValue(r, m.key);
    }
    return point;
  });

  // Calculate trends
  const trends: Record<string, { current: number; delta: number }> = {};
  if (readings.length >= 2) {
    const latest = readings[0];
    const prev = readings[1];
    for (const m of metricsWithData) {
      const cur = getMetricValue(latest, m.key);
      const prv = getMetricValue(prev, m.key);
      if (cur != null && prv != null) {
        trends[m.key] = { current: cur, delta: cur - prv };
      } else if (cur != null) {
        trends[m.key] = { current: cur, delta: 0 };
      }
    }
  } else if (readings.length === 1) {
    for (const m of metricsWithData) {
      const cur = getMetricValue(readings[0], m.key);
      if (cur != null) trends[m.key] = { current: cur, delta: 0 };
    }
  }

  return (
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex items-center gap-3">
        <Select value={selectedBucket} onValueChange={(v) => setSelectedBucket(v ?? "")}>
          <SelectTrigger className="w-48"><SelectValue placeholder="Select bucket" /></SelectTrigger>
          <SelectContent>
            {buckets.map((b) => <SelectItem key={b.id} value={b.id}>#{b.position} {b.label || "Unnamed"}</SelectItem>)}
          </SelectContent>
        </Select>
        <div className="flex gap-1">
          {TIME_RANGES.map((tr, i) => (
            <Button key={tr.label} variant={timeRange === i ? "default" : "outline"} size="sm" onClick={() => setTimeRange(i)}>
              {tr.label}
            </Button>
          ))}
        </div>
      </div>

      {!selectedBucket ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <Activity className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">Select a bucket to view sensor history</p>
        </Card>
      ) : loading ? (
        <Card className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Loading sensor data...</p>
        </Card>
      ) : readings.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <Activity className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No sensor readings for this bucket</p>
          <p className="text-xs text-muted-foreground">Log readings from the Buckets tab</p>
        </Card>
      ) : (
        <>
          {/* Trend badges */}
          <div className="grid gap-2 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
            {metricsWithData.map((m) => {
              const t = trends[m.key];
              if (!t) return null;
              return (
                <Card key={m.key}>
                  <CardContent className="p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{m.label}</span>
                      {t.delta > 0.01 ? (
                        <Badge variant="outline" className="text-xs text-green-600"><TrendingUp className="mr-0.5 size-3" />+{t.delta.toFixed(2)}</Badge>
                      ) : t.delta < -0.01 ? (
                        <Badge variant="outline" className="text-xs text-red-600"><TrendingDown className="mr-0.5 size-3" />{t.delta.toFixed(2)}</Badge>
                      ) : (
                        <Badge variant="outline" className="text-xs"><Minus className="mr-0.5 size-3" />0</Badge>
                      )}
                    </div>
                    <p className="text-lg font-bold mt-1">{typeof t.current === "number" ? t.current.toFixed(m.key === "ppm" ? 0 : m.key === "water_level_pct" || m.key === "soil_moisture" ? 0 : 2) : t.current}{m.unit}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Sensor Drift Analysis */}
          {drift && (drift.ph || drift.ec || drift.orp) && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">pH / EC / ORP Drift ({drift.hours}h)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {drift.ph && drift.ph.count > 0 && (
                    <div className="rounded-lg border p-3 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">pH Drift</span>
                        <Badge variant="outline" className={`text-xs ${drift.ph.delta > 0 ? "text-green-600" : drift.ph.delta < 0 ? "text-red-600" : ""}`}>
                          {drift.ph.delta >= 0 ? "+" : ""}{drift.ph.delta.toFixed(2)}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <span>Min: <strong className="text-foreground">{drift.ph.min.toFixed(2)}</strong></span>
                        <span>Max: <strong className="text-foreground">{drift.ph.max.toFixed(2)}</strong></span>
                        <span>First: <strong className="text-foreground">{drift.ph.first.toFixed(2)}</strong></span>
                        <span>Last: <strong className="text-foreground">{drift.ph.last.toFixed(2)}</strong></span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{drift.ph.count} readings</p>
                    </div>
                  )}
                  {drift.ec && drift.ec.count > 0 && (
                    <div className="rounded-lg border p-3 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">EC Drift</span>
                        <Badge variant="outline" className={`text-xs ${drift.ec.delta > 0 ? "text-green-600" : drift.ec.delta < 0 ? "text-red-600" : ""}`}>
                          {drift.ec.delta >= 0 ? "+" : ""}{drift.ec.delta.toFixed(3)}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <span>Min: <strong className="text-foreground">{drift.ec.min.toFixed(3)}</strong></span>
                        <span>Max: <strong className="text-foreground">{drift.ec.max.toFixed(3)}</strong></span>
                        <span>First: <strong className="text-foreground">{drift.ec.first.toFixed(3)}</strong></span>
                        <span>Last: <strong className="text-foreground">{drift.ec.last.toFixed(3)}</strong></span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{drift.ec.count} readings</p>
                    </div>
                  )}
                  {drift.orp && drift.orp.count > 0 && (
                    <div className="rounded-lg border p-3 space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">ORP Drift</span>
                        <Badge variant="outline" className={`text-xs ${drift.orp.delta > 0 ? "text-green-600" : drift.orp.delta < 0 ? "text-red-600" : ""}`}>
                          {drift.orp.delta >= 0 ? "+" : ""}{drift.orp.delta.toFixed(0)} mV
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <span>Min: <strong className="text-foreground">{drift.orp.min.toFixed(0)} mV</strong></span>
                        <span>Max: <strong className="text-foreground">{drift.orp.max.toFixed(0)} mV</strong></span>
                        <span>First: <strong className="text-foreground">{drift.orp.first.toFixed(0)} mV</strong></span>
                        <span>Last: <strong className="text-foreground">{drift.orp.last.toFixed(0)} mV</strong></span>
                      </div>
                      <p className="text-[10px] text-muted-foreground">{drift.orp.count} readings</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Charts - one per metric with data */}
          {metricsWithData.map((m) => (
            <Card key={m.key}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{m.label}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200} minWidth={0}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} domain={["auto", "auto"]} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Line type="monotone" dataKey={m.key} stroke={m.color} strokeWidth={2} dot={false} name={m.label} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          ))}

          {/* Combined chart */}
          {metricsWithData.length > 1 && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">All Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300} minWidth={0}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Legend />
                    {metricsWithData.map((m) => (
                      <Line key={m.key} type="monotone" dataKey={m.key} stroke={m.color} strokeWidth={1.5} dot={false} name={m.label} />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Recent Readings Table */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Recent Readings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="p-2 text-left font-medium">Time</th>
                      {metricsWithData.map((m) => (
                        <th key={m.key} className="p-2 text-right font-medium">{m.label}</th>
                      ))}
                      <th className="p-2 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {readings.slice(0, 20).map((r) => (
                      <tr key={r.id} className="border-b last:border-0 hover:bg-muted/50">
                        <td className="p-2 text-muted-foreground">{formatShortDateTime(r.recorded_at)}</td>
                        {metricsWithData.map((m) => {
                          const val = getMetricValue(r, m.key);
                          return <td key={m.key} className="p-2 text-right font-mono">{val != null ? val.toFixed(m.key === "ppm" ? 0 : 2) : "—"}</td>;
                        })}
                        <td className="p-2 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                            onClick={async () => {
                              if (!await confirm({ title: "Delete Reading", description: "Permanently delete this sensor reading?", confirmLabel: "Delete", variant: "destructive" })) return;
                              const token = getAccessToken();
                              if (!token) return;
                              await deleteSensorReading(token, r.id);
                              loadReadings();
                            }}
                          >
                            <Trash2 className="size-3" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {readings.length > 20 && (
                <p className="mt-2 text-center text-xs text-muted-foreground">Showing 20 of {readings.length} readings</p>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
