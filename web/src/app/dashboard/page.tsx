"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { getAccessToken } from "@/lib/auth";
import { toast } from "sonner";
import { useGrow } from "@/hooks/use-grow";
import { useLayoutMode } from "@/hooks/use-layout-mode";
import {
  listDevices,
  listTasks,
  listBuckets,
  completeTask,
  getHarvestCountdown,
  listSensorReadings,
  listTentReadings,
  type DeviceResponse,
  type HarvestCountdownItem,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type TaskItem,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { OnboardingChecklist } from "@/components/onboarding-checklist";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, tempUnitLabel } from "@/lib/units";
import { isActiveHydro } from "@/lib/terminology";
import { CameraGrid } from "@/components/camera-grid";
import { Sparkline, SensorSparkline } from "@/components/sparkline";
import { MultiMetricCard } from "@/components/multi-metric-card";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Sprout, Droplets, Thermometer, Wind, Waves, CheckCircle2, TrendingUp, CalendarIcon, FlaskConical, AlertTriangle, Wrench } from "lucide-react";
import { cn, formatCalendarDate } from "@/lib/utils";
import { PullToRefresh } from "@/components/pull-to-refresh";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
  Tooltip as RechartsTooltip,
} from "recharts";

// ─── Helpers ────────────────────────────────────────────────────────────────────

