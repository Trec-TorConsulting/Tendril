"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listBuckets,
  listSensorReadings,
  getSensorDrift,
  getStrainLeaderboard,
  listYields,
  getLatestReading,
  type BucketResponse,
  type SensorReadingResponse,
  type YieldResponse,
} from "@/lib/api";
import { useGrow } from "@/hooks/use-grow";
import { PageHeader } from "@/components/page-header";
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
  ambient_temp_f: number | null;
  ambient_humidity: number | null;
  water_temp_f: number | null;
  ph: number | null;
  ec: number | null;
}

export default function AnalyticsPage() {
  const { grows, selectedGrow } = useGrow();
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [selectedBucketId, setSelectedBucketId] = useState<string>("");
  const [sensorData, setSensorData] = useState<SensorReadingResponse[]>([]);
  const [driftData, setDriftData] = useState<DriftResponse | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [allYields, setAllYields] = useState<YieldResponse[]>([]);
  const [envSnapshots, setEnvSnapshots] = useState<EnvSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [sensorLoading, setSensorLoading] = useState(false);

  // Load leaderboard + yields on mount
  useEffect(() => {
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      try {
        const [lb, ylds] = await Promise.all([
          getStrainLeaderboard(token).catch(() => [] as LeaderboardEntry[]),
          listYields(token).catch(() => [] as YieldResponse[]),
        ]);
        setLeaderboard(lb);
        setAllYields(ylds);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Load buckets when grow changes
  useEffect(() => {
    if (!selectedGrow) {
      setBuckets([]);
      setSelectedBucketId("");
      setEnvSnapshots([]);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    (async () => {
      const bkts = await listBuckets(token, selectedGrow.id);
      setBuckets(bkts);
      const activeBuckets = bkts.filter((b) => b.status === "active");
      if (activeBuckets.length > 0) {
        setSelectedBucketId(activeBuckets[0].id);
      } else if (bkts.length > 0) {
        setSelectedBucketId(bkts[0].id);
      } else {
        setSelectedBucketId("");
      }
      // Load environment snapshots for all active buckets
      const snapshots: EnvSnapshot[] = [];
      for (const b of activeBuckets.slice(0, 10)) {
        try {
          const latest = await getLatestReading(token, b.id);
          if (latest) {
            snapshots.push({
              bucketLabel: `#${b.position} ${b.label || b.strain_name || ""}`.trim(),
              ambient_temp_f: latest.ambient_temp_f,
              ambient_humidity: latest.ambient_humidity,
              water_temp_f: latest.water_temp_f,
              ph: latest.ph,
              ec: latest.ec,
            });
          }
        } catch { /* skip */ }
      }
      setEnvSnapshots(snapshots);
    })();
  }, [selectedGrow?.id]);

  // Load sensor data + drift when bucket changes
  useEffect(() => {
    if (!selectedBucketId) {
      setSensorData([]);
      setDriftData(null);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    setSensorLoading(true);
    (async () => {
      try {
        const [readings, drift] = await Promise.all([
          listSensorReadings(token, selectedBucketId, 200),
          getSensorDrift(token, selectedBucketId, 24).catch(() => null),
        ]);
        setSensorData(readings.reverse()); // oldest first for chart
        setDriftData(drift as DriftResponse | null);
      } finally {
        setSensorLoading(false);
      }
    })();
  }, [selectedBucketId]);

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
  const stageTimeline = selectedGrow?.milestones
    ? STAGES_ORDERED.map((stage, i) => {
        const ts = selectedGrow.milestones?.[stage];
        if (!ts) return null;
        const nextStage = STAGES_ORDERED.find((s, j) => j > i && selectedGrow.milestones?.[s]);
        const nextTs = nextStage ? selectedGrow.milestones?.[nextStage] : null;
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
  const chartData = sensorData.map((r) => ({
    time: new Date(r.recorded_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }),
    pH: r.ph,
    EC: r.ec,
    PPM: r.ppm,
    "Water °F": r.water_temp_f,
    "Temp °F": r.ambient_temp_f,
    "Humidity %": r.ambient_humidity,
  }));

  return (
    <>
      <PageHeader
        title="Analytics"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Analytics" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Bucket Selector */}
        <div className="flex flex-wrap items-center gap-3">
          {buckets.length > 1 && (
            <Select value={selectedBucketId} onValueChange={(v) => setSelectedBucketId(v ?? "")}>
              <SelectTrigger className="w-56">
                <SelectValue>
                  {(() => {
                    const b = buckets.find((bk) => bk.id === selectedBucketId);
                    return b ? `#${b.position} ${b.label || b.strain_name || "Unnamed"}` : "Select bucket";
                  })()}
                </SelectValue>
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
                  <ResponsiveContainer width="100%" height={240}>
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
                  <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ fontSize: 12 }} />
                      <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
                      <Area type="monotone" dataKey="Water °F" stroke="#ef4444" fill="#ef444420" strokeWidth={2} dot={false} connectNulls />
                      <Area type="monotone" dataKey="Temp °F" stroke="#f97316" fill="#f9731620" strokeWidth={2} dot={false} connectNulls />
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
              {envSnapshots.length === 0 ? (
                <p className="py-6 text-center text-sm text-muted-foreground">No active bucket readings</p>
              ) : (
                <div className="space-y-2">
                  {envSnapshots.map((s, i) => (
                    <div key={i} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
                      <span className="font-medium min-w-[6rem]">{s.bucketLabel}</span>
                      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                        {s.ambient_temp_f != null && <span>🌡 {s.ambient_temp_f.toFixed(1)}°F</span>}
                        {s.ambient_humidity != null && <span>💧 {s.ambient_humidity.toFixed(0)}%</span>}
                        {s.water_temp_f != null && <span>🌊 {s.water_temp_f.toFixed(1)}°F</span>}
                        {s.ph != null && <span>pH {s.ph.toFixed(1)}</span>}
                        {s.ec != null && <span>EC {s.ec.toFixed(2)}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Grow Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Timer className="size-4" /> Grow Timeline
              {selectedGrow && <Badge variant="secondary" className="text-xs capitalize ml-2">{selectedGrow.stage}</Badge>}
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
                <ResponsiveContainer width="100%" height={Math.max(leaderboard.length * 40, 120)}>
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
                      <ResponsiveContainer width="100%" height={160}>
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
