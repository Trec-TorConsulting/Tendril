"use client";

import { useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { getAccessToken } from "@/lib/auth";
import { toast } from "sonner";
import { useGrow } from "@/hooks/use-grow";
import { useDashboardPriority } from "@/hooks/use-dashboard-priority";
import {
  listDevices,
  listTasks,
  listBuckets,
  completeTask,
  listSensorReadings,
  listTentReadings,
  getHealthCheckHistory,
  type DeviceResponse,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type TaskItem,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { OnboardingChecklist } from "@/components/onboarding-checklist";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, tempUnitLabel } from "@/lib/units";
import { getHumidityThreshold } from "@/lib/humidity-thresholds";
import { isActiveHydro } from "@/lib/terminology";
import { CameraGrid } from "@/components/camera-grid";
import { SensorSparkline } from "@/components/sparkline";
import { MultiMetricCard } from "@/components/multi-metric-card";
import { DashboardAiInsights } from "@/components/dashboard-ai-insights";
import { NextBestAction } from "@/components/next-best-action";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import { Droplets, Thermometer, Wind, CheckCircle2, TrendingUp, CalendarIcon, FlaskConical, AlertTriangle, Wrench, Heart } from "lucide-react";
import { cn, formatCalendarDate } from "@/lib/utils";
import { useApiSWR } from "@/lib/swr";
import { PullToRefresh } from "@/components/pull-to-refresh";
import { selectPreferredWaterReadings } from "@/lib/water-readings";
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

interface ClimateDataPoint {
  time: string;
  temperature: number | null;
  humidity: number | null;
  water_temp: number | null;
  ph: number | null;
  ppm: number | null;
  water_level: number | null;
}

const EMPTY_SENSOR_TRENDS: {
  ph: number[];
  ec: number[];
  ppm: number[];
  water_temp: number[];
  water_level: number[];
  orp: number[];
  temp: number[];
  humidity: number[];
} = { ph: [], ec: [], ppm: [], water_temp: [], water_level: [], orp: [], temp: [], humidity: [] };

// ─── Animations ─────────────────────────────────────────────────────────────────

const fadeUp = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

// ─── Main Page ──────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { selectedGrow, grows, loading: growLoading } = useGrow();
  const { prefs } = usePreferences();
  const {
    data: dashboardData,
    isLoading: loading,
    mutate,
  } = useApiSWR(
    selectedGrow ? ["dashboard", "home", selectedGrow.id, selectedGrow.tent_id] : null,
    async (token) => {
      const tentId = selectedGrow!.tent_id;
      const growId = selectedGrow!.id;

      const [devices, buckets, pendingTasks, tentReadings] = await Promise.all([
        listDevices(token).catch(() => [] as DeviceResponse[]),
        listBuckets(token, growId).catch(() => [] as BucketResponse[]),
        listTasks(token, { status: "pending", grow_cycle_id: growId }).catch(() => [] as TaskItem[]),
        listTentReadings(token, tentId, 50).catch(() => [] as TentReadingResponse[]),
      ]);

      const twelveHoursAgo = new Date(Date.now() - 12 * 60 * 60 * 1000);
      const freshTasks = pendingTasks.filter((t) => new Date(t.created_at ?? t.due_date ?? 0) > twelveHoursAgo);
      const alertTasks = freshTasks.filter((t) => t.category === "alert_response");
      const healthTasks = freshTasks.filter((t) => t.source === "ai" || t.category === "health_response");

      const prio = { urgent: 0, high: 1, medium: 2, low: 3 } as const;
      const sortedAlerts = [...alertTasks].sort((a, b) =>
        (prio[a.priority as keyof typeof prio] ?? 3) - (prio[b.priority as keyof typeof prio] ?? 3)
      );
      const sortedHealth = [...healthTasks].sort((a, b) =>
        (prio[a.priority as keyof typeof prio] ?? 3) - (prio[b.priority as keyof typeof prio] ?? 3)
      );
      const tasks = [...sortedAlerts, ...sortedHealth].slice(0, 5);

      const perBucketReadings = await Promise.all(
        buckets.map((bk) => listSensorReadings(token, bk.id, 30).catch(() => [] as SensorReadingResponse[]))
      );
      const growSensorReadings = perBucketReadings
        .flat()
        .sort((a, bb) => new Date(bb.recorded_at).getTime() - new Date(a.recorded_at).getTime());

      const waterReadings = selectPreferredWaterReadings(perBucketReadings, buckets, selectedGrow!.grow_type);

      const phVals = waterReadings.map((r) => r.ph).filter((v): v is number => v != null).slice(0, 30).reverse();
      const ecVals = waterReadings.map((r) => r.ec).filter((v): v is number => v != null).slice(0, 30).reverse();
      const ppmVals = waterReadings.map((r) => r.ppm).filter((v): v is number => v != null).slice(0, 30).reverse();
      const waterTempVals = waterReadings.map((r) => r.water_temp_f).filter((v): v is number => v != null).slice(0, 30).reverse();
      const waterLevelVals = waterReadings.map((r) => r.water_level_pct).filter((v): v is number => v != null).slice(0, 30).reverse();
      const orpVals = waterReadings.map((r) => r.orp).filter((v): v is number => v != null).slice(0, 30).reverse();
      const tentTempVals = tentReadings.map((r) => r.ambient_temp_f).filter((v): v is number => v != null).reverse();
      const tentHumVals = tentReadings.map((r) => r.ambient_humidity).filter((v): v is number => v != null).reverse();
      const bucketTempVals = growSensorReadings.map((r) => r.ambient_temp_f).filter((v): v is number => v != null).slice(0, 30).reverse();
      const bucketHumVals = growSensorReadings.map((r) => r.ambient_humidity).filter((v): v is number => v != null).slice(0, 30).reverse();
      const tempVals = tentTempVals.length > 0 ? tentTempVals : bucketTempVals;
      const humVals = tentHumVals.length > 0 ? tentHumVals : bucketHumVals;
      const sensorTrends = { ph: phVals, ec: ecVals, ppm: ppmVals, water_temp: waterTempVals, water_level: waterLevelVals, orp: orpVals, temp: tempVals, humidity: humVals };

      const latestTentReading = tentReadings[0];
      const latestBucketReading = waterReadings[0] ?? growSensorReadings[0];
      const tentTs = latestTentReading?.recorded_at ?? null;
      const bucketTs = latestBucketReading?.recorded_at ?? null;
      let lastReadingAt: string | null;
      if (tentTs && bucketTs) {
        lastReadingAt = tentTs > bucketTs ? tentTs : bucketTs;
      } else {
        lastReadingAt = tentTs ?? bucketTs ?? null;
      }

      const timeSlots = new Map<string, ClimateDataPoint>();
      for (const r of tentReadings.slice(0, 30).reverse()) {
        const time = new Date(r.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const existing = timeSlots.get(time) || { time, temperature: null, humidity: null, water_temp: null, ph: null, ppm: null, water_level: null };
        existing.temperature = r.ambient_temp_f ?? existing.temperature;
        existing.humidity = r.ambient_humidity ?? existing.humidity;
        timeSlots.set(time, existing);
      }
      for (const r of waterReadings.slice(0, 30).reverse()) {
        const time = new Date(r.recorded_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        const existing = timeSlots.get(time) || { time, temperature: null, humidity: null, water_temp: null, ph: null, ppm: null, water_level: null };
        existing.water_temp = r.water_temp_f ?? existing.water_temp;
        existing.ph = r.ph ?? existing.ph;
        existing.ppm = r.ppm ?? existing.ppm;
        existing.water_level = r.water_level_pct ?? existing.water_level;
        if (!existing.temperature && r.ambient_temp_f) existing.temperature = r.ambient_temp_f;
        if (!existing.humidity && r.ambient_humidity) existing.humidity = r.ambient_humidity;
        timeSlots.set(time, existing);
      }
      const climateData = Array.from(timeSlots.values());

      const healthScore = await getHealthCheckHistory(token, growId, 1)
        .then((hist) => (hist.items.length > 0 ? hist.items[0].score : null))
        .catch(() => null);

      return {
        devices,
        tasks,
        sensorTrends,
        lastReadingAt,
        climateData,
        healthScore,
      };
    },
  );

  const refresh = useCallback(async () => {
    await mutate();
  }, [mutate]);

  const devices = dashboardData?.devices ?? [];
  const tasks = dashboardData?.tasks ?? [];
  const sensorTrends = dashboardData?.sensorTrends ?? EMPTY_SENSOR_TRENDS;
  const lastReadingAt = dashboardData?.lastReadingAt ?? null;
  const climateData = dashboardData?.climateData ?? [];
  const healthScore = dashboardData?.healthScore ?? null;

  const handleCompleteTask = async (taskId: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await completeTask(taskId, token);
      await mutate(
        (prev) => (prev ? { ...prev, tasks: prev.tasks.filter((t) => t.id !== taskId) } : prev),
        { revalidate: false },
      );
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
  const updatedAgo = lastReadingAt ? timeAgo(lastReadingAt) : null;
  const isHydro = isActiveHydro(selectedGrow?.grow_type);
  const hasSensorData = sensorTrends.ph.length > 0 || sensorTrends.ec.length > 0 || sensorTrends.ppm.length > 0;
  const { topSectionOrder } = useDashboardPriority({ tasks, growStage: selectedGrow?.stage });

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
          {selectedGrow && (
            <div className="flex flex-col gap-4">
              {topSectionOrder.map((section) => {
                if (section === "next") {
                  return (
                    <motion.section key="next-best-action" {...fadeUp} transition={{ duration: 0.35 }}>
                      <NextBestAction
                        growId={selectedGrow.id}
                        growStage={selectedGrow.stage}
                        tasks={tasks}
                        healthScore={healthScore}
                      />
                    </motion.section>
                  );
                }

                if (section === "health") {
                  if (healthScore == null) return null;
                  return (
                    <motion.section key="health-status" {...fadeUp} transition={{ duration: 0.35 }}>
                      <div className="flex items-center gap-2 rounded-lg border bg-card px-4 py-2.5">
                        <Heart className={cn("size-4", healthScore >= 80 ? "text-emerald-500" : healthScore >= 50 ? "text-yellow-500" : "text-destructive")} />
                        <span className="text-sm font-medium">Health</span>
                        <Badge variant={healthScore >= 80 ? "default" : healthScore >= 50 ? "secondary" : "destructive"} className="text-xs">
                          {healthScore >= 80 ? "Healthy" : healthScore >= 50 ? "Needs Attention" : "Critical"} — {healthScore}/100
                        </Badge>
                      </div>
                    </motion.section>
                  );
                }

                return (
                  <motion.section key="ai-guidance" {...fadeUp} transition={{ duration: 0.35 }}>
                    <DashboardAiInsights
                      growId={selectedGrow.id}
                      growStage={selectedGrow.stage}
                      hasSensorData={hasSensorData}
                      sensorTrends={sensorTrends}
                    />
                  </motion.section>
                );
              })}
            </div>
          )}

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
                        status: getHumidityThreshold(latestHumidity, selectedGrow?.stage).status,
                        hint: getHumidityThreshold(latestHumidity, selectedGrow?.stage).hint,
                      },
                      {
                        label: "Water Temp",
                        value: latestWaterTemp != null ? formatTemp(latestWaterTemp, "f", prefs.temp_unit, 0) : "—",
                        status: latestWaterTemp != null ? (latestWaterTemp >= 62 && latestWaterTemp <= 70 ? "optimal" : "warning") : "unknown",
                        hint: latestWaterTemp != null && latestWaterTemp < 62 ? "Too cold — target 64–70°F" : latestWaterTemp != null && latestWaterTemp > 70 ? "Too warm — root rot risk above 72°F. Target 64–70°F" : undefined,
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
                        status: sensorTrends.ph.length > 0 ? (sensorTrends.ph[sensorTrends.ph.length - 1] >= 5.5 && sensorTrends.ph[sensorTrends.ph.length - 1] <= 6.2 ? "optimal" : "warning") : "unknown",
                        hint: sensorTrends.ph.length > 0 && sensorTrends.ph[sensorTrends.ph.length - 1] < 5.5 ? "Too acidic — target 5.5–6.2" : sensorTrends.ph.length > 0 && sensorTrends.ph[sensorTrends.ph.length - 1] > 6.2 ? "Too alkaline — target 5.5–6.2" : undefined,
                      },
                      {
                        label: "PPM",
                        value: latestPpm != null ? `${Math.round(latestPpm)}` : "—",
                        status: latestPpm != null ? (latestPpm >= 400 && latestPpm <= 1500 ? "optimal" : "warning") : "unknown",
                        hint: latestPpm != null && latestPpm < 400 ? "Nutrients too low — target 400–1500 PPM" : latestPpm != null && latestPpm > 1500 ? "Nutrients too high — target 400–1500 PPM" : undefined,
                      },
                      ...(sensorTrends.orp.length > 0 ? [{
                        label: "ORP",
                        value: `${Math.round(sensorTrends.orp[sensorTrends.orp.length - 1])} mV`,
                        status: (sensorTrends.orp[sensorTrends.orp.length - 1] >= 300 && sensorTrends.orp[sensorTrends.orp.length - 1] <= 450 ? "optimal" : "warning") as "optimal" | "warning",
                        hint: sensorTrends.orp[sensorTrends.orp.length - 1] < 300 ? "ORP low — anaerobic risk. Target 300–450 mV" : sensorTrends.orp[sensorTrends.orp.length - 1] > 450 ? "ORP high — too oxidizing. Target 300–450 mV" : undefined,
                      }] : []),
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
                    status={getHumidityThreshold(latestHumidity, selectedGrow?.stage).status}
                    icon={<Droplets className="size-5" />}
                    updatedAgo={updatedAgo}
                    hint={getHumidityThreshold(latestHumidity, selectedGrow?.stage).hint}
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
                    status={sensorTrends.ph.length > 0 ? (sensorTrends.ph[sensorTrends.ph.length - 1] >= 6.0 && sensorTrends.ph[sensorTrends.ph.length - 1] <= 7.0 ? "optimal" : "warning") : "unknown"}
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
                        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
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