function timeAgo(isoString: string): string {
  const seconds = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

// ─── Types ──────────────────────────────────────────────────────────────────────

interface PlantCardData {
  id: string;
  name: string;
  stage: string;
  dayInStage: number;
  stageDuration: number;
  moistureHistory: number[];
  growType: string;
  growId: string;
  lastReadingAt: string | null;
}

interface ClimateDataPoint {
  time: string;
  temperature: number | null;
  humidity: number | null;
  water_temp: number | null;
  ph: number | null;
  ppm: number | null;
  water_level: number | null;
}

// Stage durations (days) used for progress calculation
const STAGE_DURATIONS: Record<string, number> = {
  germination: 7,
  seedling: 14,
  vegetative: 30,
  flowering: 56,
  drying: 10,
  curing: 21,
};

// ─── Animations ─────────────────────────────────────────────────────────────────

const fadeUp = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

const stagger = {
  animate: { transition: { staggerChildren: 0.06 } },
};

// ─── Main Page ──────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { selectedGrow, grows, loading: growLoading } = useGrow();
  const { prefs } = usePreferences();
  const { mode, config } = useLayoutMode();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [countdown, setCountdown] = useState<HarvestCountdownItem[]>([]);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [sensorTrends, setSensorTrends] = useState<{
    ph: number[];
    ec: number[];
    ppm: number[];
    water_temp: number[];
    water_level: number[];
    temp: number[];
    humidity: number[];
  }>({ ph: [], ec: [], ppm: [], water_temp: [], water_level: [], temp: [], humidity: [] });
  const [lastReadingAt, setLastReadingAt] = useState<string | null>(null);
  const [bucketLastReading, setBucketLastReading] = useState<Map<string, string>>(new Map());
  const [climateData, setClimateData] = useState<ClimateDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !selectedGrow) { setLoading(false); return; }
    try {
      const tentId = selectedGrow.tent_id;
      const growId = selectedGrow.id;

      const [d, hc, b, tk, tentReadings] = await Promise.all([
        listDevices(token).catch(() => [] as DeviceResponse[]),
        getHarvestCountdown(token).catch(() => [] as HarvestCountdownItem[]),
        listBuckets(token, growId).catch(() => [] as BucketResponse[]),
        listTasks(token, { status: "pending", grow_cycle_id: growId }).catch(() => [] as TaskItem[]),
        listTentReadings(token, tentId, 50).catch(() => [] as TentReadingResponse[]),
      ]);
      setDevices(d);
      setCountdown(hc.filter((h) => h.grow_id === growId));
      setBuckets(b);
      // Only show actionable tasks: alerts + health fix actions
      // Daily routines live on the full Tasks page — they don't belong here
      const alertTasks = tk.filter((t) => t.category === "alert_response");
      const healthTasks = tk.filter((t) => t.source === "ai" || t.category === "health_response");

      // Priority sort: alerts by severity, health by due date
      const sortedAlerts = [...alertTasks].sort((a, b) => {
        const prio = { urgent: 0, high: 1, medium: 2, low: 3 };
        return (prio[a.priority as keyof typeof prio] ?? 3) - (prio[b.priority as keyof typeof prio] ?? 3);
      });
      const sortedHealth = [...healthTasks].sort((a, b) => {
        if (!a.due_date && !b.due_date) return 0;
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      });

      setTasks([
        ...sortedAlerts,
        ...sortedHealth.slice(0, 1), // Only the NEXT health action
      ]);

      // Fetch sensor readings per bucket (same as grow detail page) so sparse
      // metrics like pH and water_level are not lost in a global top-50 slice.
      const perBucketReadings = await Promise.all(
        b.map((bk) => listSensorReadings(token, bk.id, 30).catch(() => [] as SensorReadingResponse[]))
      );
      const growSensorReadings = perBucketReadings
        .flat()
        .sort((a, bb) => new Date(bb.recorded_at).getTime() - new Date(a.recorded_at).getTime());

      // Build each metric independently so sparse metrics are not dropped
      const phVals = growSensorReadings.map((r) => r.ph).filter((v): v is number => v != null).slice(0, 30).reverse();
      const ecVals = growSensorReadings.map((r) => r.ec).filter((v): v is number => v != null).slice(0, 30).reverse();
      const ppmVals = growSensorReadings.map((r) => r.ppm).filter((v): v is number => v != null).slice(0, 30).reverse();
      const waterTempVals = growSensorReadings.map((r) => r.water_temp_f).filter((v): v is number => v != null).slice(0, 30).reverse();
      const waterLevelVals = growSensorReadings.map((r) => r.water_level_pct).filter((v): v is number => v != null).slice(0, 30).reverse();
      const tentTempVals = tentReadings.map((r) => r.ambient_temp_f).filter((v): v is number => v != null).reverse();
      const tentHumVals = tentReadings.map((r) => r.ambient_humidity).filter((v): v is number => v != null).reverse();
      const bucketTempVals = growSensorReadings.map((r) => r.ambient_temp_f).filter((v): v is number => v != null).slice(0, 30).reverse();
      const bucketHumVals = growSensorReadings.map((r) => r.ambient_humidity).filter((v): v is number => v != null).slice(0, 30).reverse();
      const tempVals = tentTempVals.length > 0 ? tentTempVals : bucketTempVals;
      const humVals = tentHumVals.length > 0 ? tentHumVals : bucketHumVals;
      setSensorTrends({ ph: phVals, ec: ecVals, ppm: ppmVals, water_temp: waterTempVals, water_level: waterLevelVals, temp: tempVals, humidity: humVals });
      // Track when the latest reading was recorded (bucket for hydro, tent for others)
      const latestTentReading = tentReadings[0];
      const latestBucketReading = growSensorReadings[0];
      if (isActiveHydro(selectedGrow?.grow_type) && latestBucketReading?.recorded_at) {
        setLastReadingAt(latestBucketReading.recorded_at);
      } else {
        setLastReadingAt(latestTentReading?.recorded_at ?? null);
      }

      // Build per-bucket latest reading timestamp map
      const bucketLatest = new Map<string, string>();
      for (const r of growSensorReadings) {
        if (!bucketLatest.has(r.bucket_id) || r.recorded_at > bucketLatest.get(r.bucket_id)!) {
          bucketLatest.set(r.bucket_id, r.recorded_at);
        }
      }
      setBucketLastReading(bucketLatest);

      // Build 24h analytics chart combining tent + sensor data by timestamp
      const timeSlots = new Map<string, ClimateDataPoint>();
      for (const r of tentReadings.slice(0, 30).reverse()) {
        const time = new Date(r.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const existing = timeSlots.get(time) || { time, temperature: null, humidity: null, water_temp: null, ph: null, ppm: null, water_level: null };
        existing.temperature = r.ambient_temp_f ?? existing.temperature;
        existing.humidity = r.ambient_humidity ?? existing.humidity;
        timeSlots.set(time, existing);
      }
      for (const r of growSensorReadings.slice(0, 30).reverse()) {
        const time = new Date(r.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const existing = timeSlots.get(time) || { time, temperature: null, humidity: null, water_temp: null, ph: null, ppm: null, water_level: null };
        existing.water_temp = r.water_temp_f ?? existing.water_temp;
        existing.ph = r.ph ?? existing.ph;
        existing.ppm = r.ppm ?? existing.ppm;
        existing.water_level = r.water_level_pct ?? existing.water_level;
        // Fallback ambient from bucket if tent not available
        if (!existing.temperature && r.ambient_temp_f) existing.temperature = r.ambient_temp_f;
        if (!existing.humidity && r.ambient_humidity) existing.humidity = r.ambient_humidity;
        timeSlots.set(time, existing);
      }
      setClimateData(Array.from(timeSlots.values()));
    } finally {
      setLoading(false);
    }
  }, [selectedGrow]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCompleteTask = async (taskId: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await completeTask(taskId, token);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to complete task");
    }
  };

  // Derive environment stats from latest readings
  const latestTemp = sensorTrends.temp[sensorTrends.temp.length - 1];
  const latestHumidity = sensorTrends.humidity[sensorTrends.humidity.length - 1];
  const latestWaterTemp = sensorTrends.water_temp[sensorTrends.water_temp.length - 1];
  const latestPpm = sensorTrends.ppm[sensorTrends.ppm.length - 1];
  const latestCO2 = null; // Placeholder — CO2 sensor not yet in data model
  const envValue =
    latestTemp != null || latestHumidity != null
      ? `${latestTemp != null ? formatTemp(latestTemp, "f", prefs.temp_unit, 0) : "—"}${latestHumidity != null ? ` / ${latestHumidity.toFixed(0)}%` : ""}`
      : "—";
  const envStatus =
    latestTemp != null && latestHumidity != null
      ? (latestTemp >= 68 && latestTemp <= 82 && latestHumidity >= 40 && latestHumidity <= 70 ? "optimal" : "warning")
      : "unknown";
  const updatedAgo = lastReadingAt ? timeAgo(lastReadingAt) : null;
  const isHydro = isActiveHydro(selectedGrow?.grow_type);

  // Build plant cards from selected grow's buckets
  const maxCards = mode === "pro" || mode === "commercial" ? 16 : mode === "beginner" ? 4 : 8;
  const plantCards: PlantCardData[] = selectedGrow
    ? buckets
        .filter((b) => b.status === "active")
        .slice(0, maxCards)
        .map((b) => {
          const daysSinceStart = Math.floor(
            (Date.now() - new Date(selectedGrow.started_at).getTime()) / 86400000
          );
          const stageDuration = STAGE_DURATIONS[b.growth_stage || selectedGrow.stage] || 30;
          const stageStart = selectedGrow.milestones?.[selectedGrow.stage]
            ? Math.floor((Date.now() - new Date(selectedGrow.milestones[selectedGrow.stage]).getTime()) / 86400000)
            : Math.min(daysSinceStart, stageDuration);
          return {
            id: b.id,
            name: b.label || b.strain_name || `Bucket ${b.position}`,
            stage: b.growth_stage || selectedGrow.stage,
            dayInStage: stageStart,
            stageDuration,
            moistureHistory: sensorTrends.humidity.slice(-10),
            growType: selectedGrow.grow_type,
            growId: selectedGrow.id,
            lastReadingAt: bucketLastReading.get(b.id) ?? null,
          };
        })
    : [];

  if (loading || growLoading) {
    return (
      <>
        <PageHeader title="Dashboard" />
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          <div className="grid gap-4 sm:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
          <Skeleton className="h-64 rounded-xl" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-56 rounded-xl" />
            ))}
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader title={selectedGrow ? `Dashboard — ${selectedGrow.name}` : "Dashboard"} />
      <PullToRefresh onRefresh={refresh}>
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          {/* ─── Camera Feeds ──────────────────────────────────── */}
          {selectedGrow && (
            <motion.section {...fadeUp} transition={{ duration: 0.4 }}>
              <CameraGrid key={selectedGrow.tent_id} tentId={selectedGrow.tent_id} hideEmpty />
            </motion.section>
          )}

          {/* ─── Environment Health Header ─────────────────────────── */}
          <motion.section {...fadeUp} transition={{ duration: 0.4 }}>
            <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
              {isHydro ? (
                <>
                  <MultiMetricCard
                    title="Environment"
                    icon={<Thermometer className="size-5" />}
                    metrics={[
                      {
                        label: "Tent Temp",
                        value: latestTemp != null ? formatTemp(latestTemp, "f", prefs.temp_unit, 0) : "—",
                        status: latestTemp != null ? (latestTemp >= 68 && latestTemp <= 82 ? "optimal" : "warning") : "unknown",
                        hint: latestTemp != null && latestTemp < 68 ? "Too cold — target 68–82°F" : latestTemp != null && latestTemp > 82 ? "Too hot — target 68–82°F" : undefined,
                      },
                      {
                        label: "Humidity",
                        value: latestHumidity != null ? `${latestHumidity.toFixed(0)}%` : "—",
                        status: latestHumidity != null ? (latestHumidity >= 40 && latestHumidity <= 70 ? "optimal" : "warning") : "unknown",
                        hint: latestHumidity != null && latestHumidity < 40 ? "Too dry — target 40–70%" : latestHumidity != null && latestHumidity > 70 ? "Too humid — target 40–70%" : undefined,
                      },
                      {
                        label: "Water Temp",
                        value: latestWaterTemp != null ? formatTemp(latestWaterTemp, "f", prefs.temp_unit, 0) : "—",
                        status: latestWaterTemp != null ? (latestWaterTemp >= 62 && latestWaterTemp <= 72 ? "optimal" : "warning") : "unknown",
                        hint: latestWaterTemp != null && latestWaterTemp < 62 ? "Too cold — target 62–72°F" : latestWaterTemp != null && latestWaterTemp > 72 ? "Too warm — risk of root rot. Target 62–72°F" : undefined,
                      },
                    ]}
                    updatedAgo={updatedAgo}
                  />
                  <MultiMetricCard
                    title="Nutrients"
                    icon={<FlaskConical className="size-5" />}
                    metrics={[
                      {
                        label: "pH",
                        value: sensorTrends.ph.length > 0 ? sensorTrends.ph[sensorTrends.ph.length - 1].toFixed(1) : "—",
                        status: sensorTrends.ph.length > 0 ? (sensorTrends.ph[sensorTrends.ph.length - 1] >= 5.5 && sensorTrends.ph[sensorTrends.ph.length - 1] <= 6.5 ? "optimal" : "warning") : "unknown",
                        hint: sensorTrends.ph.length > 0 && sensorTrends.ph[sensorTrends.ph.length - 1] < 5.5 ? "Too acidic — target 5.5–6.5" : sensorTrends.ph.length > 0 && sensorTrends.ph[sensorTrends.ph.length - 1] > 6.5 ? "Too alkaline — target 5.5–6.5" : undefined,
                      },
                      {
                        label: "PPM",
                        value: latestPpm != null ? `${Math.round(latestPpm)}` : "—",
                        status: latestPpm != null ? (latestPpm >= 400 && latestPpm <= 1500 ? "optimal" : "warning") : "unknown",
                        hint: latestPpm != null && latestPpm < 400 ? "Nutrients too low — target 400–1500 PPM" : latestPpm != null && latestPpm > 1500 ? "Nutrients too high — target 400–1500 PPM" : undefined,
                      },
                      {
                        label: "Water Level",
                        value: sensorTrends.water_level.length > 0 ? `${Math.round(sensorTrends.water_level[sensorTrends.water_level.length - 1])}%` : "—",
                        status: sensorTrends.water_level.length > 0 ? (sensorTrends.water_level[sensorTrends.water_level.length - 1] >= 20 ? "optimal" : "warning") : "unknown",
                        hint: sensorTrends.water_level.length > 0 && sensorTrends.water_level[sensorTrends.water_level.length - 1] < 20 ? "Water level critically low — refill reservoir" : undefined,
                      },
                    ]}
                    updatedAgo={updatedAgo}
                  />
                  <EnvironmentBadgeCard
                    label="EC"
                    value={sensorTrends.ec.length > 0 ? sensorTrends.ec[sensorTrends.ec.length - 1].toFixed(2) : "—"}
                    status={sensorTrends.ec.length > 0 ? (sensorTrends.ec[sensorTrends.ec.length - 1] >= 0.8 && sensorTrends.ec[sensorTrends.ec.length - 1] <= 2.5 ? "optimal" : "warning") : "unknown"}
                    icon={<Droplets className="size-5" />}
                    updatedAgo={updatedAgo}
                    hint={sensorTrends.ec.length > 0 && sensorTrends.ec[sensorTrends.ec.length - 1] < 0.8 ? "EC too low — target 0.8–2.5" : sensorTrends.ec.length > 0 && sensorTrends.ec[sensorTrends.ec.length - 1] > 2.5 ? "EC too high — risk of nutrient burn. Target 0.8–2.5" : undefined}
                  />
                  <EnvironmentBadgeCard
                    label="CO₂"
                    value={latestCO2 != null ? `${latestCO2} ppm` : "—"}
                    status="unknown"
                    icon={<Wind className="size-5" />}
                    updatedAgo={updatedAgo}
                  />
                </>
              ) : (
                <>
                  <EnvironmentBadgeCard
                    label="Temperature"
                    value={latestTemp != null ? formatTemp(latestTemp, "f", prefs.temp_unit, 0) : "—"}
                    status={latestTemp != null ? (latestTemp >= 68 && latestTemp <= 82 ? "optimal" : "warning") : "unknown"}
                    icon={<Thermometer className="size-5" />}
                    updatedAgo={updatedAgo}
                  />
                  <EnvironmentBadgeCard
                    label="Humidity"
                    value={latestHumidity != null ? `${latestHumidity.toFixed(0)}%` : "—"}
                    status={latestHumidity != null ? (latestHumidity >= 40 && latestHumidity <= 70 ? "optimal" : "warning") : "unknown"}
                    icon={<Droplets className="size-5" />}
                    updatedAgo={updatedAgo}
                  />
                  <EnvironmentBadgeCard
                    label="CO₂"
                    value={latestCO2 != null ? `${latestCO2} ppm` : "—"}
                    status="unknown"
                    icon={<Wind className="size-5" />}
                    updatedAgo={updatedAgo}
                  />
                  <EnvironmentBadgeCard
                    label="pH"
                    value={sensorTrends.ph.length > 0 ? sensorTrends.ph[sensorTrends.ph.length - 1].toFixed(1) : "—"}
                    status={sensorTrends.ph.length > 0 ? (sensorTrends.ph[sensorTrends.ph.length - 1] >= 5.5 && sensorTrends.ph[sensorTrends.ph.length - 1] <= 6.5 ? "optimal" : "warning") : "unknown"}
                    icon={<FlaskConical className="size-5" />}
                    updatedAgo={updatedAgo}
                  />
                </>
              )}
            </div>
          </motion.section>

          {/* ─── Main Content: Grid + Sidebar ─────────────────────── */}
          <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
            {/* Left Column */}
            <div className="flex flex-col gap-6">
              {/* ─── Plant Grid ────────────────────────────────────── */}
              {plantCards.length > 0 && (
                <motion.section {...fadeUp} transition={{ duration: 0.4, delay: 0.1 }}>
                  <div className="mb-3 flex items-center justify-between">
                    <h2 className="flex items-center gap-2 text-lg font-semibold">
                      <Sprout className="size-5 text-primary" />
                      Buckets
                    </h2>
                    <Button variant="ghost" size="sm" render={<Link href={`/dashboard/grows/${selectedGrow?.id}`} />}>
                      View grow
                    </Button>
                  </div>
                  <motion.div
                    className={cn(
                      "grid gap-4",
                      config.density === "compact"
                        ? "grid-cols-2 sm:grid-cols-3 xl:grid-cols-5"
                        : config.density === "relaxed"
                          ? "sm:grid-cols-2"
                          : "sm:grid-cols-2 xl:grid-cols-4"
                    )}
                    variants={stagger}
                    initial="initial"
                    animate="animate"
                  >
                    {plantCards.map((plant) => (
                      <PlantCard key={plant.id} plant={plant} />
                    ))}
                  </motion.div>
                </motion.section>
              )}

              {/* ─── Analytics ─────────────────────────────── */}
              {climateData.length >= 2 && (
                <motion.section {...fadeUp} transition={{ duration: 0.4, delay: 0.2 }}>
                  <Card className="border-border/50 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="size-5 text-primary" />
                        Grow Analytics — 24h
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={climateData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" opacity={0.5} />
                            <XAxis
                              dataKey="time"
                              tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                              tickLine={false}
                              axisLine={false}
                            />
                            <YAxis
                              yAxisId="temp"
                              tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                              tickLine={false}
                              axisLine={false}
                              domain={["dataMin - 5", "dataMax + 5"]}
                            />
                            <YAxis
                              yAxisId="pct"
                              orientation="right"
                              tick={{ fontSize: 11, fill: "var(--color-muted-foreground)" }}
                              tickLine={false}
                              axisLine={false}
                              domain={[0, 100]}
                            />
                            <RechartsTooltip
                              contentStyle={{
                                backgroundColor: "var(--color-card)",
                                border: "1px solid var(--color-border)",
                                borderRadius: "8px",
                                fontSize: 12,
                              }}
                            />
                            <Legend
                              wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
                            />
                            <Line
                              yAxisId="temp"
                              type="monotone"
                              dataKey="temperature"
                              stroke="oklch(0.65 0.15 30)"
                              strokeWidth={2}
                              dot={false}
                              name={`Tent Temp (${tempUnitLabel(prefs.temp_unit)})`}
                              connectNulls
                            />
                            <Line
                              yAxisId="pct"
                              type="monotone"
                              dataKey="humidity"
                              stroke="oklch(0.65 0.14 200)"
                              strokeWidth={2}
                              dot={false}
                              name="Humidity (%)"
                              connectNulls
                            />
                            {isHydro && (
                              <>
                                <Line
                                  yAxisId="temp"
                                  type="monotone"
                                  dataKey="water_temp"
                                  stroke="#f97316"
                                  strokeWidth={2}
                                  dot={false}
                                  name={`Water Temp (${tempUnitLabel(prefs.temp_unit)})`}
                                  connectNulls
                                />
                                <Line
                                  yAxisId="temp"
                                  type="monotone"
                                  dataKey="ph"
                                  stroke="#10b981"
                                  strokeWidth={2}
                                  dot={false}
                                  name="pH"
                                  connectNulls
                                />
                                <Line
                                  yAxisId="temp"
                                  type="monotone"
                                  dataKey="ppm"
                                  stroke="#3b82f6"
                                  strokeWidth={1.5}
                                  strokeDasharray="4 2"
                                  dot={false}
                                  name="PPM"
                                  connectNulls
                                />
                                <Line
                                  yAxisId="pct"
                                  type="monotone"
                                  dataKey="water_level"
                                  stroke="#8b5cf6"
                                  strokeWidth={1.5}
                                  strokeDasharray="4 2"
                                  dot={false}
                                  name="Water Level (%)"
                                  connectNulls
                                />
                              </>
                            )}
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </motion.section>
              )}
            </div>

            {/* ─── Right Sidebar: Tasks ──────────────────── */}
            <motion.aside {...fadeUp} transition={{ duration: 0.4, delay: 0.15 }} className="flex flex-col gap-4">
              <Card className="border-border/50 backdrop-blur-sm">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-base">
                      <CheckCircle2 className="size-4 text-primary" />
                      Tasks
                    </CardTitle>
                    <Button variant="ghost" size="sm" className="text-xs text-muted-foreground" render={<Link href="/dashboard/tasks" />}>
                      View all
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  {tasks.length === 0 && (
                    <p className="text-sm text-muted-foreground py-4 text-center">
                      No issues detected. Your grow is on track.
                    </p>
                  )}
                  <AnimatePresence mode="popLayout">
                    {tasks.map((task) => {
                      const isAlert = task.category === "alert_response";
                      const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "completed";

                      return (
                        <motion.div
                          key={task.id}
                          layout
                          {...fadeUp}
                          transition={{ duration: 0.2 }}
                          className={cn(
                            "flex items-start gap-3 rounded-lg border p-3 transition-colors",
                            isAlert ? "border-red-500/60 bg-red-500/5" : "border-amber-500/50 bg-amber-500/5",
                          )}
                        >
                          <button
                            onClick={() => handleCompleteTask(task.id)}
                            className={cn(
                              "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full border-2 transition",
                              isAlert ? "border-red-500/60 hover:border-red-500 hover:bg-red-500/10" :
                              "border-amber-500/60 hover:border-amber-500 hover:bg-amber-500/10",
                            )}
                            aria-label={`Complete task: ${task.title}`}
                          >
                            <CheckCircle2 className="size-3 text-transparent" />
                          </button>
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-wrap items-center gap-1.5">
                              {isAlert ? <AlertTriangle className="size-3.5 text-red-500 shrink-0" /> : <Wrench className="size-3 text-amber-500 shrink-0" />}
                              <p className={cn(
                                "text-sm leading-tight truncate",
                                isAlert ? "font-semibold" : "font-medium",
                              )}>{task.title}</p>
                            </div>
                            {task.description && (
                              <p className="mt-0.5 text-xs text-muted-foreground line-clamp-2">{task.description}</p>
                            )}
                            <div className="mt-1 flex flex-wrap items-center gap-2">
                              <Badge variant={isAlert ? "destructive" : "outline"} className={cn("text-[10px] px-1.5 py-0", !isAlert && "border-amber-500/50 text-amber-600")}>
                                {isAlert ? "Action Required" : "Fix Issue"}
                              </Badge>
                              {task.due_date && (
                                <span className={cn("flex items-center gap-0.5 text-[10px]", isOverdue ? "text-red-500 font-medium" : "text-muted-foreground")}>
                                  <CalendarIcon className="size-2.5" />
                                  {isOverdue ? "Overdue" : formatCalendarDate(task.due_date)}
                                </span>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </AnimatePresence>
                </CardContent>
              </Card>

              {/* Quick sensor stats sidebar cards */}
              {sensorTrends.ec.length >= 2 ? (
                <Card className="border-border/50 backdrop-blur-sm">
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-muted-foreground">EC Level</span>
                      <span className="text-lg font-bold">
                        {sensorTrends.ec[sensorTrends.ec.length - 1]?.toFixed(2)}
                      </span>
                    </div>
                    <SensorSparkline
                      data={sensorTrends.ec}
                      ranges={{ min: 1.0, max: 2.5 }}
                      height={36}
                    />
                  </CardContent>
                </Card>
              ) : sensorTrends.water_level.length >= 2 && (
                <Card className="border-border/50 backdrop-blur-sm">
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-muted-foreground">Water Level</span>
                      <span className="text-lg font-bold">
                        {Math.round(sensorTrends.water_level[sensorTrends.water_level.length - 1])}%
                      </span>
                    </div>
                    <SensorSparkline
                      data={sensorTrends.water_level}
                      ranges={{ min: 20, max: 100 }}
                      height={36}
                    />
                  </CardContent>
                </Card>
              )}
            </motion.aside>
          </div>

          {/* ─── Onboarding / Empty State ──────────────────────────── */}
          {grows.length === 0 || devices.length === 0 ? (
            <OnboardingChecklist
              hasTents={!!selectedGrow?.tent_id}
              hasGrows={grows.length > 0}
              hasDevices={devices.length > 0}
            />
          ) : null}
        </div>
      </PullToRefresh>
    </>
  );
}

// ─── Sub-Components ───────────────────────────────────────────────────────────

function EnvironmentBadgeCard({
  label,
  value,
  status,
  icon,
  updatedAgo,
  hint,
}: {
  label: string;
  value: string;
  status: "optimal" | "warning" | "unknown";
  icon: React.ReactNode;
  updatedAgo?: string | null;
  hint?: string;
}) {
  const statusColor = {
    optimal: "bg-primary/10 text-primary border-primary/20",
    warning: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    unknown: "bg-muted text-muted-foreground border-border",
  }[status];

  const statusLabel = {
    optimal: "Optimal",
    warning: "Attention",
    unknown: "No data",
  }[status];

  const badge = (
    <Badge
      variant="outline"
      className={`text-[10px] ${status === "optimal" ? "border-primary/40 text-primary" : status === "warning" ? "border-orange-500/40 text-orange-500" : ""}`}
    >
      {statusLabel}
    </Badge>
  );

  return (
    <Card className={`border ${statusColor.split(" ").find((c) => c.startsWith("border-")) || "border-border"} backdrop-blur-sm`}>
      <CardContent className="flex items-center gap-4 py-4">
        <div className={`flex size-10 items-center justify-center rounded-lg ${statusColor.split(" ").slice(0, 2).join(" ")}`}>
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-xl font-bold">{value}</p>
          {updatedAgo && <p className="text-[10px] text-muted-foreground">{updatedAgo}</p>}
        </div>
        {status === "warning" && hint ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger className="cursor-help">{badge}</TooltipTrigger>
              <TooltipContent>{hint}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : badge}
      </CardContent>
    </Card>
  );
}

function PlantCard({ plant }: { plant: PlantCardData }) {
  const progress = Math.min(100, (plant.dayInStage / plant.stageDuration) * 100);

  return (
    <motion.div variants={fadeUp}>
      <Link href={`/dashboard/grows/${plant.growId}`} className="block">
        <Card className="group border-border/50 backdrop-blur-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 cursor-pointer">
          {/* Plant thumbnail placeholder */}
          <div className="relative mx-4 mt-4 flex h-28 items-center justify-center rounded-lg bg-gradient-to-br from-primary/5 to-primary/15 overflow-hidden">
            <Sprout className="size-10 text-primary/60" />
            <div className="absolute top-2 right-2">
              <Badge variant="secondary" className="text-[10px] capitalize">
                {plant.stage}
              </Badge>
            </div>
          </div>

          <CardContent className="pt-3">
            <h3 className="font-medium text-sm truncate">{plant.name}</h3>
            <div className="flex items-center justify-between mt-0.5">
              <p className="text-xs text-muted-foreground">{plant.growType}</p>
              {plant.lastReadingAt && (
                <p className="text-[10px] text-muted-foreground">{timeAgo(plant.lastReadingAt)}</p>
              )}
            </div>

            {/* Growth progress */}
            <div className="mt-3">
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                <span className="capitalize">{plant.stage}</span>
                <span>Day {plant.dayInStage}/{plant.stageDuration}</span>
              </div>
              <Progress value={progress} className="h-1.5" />
            </div>

            {/* Moisture sparkline */}
            {plant.moistureHistory.length >= 2 && (
              <div className="mt-3">
                <p className="text-[10px] text-muted-foreground mb-1">Moisture</p>
                <Sparkline
                  data={plant.moistureHistory}
                  color="oklch(0.65 0.14 200)"
                  height={24}
                />
              </div>
            )}
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
