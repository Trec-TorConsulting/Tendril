"use client";

import { useEffect, useMemo, useState } from "react";
import { formatShortDateTime } from "@/lib/utils";
import { useApiSWR } from "@/lib/swr";
import {
  listBuckets,
  listSensorReadings,
  getSensorDrift,
  getStrainLeaderboard,
  listYields,
  getLatestReading,
  getLatestTentReading,
  getTentSensorTrends,
  listTasks,
  listJournalEntries,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type YieldResponse,
} from "@/lib/api";
import { useGrow } from "@/hooks/use-grow";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, tempUnitLabel } from "@/lib/units";
import { resolveOrpSystemType } from "@/lib/orp-system-type";
import { PageHeader } from "@/components/page-header";
import { HeatMapCalendar } from "@/components/heat-map-calendar";
import { SensorGauge, GAUGE_PRESETS, getOrpZones } from "@/components/sensor-gauge";
import { GrowStageIndicator } from "@/components/grow-stage-indicator";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BarChart3,
  Sprout,
  CheckCircle2,
  Activity,
  TrendingUp,
  TrendingDown,
  Minus,
  Thermometer,
  Droplets,
  Trophy,
  Scale,
  Timer,
  CalendarDays,
  Gauge,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie,
  Legend,
  Area,
  AreaChart,
} from "recharts";

const STAGE_COLORS: Record<string, string> = {
  seedling: "#86efac",
  vegetative: "#22c55e",
  flowering: "#f472b6",
  ripening: "#f59e0b",
  drying: "#a78bfa",
  curing: "#60a5fa",
  harvest: "#14b8a6",
};

const QUALITY_COLORS = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"];

interface DriftStats {
  min: number;
  max: number;
  first: number;
  last: number;
  delta: number;
  count: number;
}

interface DriftResponse {
  bucket_id: string;
  hours: number;
  ph: DriftStats | null;
  ec: DriftStats | null;
}

interface LeaderboardEntry {
  strain_name: string;
  harvests: number;
  avg_dry_weight_g: number | null;
  avg_quality: number | null;
}

interface EnvSnapshot {
  bucketLabel: string;
  water_temp_f: number | null;
  ph: number | null;
  ec: number | null;
  orp: number | null;
}

