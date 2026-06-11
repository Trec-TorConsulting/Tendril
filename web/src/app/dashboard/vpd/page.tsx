"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Droplets, Thermometer, Wind } from "lucide-react";
import { toast } from "sonner";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/components/page-header";
import { getAccessToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";
import { useGrow } from "@/hooks/use-grow";
import {
  calculateVpd,
  getVpdChartZones,
  getVpdStatus,
  getVpdStatusDisplay,
  getVpdZone,
  type GrowStage,
  VPD_ZONES,
} from "@/lib/vpd";

interface TentOption {
  id: string;
  name: string;
}

interface TrendData {
  timestamps: string[];
  temps: (number | null)[];
  humidities: (number | null)[];
  vpd: (number | null)[];
  co2: (number | null)[];
  lux: (number | null)[];
}

export default function VpdDashboardPage() {
  const { selectedGrow } = useGrow();
  const [tents, setTents] = useState<TentOption[]>([]);
  const [selectedTent, setSelectedTent] = useState<string>("");
  const [trends, setTrends] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [leafOffset, setLeafOffset] = useState(2);
  const [stage, setStage] = useState<GrowStage>("vegetative");

  // Load tents
  useEffect(() => {
    async function loadTents() {
      try {
        const token = getAccessToken() ?? "";
        const data = await apiFetch<{ items: { id: string; name: string }[] }>("/tents", { token });
        setTents(data.items || []);
        if (data.items?.length > 0 && !selectedTent) {
          setSelectedTent(data.items[0].id);
        }
      } catch {
        toast.error("Failed to load tents");
      }
    }
    loadTents();
  }, []);

  // Detect stage from current grow
  useEffect(() => {
    if (selectedGrow?.stage) {
      const s = selectedGrow.stage.toLowerCase();
      if (s.includes("seed") || s.includes("clone") || s.includes("germination")) {
        setStage("seedling");
      } else if (s.includes("veg")) {
        setStage("vegetative");
      } else if (s.includes("late") || s.includes("ripen") || s.includes("flush")) {
        setStage("late_flower");
      } else if (s.includes("flower") || s.includes("bloom")) {
        setStage("early_flower");
      }
    }
  }, [selectedGrow?.stage]);

  // Load trends when tent changes
  const loadTrends = useCallback(async () => {
    if (!selectedTent) return;
    setLoading(true);
    try {
      const token = getAccessToken() ?? "";
      const data = await apiFetch<TrendData>(`/tent-sensors/trends/${selectedTent}?hours=24`, { token });
      setTrends(data);
    } catch {
      toast.error("Failed to load VPD trends");
    } finally {
      setLoading(false);
    }
  }, [selectedTent]);

  useEffect(() => {
    loadTrends();
    const interval = setInterval(loadTrends, 60_000);
    return () => clearInterval(interval);
  }, [loadTrends]);

  // Compute chart data with client-side VPD calculation (with leaf offset)
  const chartData = trends
    ? trends.timestamps.map((ts, i) => {
        const temp = trends.temps[i];
        const humidity = trends.humidities[i];
        const serverVpd = trends.vpd[i];
        // Prefer server VPD, fallback to client calc with leaf offset
        const vpd = serverVpd ?? (temp != null && humidity != null ? calculateVpd(temp, humidity, leafOffset) : null);
        return {
          time: new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          vpd,
          temp,
          humidity,
        };
      })
    : [];

  // Current values (last reading)
  const currentVpd = chartData.length > 0 ? chartData[chartData.length - 1].vpd : null;
  const currentTemp = chartData.length > 0 ? chartData[chartData.length - 1].temp : null;
  const currentHumidity = chartData.length > 0 ? chartData[chartData.length - 1].humidity : null;

  const vpdStatus = currentVpd != null ? getVpdStatus(currentVpd, stage) : null;
  const statusDisplay = vpdStatus ? getVpdStatusDisplay(vpdStatus) : null;
  const zone = getVpdZone(stage);
  const chartZones = getVpdChartZones(stage);

  if (loading && !trends) {
    return (
      <div className="space-y-6 p-6">
        <PageHeader title="VPD Monitor" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
        <Skeleton className="h-80 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <PageHeader title="VPD Monitor" />

      {/* Controls */}
      <div className="flex flex-wrap items-end gap-4">
        <div className="w-48">
          <Label>Tent</Label>
          <Select value={selectedTent} onValueChange={(v) => setSelectedTent(v ?? "")}>
            <SelectTrigger>
              <SelectValue placeholder="Select tent" />
            </SelectTrigger>
            <SelectContent>
              {tents.map((t) => (
                <SelectItem key={t.id} value={t.id}>
                  {t.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-48">
          <Label>Grow Stage</Label>
          <Select value={stage} onValueChange={(v) => setStage((v ?? "vegetative") as GrowStage)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(VPD_ZONES).map(([key, z]) => (
                <SelectItem key={key} value={key}>
                  {z.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="w-48">
          <Label>Leaf Offset (°F below ambient)</Label>
          <Input
            type="number"
            value={leafOffset}
            onChange={(e) => setLeafOffset(Number(e.target.value) || 0)}
            min={0}
            max={5}
            step={0.5}
            className="mt-1"
          />
        </div>
      </div>

      {/* Current Values Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Current VPD</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold" style={{ color: statusDisplay?.color }}>
              {currentVpd != null ? `${currentVpd.toFixed(2)} kPa` : "—"}
            </div>
            {statusDisplay && (
              <p className="mt-1 text-xs" style={{ color: statusDisplay.color }}>
                {statusDisplay.label}
              </p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
              Target: {zone.optMin}–{zone.optMax} kPa ({zone.label})
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Temperature</CardTitle>
            <Thermometer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {currentTemp != null ? `${currentTemp.toFixed(1)}°F` : "—"}
            </div>
            <p className="text-xs text-muted-foreground">
              Leaf: {currentTemp != null ? `${(currentTemp - leafOffset).toFixed(1)}°F` : "—"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Humidity</CardTitle>
            <Droplets className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {currentHumidity != null ? `${currentHumidity.toFixed(0)}%` : "—"}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transpiration</CardTitle>
            <Wind className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {vpdStatus === "optimal" ? "Active" : vpdStatus === "too_high" ? "Stressed" : vpdStatus === "too_low" ? "Sluggish" : "—"}
            </div>
            <p className="text-xs text-muted-foreground">
              {vpdStatus === "optimal"
                ? "Plants transpiring at peak efficiency"
                : vpdStatus === "too_high"
                  ? "Stomata closing to conserve water"
                  : vpdStatus === "too_low"
                    ? "Raise temp or lower humidity"
                    : "Waiting for data"}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* VPD Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            24-Hour VPD Trend
            <Badge variant="outline">{zone.label}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {chartData.length === 0 ? (
            <div className="flex h-64 items-center justify-center text-muted-foreground">
              No VPD data available for this tent
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={320} minWidth={0}>
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 11 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  domain={[0, 2.5]}
                  tick={{ fontSize: 11 }}
                  label={{ value: "kPa", angle: -90, position: "insideLeft", style: { fontSize: 11 } }}
                />
                <Tooltip labelStyle={{ fontSize: 11 }} />

                {/* Zone bands */}
                {chartZones.map((z, i) => (
                  <ReferenceArea
                    key={i}
                    y1={z.y1}
                    y2={z.y2}
                    fill={z.color}
                    fillOpacity={1}
                    stroke="none"
                  />
                ))}

                <Area
                  type="monotone"
                  dataKey="vpd"
                  stroke="#8b5cf6"
                  fill="#8b5cf680"
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* VPD Guide */}
      <Card>
        <CardHeader>
          <CardTitle>VPD Zones Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {Object.entries(VPD_ZONES).map(([key, z]) => (
              <div
                key={key}
                className={`rounded-lg border p-3 ${key === stage ? "border-primary bg-primary/5" : ""}`}
              >
                <p className="font-medium">{z.label}</p>
                <p className="text-sm text-muted-foreground">
                  Optimal: {z.optMin}–{z.optMax} kPa
                </p>
                <p className="text-xs text-muted-foreground">
                  Range: {z.low}–{z.high} kPa
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
