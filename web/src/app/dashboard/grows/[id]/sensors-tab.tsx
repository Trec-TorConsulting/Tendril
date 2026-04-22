"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listSensorReadings, type SensorReadingResponse, type BucketResponse } from "@/lib/api";
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
import { Activity, TrendingUp, TrendingDown, Minus } from "lucide-react";
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

const METRICS = [
  { key: "ph", label: "pH", color: "#22c55e", unit: "" },
  { key: "ec", label: "EC", color: "#3b82f6", unit: " mS" },
  { key: "ppm", label: "PPM", color: "#f59e0b", unit: "" },
  { key: "water_temp_f", label: "Water Temp", color: "#ef4444", unit: "°F" },
  { key: "dissolved_oxygen", label: "DO", color: "#8b5cf6", unit: " mg/L" },
  { key: "water_level_pct", label: "Water Level", color: "#64748b", unit: "%" },
  { key: "soil_moisture", label: "Soil Moisture", color: "#84cc16", unit: "%" },
  { key: "soil_temp", label: "Soil Temp", color: "#d946ef", unit: "°F" },
  { key: "runoff_ph", label: "Runoff pH", color: "#14b8a6", unit: "" },
  { key: "runoff_ec", label: "Runoff EC", color: "#0ea5e9", unit: " mS" },
] as const;

const TIME_RANGES = [
  { label: "24h", limit: 96 },
  { label: "7d", limit: 672 },
  { label: "30d", limit: 2880 },
  { label: "All", limit: 10000 },
];

interface SensorsTabProps {
  buckets: BucketResponse[];
}

export function SensorsTab({ buckets }: SensorsTabProps) {
  const [selectedBucket, setSelectedBucket] = useState<string>(buckets[0]?.id || "");
  const [timeRange, setTimeRange] = useState(0); // index into TIME_RANGES
  const [readings, setReadings] = useState<SensorReadingResponse[]>([]);
  const [loading, setLoading] = useState(false);

  const loadReadings = useCallback(async () => {
    if (!selectedBucket) return;
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    try {
      const data = await listSensorReadings(token, selectedBucket, TIME_RANGES[timeRange].limit);
      setReadings(data);
    } catch { setReadings([]); }
    finally { setLoading(false); }
  }, [selectedBucket, timeRange]);

  useEffect(() => { loadReadings(); }, [loadReadings]);

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
      time: new Date(r.recorded_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }),
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
                    <p className="text-lg font-bold mt-1">{typeof t.current === "number" ? t.current.toFixed(m.key === "ppm" ? 0 : m.key === "ambient_humidity" || m.key === "water_level_pct" || m.key === "soil_moisture" ? 0 : 2) : t.current}{m.unit}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* Charts - one per metric with data */}
          {metricsWithData.map((m) => (
            <Card key={m.key}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">{m.label}</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
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
                <ResponsiveContainer width="100%" height={300}>
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
        </>
      )}
    </div>
  );
}