export default function AnalyticsPage() {
  const { grows } = useGrow();
  const { prefs } = usePreferences();
  const [analyticsGrowId, setAnalyticsGrowId] = useState<string>("all");
  const activeGrow = analyticsGrowId === "all" ? null : grows.find((g) => g.id === analyticsGrowId) ?? null;
  const orpSystemType = resolveOrpSystemType(activeGrow?.settings?.system_type);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [selectedBucketId, setSelectedBucketId] = useState<string>("");
  const [sensorData, setSensorData] = useState<SensorReadingResponse[]>([]);
  const [driftData, setDriftData] = useState<DriftResponse | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [allYields, setAllYields] = useState<YieldResponse[]>([]);
  const [envSnapshots, setEnvSnapshots] = useState<EnvSnapshot[]>([]);
  const [tentAmbient, setTentAmbient] = useState<TentReadingResponse | null>(null);
  const [tentTrends, setTentTrends] = useState<{ timestamps: string[]; temps: (number | null)[]; humidities: (number | null)[] } | null>(null);
  const [heatMapData, setHeatMapData] = useState<{ date: string; count: number }[]>([]);
  const {
    data: overviewData,
    isLoading: loading,
  } = useApiSWR(
    ["analytics", "overview"],
    async (token) => {
      const [leaderboard, allYields, tasks, journal] = await Promise.all([
        getStrainLeaderboard(token).catch(() => [] as LeaderboardEntry[]),
        listYields(token).catch(() => [] as YieldResponse[]),
        listTasks(token, {}).catch(() => []),
        listJournalEntries(token).catch(() => []),
      ]);
      const activityByDate = new Map<string, number>();
      for (const t of tasks) {
        const d = (t.completed_at || t.created_at).slice(0, 10);
        activityByDate.set(d, (activityByDate.get(d) || 0) + 1);
      }
      for (const j of journal) {
        const d = j.created_at.slice(0, 10);
        activityByDate.set(d, (activityByDate.get(d) || 0) + 1);
      }
      return {
        leaderboard,
        allYields,
        heatMapData: Array.from(activityByDate.entries()).map(([date, count]) => ({ date, count })),
      };
    },
  );
  const {
    data: growContextData,
  } = useApiSWR(
    ["analytics", "grow-context", analyticsGrowId, activeGrow?.id ?? "all", activeGrow?.tent_id ?? "none"],
    async (token) => {
      const bkts = await listBuckets(token, activeGrow?.id).catch(() => [] as BucketResponse[]);
      const activeBuckets = bkts.filter((b) => b.status === "active");
      const selectedBucketId = activeBuckets.length > 0
        ? activeBuckets[0].id
        : bkts.length > 0
          ? bkts[0].id
          : "";

      let tentAmbient: TentReadingResponse | null = null;
      let tentTrends: { timestamps: string[]; temps: (number | null)[]; humidities: (number | null)[] } | null = null;
      if (activeGrow) {
        try {
          const [ambient, trends] = await Promise.all([
            getLatestTentReading(token, activeGrow.tent_id),
            getTentSensorTrends(token, activeGrow.tent_id).catch(() => null),
          ]);
          tentAmbient = ambient;
          tentTrends = trends;
        } catch {
          tentAmbient = null;
          tentTrends = null;
        }
      }

      const snapshotBuckets = activeBuckets.slice(0, 10);
      const snapshotResults = await Promise.all(
        snapshotBuckets.map(async (b) => {
          try {
            const latest = await getLatestReading(token, b.id);
            if (latest) {
              return {
                bucketLabel: `#${b.position} ${b.label || b.strain_name || ""}`.trim(),
                water_temp_f: latest.water_temp_f,
                ph: latest.ph,
                ec: latest.ec,
                orp: latest.orp,
              };
            }
          } catch { /* skip */ }
          return null;
        })
      );

      return {
        buckets: bkts,
        selectedBucketId,
        tentAmbient,
        tentTrends,
        envSnapshots: snapshotResults.filter((s): s is EnvSnapshot => s !== null),
      };
    },
  );
  const {
    data: bucketData,
    isLoading: sensorLoading,
  } = useApiSWR(
    selectedBucketId ? ["analytics", "bucket", selectedBucketId] : null,
    async (token) => {
      const [sensorData, driftData] = await Promise.all([
        listSensorReadings(token, selectedBucketId, 200),
        getSensorDrift(token, selectedBucketId, 24).catch(() => null),
      ]);
      return {
        sensorData: sensorData.reverse(),
        driftData: driftData as DriftResponse | null,
      };
    },
  );

  useEffect(() => {
    if (!overviewData) return;
    setLeaderboard(overviewData.leaderboard);
    setAllYields(overviewData.allYields);
    setHeatMapData(overviewData.heatMapData);
  }, [overviewData]);

  useEffect(() => {
    if (!growContextData) return;
    setBuckets(growContextData.buckets);
    setSelectedBucketId(growContextData.selectedBucketId);
    setTentAmbient(growContextData.tentAmbient);
    setTentTrends(growContextData.tentTrends);
    setEnvSnapshots(growContextData.envSnapshots);
  }, [growContextData]);

  useEffect(() => {
    if (!selectedBucketId) {
      setSensorData([]);
      setDriftData(null);
      return;
    }
    setSensorData(bucketData?.sensorData ?? []);
    setDriftData(bucketData?.driftData ?? null);
  }, [selectedBucketId, bucketData]);

  const activeGrows = grows.filter((g) => g.status === "active").length;
  const completedGrows = grows.filter((g) => g.status === "completed").length;
  const activeBucketCount = buckets.filter((b) => b.status === "active").length;

  // Yield aggregations
  const totalDryWeight = allYields.reduce((sum, y) => sum + (y.dry_weight_g || 0), 0);
  const totalWetWeight = allYields.reduce((sum, y) => sum + (y.wet_weight_g || 0), 0);
  const avgQuality = allYields.filter((y) => y.quality_rating).length > 0
    ? allYields.filter((y) => y.quality_rating).reduce((sum, y) => sum + (y.quality_rating || 0), 0) / allYields.filter((y) => y.quality_rating).length
    : null;
  const qualityDistribution = [1, 2, 3, 4, 5].map((q) => ({
    name: `${q}★`,
    count: allYields.filter((y) => y.quality_rating === q).length,
  }));

  // Grow timeline from milestones
  const STAGES_ORDERED = ["seedling", "vegetative", "flowering", "ripening", "drying", "curing", "harvest"];
  const stageTimeline = activeGrow?.milestones
    ? STAGES_ORDERED.map((stage, i) => {
        const ts = activeGrow.milestones?.[stage];
        if (!ts) return null;
        const nextStage = STAGES_ORDERED.find((s, j) => j > i && activeGrow.milestones?.[s]);
        const nextTs = nextStage ? activeGrow.milestones?.[nextStage] : null;
        const days = nextTs
          ? Math.round((new Date(nextTs).getTime() - new Date(ts).getTime()) / 86400000)
          : Math.round((Date.now() - new Date(ts).getTime()) / 86400000);
        return { stage, days, started: ts, isCurrent: !nextTs };
      }).filter(Boolean) as { stage: string; days: number; started: string; isCurrent: boolean }[]
    : [];

  const stats = [
    { label: "Active Grows", value: activeGrows, icon: Sprout },
    { label: "Completed", value: completedGrows, icon: CheckCircle2 },
    { label: "Total Grows", value: grows.length, icon: BarChart3 },
    { label: "Buckets", value: activeBucketCount, icon: Activity },
  ];

  // Chart data formatting
  const waterTempKey = `Water ${tempUnitLabel(prefs.temp_unit)}`;
  const ambientTempKey = `Temp ${tempUnitLabel(prefs.temp_unit)}`;

  // Build merged chart data from bucket sensors + tent trends
  const chartData = useMemo(() => {
    // Index tent trends by formatted time for merging
    const tentMap = new Map<string, { temp: number | null; humidity: number | null }>();
    if (tentTrends) {
      tentTrends.timestamps.forEach((ts, i) => {
        const key = formatShortDateTime(ts);
        const rawTemp = tentTrends.temps[i];
        const temp = rawTemp != null ? Number(formatTemp(rawTemp, "f", prefs.temp_unit, 1).replace(/[^\d.-]/g, "")) : null;
        tentMap.set(key, { temp, humidity: tentTrends.humidities[i] });
      });
    }

    // Map sensor data and merge tent data at matching timestamps
    const merged = sensorData.map((r) => {
      const timeKey = formatShortDateTime(r.recorded_at);
      const tent = tentMap.get(timeKey);
      tentMap.delete(timeKey); // consumed
      return {
        time: timeKey,
        pH: r.ph,
        EC: r.ec,
        PPM: r.ppm,
        [waterTempKey]: r.water_temp_f != null ? Number(formatTemp(r.water_temp_f, "f", prefs.temp_unit, 1).replace(/[^\d.-]/g, "")) : null,
        [ambientTempKey]: tent?.temp ?? null,
        "Humidity %": tent?.humidity ?? null,
      };
    });

    // Append any remaining tent data points that didn't align with sensor readings
    for (const [timeKey, tent] of tentMap) {
      merged.push({
        time: timeKey,
        pH: null,
        EC: null,
        PPM: null,
        [waterTempKey]: null,
        [ambientTempKey]: tent.temp,
        "Humidity %": tent.humidity,
      });
    }

    // Sort by time string (already formatted consistently)
    merged.sort((a, b) => a.time.localeCompare(b.time));
    return merged;
  }, [sensorData, tentTrends, waterTempKey, ambientTempKey, prefs.temp_unit]);

  return (
    <>
      <PageHeader
        title="Analytics"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Analytics" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Grow + Bucket Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          <Select value={analyticsGrowId} onValueChange={(v) => setAnalyticsGrowId(v ?? "all")}>
            <SelectTrigger className="w-56">
              <SelectValue placeholder="Select grow" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Grows</SelectItem>
              {grows.map((g) => (
                <SelectItem key={g.id} value={g.id}>
                  {g.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {buckets.length > 1 && (
            <Select value={selectedBucketId} onValueChange={(v) => setSelectedBucketId(v ?? "")}>
              <SelectTrigger className="w-56">
                <SelectValue placeholder="Select bucket" />
              </SelectTrigger>
              <SelectContent>
                {buckets.map((b) => (
                  <SelectItem key={b.id} value={b.id}>
                    #{b.position} {b.label || b.strain_name || "Unnamed"}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <Card key={s.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
                <s.icon className="size-4 text-primary" />
              </CardHeader>
              <CardContent>
                {loading ? <Skeleton className="h-8 w-16" /> : <div className="text-2xl font-bold">{s.value}</div>}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Sensor Trends Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="size-4" /> Sensor Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sensorLoading ? (
              <Skeleton className="h-72 w-full" />
            ) : chartData.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">
                No sensor data yet for this bucket. Add readings to see trends.
              </p>
            ) : (
              <div className="space-y-6">
                {/* pH / EC / PPM */}
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">pH · EC · PPM</p>
                  <ResponsiveContainer width="100%" height={240} minWidth={0}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                      <YAxis yAxisId="ph" domain={[4, 9]} tick={{ fontSize: 10 }} />
                      <YAxis yAxisId="ec" orientation="right" tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ fontSize: 12 }} />
                      <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                      <Line yAxisId="ph" type="monotone" dataKey="pH" stroke="#22c55e" strokeWidth={2} dot={false} connectNulls />
                      <Line yAxisId="ec" type="monotone" dataKey="EC" stroke="#3b82f6" strokeWidth={2} dot={false} connectNulls />
                      <Line yAxisId="ec" type="monotone" dataKey="PPM" stroke="#f59e0b" strokeWidth={1.5} dot={false} connectNulls />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                {/* Temperature / Humidity */}
                <div>
                  <p className="mb-2 text-xs font-medium text-muted-foreground">Temperature · Humidity</p>
                  <ResponsiveContainer width="100%" height={200} minWidth={0}>
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ fontSize: 12 }} />
                      <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                      <Area type="monotone" dataKey={waterTempKey} stroke="#ef4444" fill="#ef444420" strokeWidth={2} dot={false} connectNulls />
                      <Area type="monotone" dataKey={ambientTempKey} stroke="#f97316" fill="#f9731620" strokeWidth={2} dot={false} connectNulls />
                      <Area type="monotone" dataKey="Humidity %" stroke="#06b6d4" fill="#06b6d420" strokeWidth={2} dot={false} connectNulls />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* pH/EC Drift + Environment Overview row */}
        <div className="grid gap-4 lg:grid-cols-2">
          {/* pH/EC Drift Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Droplets className="size-4" /> 24h pH/EC Drift
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!driftData || (!driftData.ph && !driftData.ec) ? (
                <p className="py-6 text-center text-sm text-muted-foreground">Not enough data for drift analysis</p>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {driftData.ph && (
                    <div className="space-y-2 rounded-lg border p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">pH</span>
                        <DriftBadge delta={driftData.ph.delta} />
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <span>First: <span className="text-foreground font-medium">{driftData.ph.first.toFixed(2)}</span></span>
                        <span>Last: <span className="text-foreground font-medium">{driftData.ph.last.toFixed(2)}</span></span>
                        <span>Min: <span className="text-foreground font-medium">{driftData.ph.min.toFixed(2)}</span></span>
                        <span>Max: <span className="text-foreground font-medium">{driftData.ph.max.toFixed(2)}</span></span>
                      </div>
                      <p className="text-xs text-muted-foreground">{driftData.ph.count} readings</p>
                    </div>
                  )}
                  {driftData.ec && (
                    <div className="space-y-2 rounded-lg border p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">EC</span>
                        <DriftBadge delta={driftData.ec.delta} />
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                        <span>First: <span className="text-foreground font-medium">{driftData.ec.first.toFixed(2)}</span></span>
                        <span>Last: <span className="text-foreground font-medium">{driftData.ec.last.toFixed(2)}</span></span>
                        <span>Min: <span className="text-foreground font-medium">{driftData.ec.min.toFixed(2)}</span></span>
                        <span>Max: <span className="text-foreground font-medium">{driftData.ec.max.toFixed(2)}</span></span>
                      </div>
                      <p className="text-xs text-muted-foreground">{driftData.ec.count} readings</p>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Environment Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Thermometer className="size-4" /> Environment Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              {envSnapshots.length === 0 && !tentAmbient ? (
                <p className="py-6 text-center text-sm text-muted-foreground">No active bucket readings</p>
              ) : (
                <div className="space-y-2">
                  {tentAmbient && (
                    <div className="flex items-center justify-between rounded-md border bg-muted/30 px-3 py-2 text-sm">
                      <span className="font-medium min-w-[6rem]">Tent Ambient</span>
                      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                        {tentAmbient.ambient_temp_f != null && <span>🌡 {formatTemp(tentAmbient.ambient_temp_f, "f", prefs.temp_unit)}</span>}
                        {tentAmbient.ambient_humidity != null && <span>💧 {tentAmbient.ambient_humidity.toFixed(0)}%</span>}
                      </div>
                    </div>
                  )}
                  {envSnapshots.map((s, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
                      <span className="font-medium min-w-[6rem]">{s.bucketLabel}</span>
                      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                        {s.water_temp_f != null && <span>🌊 {formatTemp(s.water_temp_f, "f", prefs.temp_unit)}</span>}
                        {s.ph != null && <span>pH {s.ph.toFixed(1)}</span>}
                        {s.ec != null && <span>EC {s.ec.toFixed(2)}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tent Sensor Trends */}
          {tentTrends && Array.isArray(tentTrends.timestamps) && tentTrends.timestamps.length > 0 && (
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Activity className="size-4" /> Tent Environment Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250} minWidth={0}>
                  <AreaChart data={tentTrends.timestamps.map((ts, i) => ({
                    time: formatShortDateTime(ts),
                    temp: tentTrends.temps[i],
                    humidity: tentTrends.humidities[i],
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis yAxisId="temp" tick={{ fontSize: 10 }} domain={["auto", "auto"]} />
                    <YAxis yAxisId="humidity" orientation="right" tick={{ fontSize: 10 }} domain={[0, 100]} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Legend />
                    <Area yAxisId="temp" type="monotone" dataKey="temp" stroke="#ef4444" fill="#ef444420" strokeWidth={2} name={`Temp (${tempUnitLabel(prefs.temp_unit)})`} />
                    <Area yAxisId="humidity" type="monotone" dataKey="humidity" stroke="#3b82f6" fill="#3b82f620" strokeWidth={2} name="Humidity (%)" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Grow Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Timer className="size-4" /> Grow Timeline
              {activeGrow && <Badge variant="secondary" className="text-xs capitalize ml-2">{activeGrow.stage}</Badge>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {stageTimeline.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                No milestone dates recorded yet. Update milestones on the grow page to see stage durations.
              </p>
            ) : (
              <div className="flex items-end gap-1">
                {stageTimeline.map((s) => {
                  const maxDays = Math.max(...stageTimeline.map((x) => x.days), 1);
                  const height = Math.max((s.days / maxDays) * 160, 24);
                  return (
                    <div key={s.stage} className="flex flex-1 flex-col items-center gap-1">
                      <span className="text-xs font-bold">{s.days}d</span>
                      <div
                        className="w-full rounded-t-md transition-all"
                        style={{
                          height,
                          backgroundColor: STAGE_COLORS[s.stage] || "#94a3b8",
                          opacity: s.isCurrent ? 1 : 0.7,
                        }}
                      />
                      <span className="text-[10px] capitalize text-muted-foreground">{s.stage}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Strain Leaderboard + Yield Tracker row */}
        <div className="grid gap-4 lg:grid-cols-2">
          {/* Strain Leaderboard */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="size-4" /> Strain Leaderboard
              </CardTitle>
            </CardHeader>
            <CardContent>
              {leaderboard.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  Complete harvests to see strain rankings
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={Math.max(leaderboard.length * 40, 120)} minWidth={0}>
                  <BarChart data={leaderboard} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                    <XAxis type="number" tick={{ fontSize: 10 }} />
                    <YAxis dataKey="strain_name" type="category" tick={{ fontSize: 11 }} width={80} />
                    <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => [`${Number(v)?.toFixed(1)}g`, "Avg Dry Weight"]} />
                    <Bar dataKey="avg_dry_weight_g" name="Avg Dry Weight (g)" radius={[0, 4, 4, 0]}>
                      {leaderboard.map((_, i) => (
                        <Cell key={i} fill={i === 0 ? "#22c55e" : i === 1 ? "#3b82f6" : i === 2 ? "#f59e0b" : "#94a3b8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
              {leaderboard.length > 0 && (
                <div className="mt-3 space-y-1">
                  {leaderboard.map((entry, i) => (
                    <div key={entry.strain_name} className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1">
                        {i === 0 && "🥇"}{i === 1 && "🥈"}{i === 2 && "🥉"}
                        <span className="font-medium">{entry.strain_name}</span>
                      </span>
                      <span className="text-muted-foreground">
                        {entry.harvests} harvest{entry.harvests !== 1 && "s"}
                        {entry.avg_quality != null && ` · ${entry.avg_quality.toFixed(1)}★`}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Yield Tracker */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="size-4" /> Yield Tracker
              </CardTitle>
            </CardHeader>
            <CardContent>
              {allYields.length === 0 ? (
                <p className="py-8 text-center text-sm text-muted-foreground">
                  No harvest data yet. Record yields on the grow page.
                </p>
              ) : (
                <div className="space-y-4">
                  {/* Summary stats */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="rounded-lg border p-3 text-center">
                      <p className="text-2xl font-bold">{totalDryWeight.toFixed(0)}g</p>
                      <p className="text-xs text-muted-foreground">Total Dry</p>
                    </div>
                    <div className="rounded-lg border p-3 text-center">
                      <p className="text-2xl font-bold">{totalWetWeight.toFixed(0)}g</p>
                      <p className="text-xs text-muted-foreground">Total Wet</p>
                    </div>
                    <div className="rounded-lg border p-3 text-center">
                      <p className="text-2xl font-bold">{avgQuality != null ? `${avgQuality.toFixed(1)}★` : "—"}</p>
                      <p className="text-xs text-muted-foreground">Avg Quality</p>
                    </div>
                  </div>
                  {/* Quality distribution pie */}
                  {qualityDistribution.some((q) => q.count > 0) && (
                    <div>
                      <p className="mb-2 text-xs font-medium text-muted-foreground">Quality Distribution</p>
                      <ResponsiveContainer width="100%" height={160} minWidth={0}>
                        <PieChart>
                          <Pie
                            data={qualityDistribution.filter((q) => q.count > 0)}
                            dataKey="count"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={60}
                            innerRadius={30}
                            label
                          >
                            {qualityDistribution.filter((q) => q.count > 0).map((q) => {
                              const rating = parseInt(q.name);
                              return <Cell key={q.name} fill={QUALITY_COLORS[rating - 1] || "#94a3b8"} />;
                            })}
                          </Pie>
                          <Tooltip contentStyle={{ fontSize: 12 }} />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                  {/* Dry-to-wet ratio */}
                  {totalWetWeight > 0 && (
                    <p className="text-xs text-center text-muted-foreground">
                      Dry/Wet Ratio: <span className="font-medium text-foreground">{((totalDryWeight / totalWetWeight) * 100).toFixed(1)}%</span>
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Activity Heat Map */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarDays className="size-4" /> Grow Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {heatMapData.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">
                Complete tasks and log journal entries to see your activity heat map.
              </p>
            ) : (
              <HeatMapCalendar data={heatMapData} />
            )}
          </CardContent>
        </Card>

        {/* Sensor Gauges + Stage Indicator */}
        {tentAmbient && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge className="size-4" /> Live Environment
                {activeGrow && <GrowStageIndicator stage={activeGrow.stage} size="sm" className="ml-auto" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                {tentAmbient.ambient_temp_f != null && (
                  <SensorGauge value={tentAmbient.ambient_temp_f} {...GAUGE_PRESETS.temp} />
                )}
                {tentAmbient.ambient_humidity != null && (
                  <SensorGauge value={tentAmbient.ambient_humidity} {...GAUGE_PRESETS.humidity} />
                )}
                {envSnapshots.length > 0 && envSnapshots[0].ph != null && (
                  <SensorGauge value={envSnapshots[0].ph} {...GAUGE_PRESETS.ph} />
                )}
                {envSnapshots.length > 0 && envSnapshots[0].ec != null && (
                  <SensorGauge value={envSnapshots[0].ec} {...GAUGE_PRESETS.ec} />
                )}
                {envSnapshots.length > 0 && envSnapshots[0].water_temp_f != null && (
                  <SensorGauge value={envSnapshots[0].water_temp_f} {...GAUGE_PRESETS.waterTemp} />
                )}
                {envSnapshots.length > 0 && envSnapshots[0].orp != null && (
                  <SensorGauge
                    value={envSnapshots[0].orp}
                    {...GAUGE_PRESETS.orp}
                    zones={getOrpZones(orpSystemType)}
                  />
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}

function DriftBadge({ delta }: { delta: number }) {
  const abs = Math.abs(delta);
  if (abs < 0.05) return <Badge variant="secondary" className="gap-1 text-xs"><Minus className="size-3" /> Stable</Badge>;
  if (delta > 0) return <Badge variant="outline" className="gap-1 text-xs text-amber-500 border-amber-500"><TrendingUp className="size-3" /> +{delta.toFixed(3)}</Badge>;
  return <Badge variant="outline" className="gap-1 text-xs text-blue-500 border-blue-500"><TrendingDown className="size-3" /> {delta.toFixed(3)}</Badge>;
}
