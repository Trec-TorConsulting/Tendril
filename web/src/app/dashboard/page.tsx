"use client";

import { useCallback, useMemo } from "react";
import { getAccessToken } from "@/lib/auth";
import { toast } from "sonner";
import { useGrow } from "@/hooks/use-grow";
import { useLayoutMode } from "@/hooks/use-layout-mode";
import {
  listDevices,
  listTasks,
  listBuckets,
  completeTask,
  listSensorReadings,
  listTentReadings,
  getHealthCheckHistory,
  getHarvestCountdown,
  type DeviceResponse,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type TaskItem,
  type HarvestCountdownItem,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { OnboardingChecklist } from "@/components/onboarding-checklist";
import { usePreferences } from "@/hooks/use-preferences";
import { isActiveHydro } from "@/lib/terminology";
import { Skeleton } from "@/components/ui/skeleton";
import { useApiSWR } from "@/lib/swr";
import { PullToRefresh } from "@/components/pull-to-refresh";
import { selectPreferredWaterReadings } from "@/lib/water-readings";
import {
  buildDashboardMetrics,
  CommandCenterView,
  BentoView,
  type AdaptiveDashboardProps,
} from "@/components/dashboard/adaptive-dashboard";
import type { PreviewGrow } from "@/components/dashboard-preview/preview-data";

// ─── Helpers ────────────────────────────────────────────────────────────────────


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

export default function DashboardPage() {
  const { selectedGrow, grows, loading: growLoading } = useGrow();
  const { prefs } = usePreferences();
  const { mode, config } = useLayoutMode();
  const {
    data: dashboardData,
    isLoading: loading,
    mutate,
  } = useApiSWR(
    selectedGrow ? ["dashboard", "home", selectedGrow.id, selectedGrow.tent_id] : null,
    async (token) => {
      const tentId = selectedGrow!.tent_id;
      const growId = selectedGrow!.id;

      const [devices, buckets, pendingTasks, tentReadings, harvestCountdown] = await Promise.all([
        listDevices(token).catch(() => [] as DeviceResponse[]),
        listBuckets(token, growId).catch(() => [] as BucketResponse[]),
        listTasks(token, { status: "pending", grow_cycle_id: growId }).catch(() => [] as TaskItem[]),
        listTentReadings(token, tentId, 50).catch(() => [] as TentReadingResponse[]),
        getHarvestCountdown(token).catch(() => [] as HarvestCountdownItem[]),
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
        harvestCountdown,
      };
    },
  );

  const refresh = useCallback(async () => {
    await mutate();
  }, [mutate]);

  const devices = dashboardData?.devices ?? [];
  const tasks = dashboardData?.tasks ?? [];
  const sensorTrends = dashboardData?.sensorTrends ?? EMPTY_SENSOR_TRENDS;
  const climateData = dashboardData?.climateData ?? [];
  const healthScore = dashboardData?.healthScore ?? null;

  const handleCompleteTask = useCallback(async (taskId: string) => {
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
  }, [mutate]);

  const isHydro = isActiveHydro(selectedGrow?.grow_type);
  const hasSensorData = sensorTrends.ph.length > 0 || sensorTrends.ec.length > 0 || sensorTrends.ppm.length > 0;

  const metrics = useMemo(
    () => (selectedGrow ? buildDashboardMetrics({ trends: sensorTrends, isHydro, stage: selectedGrow.stage, tempUnit: prefs.temp_unit }) : []),
    [selectedGrow, sensorTrends, isHydro, prefs.temp_unit],
  );

  const heroGrow = useMemo<PreviewGrow | null>(() => {
    if (!selectedGrow) return null;
    const startedAt = new Date(selectedGrow.started_at).getTime();
    const dayInStage = Math.max(0, Math.floor((Date.now() - startedAt) / 86_400_000));
    const harvestItem = (dashboardData?.harvestCountdown ?? []).find((h) => h.grow_id === selectedGrow.id);
    const harvestInDays = harvestItem ? Math.max(0, harvestItem.days_remaining) : null;
    const cycleTotal = harvestInDays != null ? dayInStage + harvestInDays : 0;
    return {
      name: selectedGrow.name,
      strain: harvestItem?.strain_name ?? selectedGrow.grow_type.replace(/_/g, " "),
      stage: selectedGrow.stage,
      dayInStage,
      cycleDay: dayInStage,
      cycleTotal,
      harvestInDays,
      healthScore,
    };
  }, [selectedGrow, dashboardData?.harvestCountdown, healthScore]);

  const layout = mode === "beginner" || mode === "home" ? "command" : "bento";
  const viewProps: AdaptiveDashboardProps | null =
    selectedGrow && heroGrow
      ? {
          grow: heroGrow,
          metrics,
          climate: climateData,
          tasks,
          onCompleteTask: handleCompleteTask,
          growId: selectedGrow.id,
          growStage: selectedGrow.stage,
          tentId: selectedGrow.tent_id,
          hasSensorData,
          sensorTrends,
          healthScore,
          density: config.density,
        }
      : null;

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
          {viewProps &&
            (layout === "command" ? (
              <CommandCenterView {...viewProps} />
            ) : (
              <BentoView {...viewProps} />
            ))}



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
