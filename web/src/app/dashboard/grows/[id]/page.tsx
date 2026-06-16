"use client";

import { useCallback, useEffect, useState, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import { fireBurst } from "@/lib/confetti";
import { toast } from "sonner";
import {
  getGrow,
  updateGrow,
  createGrow,
  listBuckets,
  createBucket,
  getLatestReading,
  createSensorReading,
  createTentReading,
  getLatestTentReading,
  getTent,
  listJournalEntries,
  getExportUrl,
  getGrowExportUrl,
  getHealthCheckHistory,
  listDevices,
  listSensorReadings,
  listTentReadings,
  listTasks,
  type GrowResponse,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type TentResponse,
  type JournalEntryResponse,
  type DeviceResponse,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  CheckCircle,
  Droplets,
  Loader2,
  Pencil,
  Download,
  Copy,
  Settings,
  Thermometer,
  Heart,
  MessageSquare,
  Calendar,
  Sprout,
  FlaskConical,
  Waves,
  Activity,
  SunMedium,
  Timer,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { SensorSparkline } from "@/components/sparkline";
import { CameraGrid } from "@/components/camera-grid";
import { MultiMetricCard } from "@/components/multi-metric-card";
import { useChat } from "@/components/chat-provider";
import { useGrow } from "@/hooks/use-grow";

import { formatCalendarDate, formatDateTime } from "@/lib/utils";
import { BucketsTab } from "./buckets-tab";
import { TasksTab } from "./tasks-tab";
import { ActivityTab } from "./activity-tab";
import { NutritionYieldTab } from "./nutrition-yield-tab";
import { HealthPhotosTab } from "./health-photos-tab";
import { FieldTab } from "./field-tab";
import { WeatherCard } from "./weather-card";
import { isOutdoor, isActiveHydro, isSoil, t } from "@/lib/terminology";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, tempUnitLabel } from "@/lib/units";
import { getHumidityThreshold } from "@/lib/humidity-thresholds";

const STAGES = ["seedling", "vegetative", "flowering", "ripening", "drying", "curing"];
const STAGE_DURATIONS: Record<string, number> = { seedling: 14, vegetative: 30, flowering: 56, ripening: 14, drying: 10, curing: 21 };
const STAGE_ICONS: Record<string, typeof Sprout> = { seedling: Sprout, vegetative: SunMedium, flowering: Waves, ripening: Timer, drying: Activity, curing: FlaskConical };
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -8 } };
const stagger = { animate: { transition: { staggerChildren: 0.06 } } };
const MILESTONE_LABELS: Record<string, string> = {
  seedling: "Seedling / Germ",
  vegetative: "Veg Started",
  flowering: "Flower Started",
  ripening: "Ripening",
  drying: "Drying",
  curing: "Curing",
  harvest: "Harvest",
};

function ChatButton() {
  const { toggle } = useChat();
  return (
    <Button variant="outline" size="sm" onClick={toggle} className="gap-2">
      <MessageSquare className="size-4" />
      AI Chat
    </Button>
  );
}

export default function GrowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const confirm = useConfirm();
  const { prefs } = usePreferences();
  const { setSelectedGrowId } = useGrow();
  const [grow, setGrow] = useState<GrowResponse | null>(null);
  const [tent, setTent] = useState<TentResponse | null>(null);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, SensorReadingResponse | null>>({});

  const [journalEntries, setJournalEntries] = useState<JournalEntryResponse[]>([]);

  // Sensor reading dialog
  const [sensorDialog, setSensorDialog] = useState<{ open: boolean; bucketIds: string[]; bucketLabel: string }>({ open: false, bucketIds: [], bucketLabel: "" });
  const [sensorForm, setSensorForm] = useState({ ph: "", ec: "", ppm: "", water_temp_f: "", soil_moisture: "", soil_temp: "", runoff_ph: "", runoff_ec: "" });
  const [sensorSaving, setSensorSaving] = useState(false);

  // Tent ambient dialog
  const [ambientDialog, setAmbientDialog] = useState(false);
  const [ambientForm, setAmbientForm] = useState({ ambient_temp_f: "", ambient_humidity: "" });
  const [ambientSaving, setAmbientSaving] = useState(false);
  const [tentAmbient, setTentAmbient] = useState<TentReadingResponse | null>(null);

  // Sync sidebar grow selector with the current page
  useEffect(() => {
    if (id) setSelectedGrowId(id);
  }, [id, setSelectedGrowId]);

  // Edit grow dialog
  const [editGrowDialog, setEditGrowDialog] = useState(false);
  const [editGrowForm, setEditGrowForm] = useState({ name: "", notes: "", started_at: "", milestones: {} as Record<string, string> });
  const [editGrowSaving, setEditGrowSaving] = useState(false);



  // Clone dialog
  const [cloneDialog, setCloneDialog] = useState(false);
  const [cloneName, setCloneName] = useState("");
  const [cloneSaving, setCloneSaving] = useState(false);

  // Settings dialog
  const [settingsDialog, setSettingsDialog] = useState(false);
  const [settingsForm, setSettingsForm] = useState<Record<string, string>>({});
  const [settingsSaving, setSettingsSaving] = useState(false);

  // Health score
  const [healthScore, setHealthScore] = useState<number | null>(null);
  const [openTaskCount, setOpenTaskCount] = useState(0);

  // Sensor trends for overview sparklines
  const [sensorTrends, setSensorTrends] = useState<{ ph: number[]; ec: number[]; ppm: number[]; temp: number[]; humidity: number[]; water_temp: number[]; water_level: number[]; orp: number[] }>({ ph: [], ec: [], ppm: [], temp: [], humidity: [], water_temp: [], water_level: [], orp: [] });

  const [loadError, setLoadError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    let g: GrowResponse;
    let bkts: BucketResponse[];
    try {
      [g, bkts] = await Promise.all([
        getGrow(token, id),
        listBuckets(token, id),
      ]);
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Failed to load grow");
      return;
    }
    setLoadError(null);
    setGrow(g);
    setBuckets(bkts);

    try { setTent(await getTent(token, g.tent_id)); } catch { setTent(null); }

    try { setTentAmbient(await getLatestTentReading(token, g.tent_id)); } catch { setTentAmbient(null); }

    if (isOutdoor(g.grow_type)) {
      try { setDevices(await listDevices(token)); } catch { setDevices([]); }
    }

    const readings: Record<string, SensorReadingResponse | null> = {};
    await Promise.all(
      bkts.map(async (b) => {
        try { readings[b.id] = await getLatestReading(token, b.id); } catch { readings[b.id] = null; }
      }),
    );
    setLatestReadings(readings);


    try {
      const hist = await getHealthCheckHistory(token, id, 1);
      setHealthScore(hist.items.length > 0 ? hist.items[0].score : null);
    } catch { setHealthScore(null); }

    try {
      const tasks = await listTasks(token, { grow_cycle_id: id, status: "pending" });
      setOpenTaskCount(tasks.length);
    } catch { setOpenTaskCount(0); }

    // Fetch sensor trends for overview sparklines
    try {
      const [perBucketReadings, tentReadings2] = await Promise.all([
        Promise.all(bkts.map((b) => listSensorReadings(token, b.id, 30).catch(() => []))),
        listTentReadings(token, g.tent_id, 30).catch(() => []),
      ]);
      // For RDWC grows, use only the header bucket's readings for shared water
      // metrics to avoid double-counting propagated duplicates.
      const headerBkt = g.grow_type === "rdwc" ? bkts.find((b) => b.role === "header") : null;
      const headerIdx = headerBkt ? bkts.indexOf(headerBkt) : -1;
      const waterReadings = headerIdx >= 0
        ? [...perBucketReadings[headerIdx]].sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime())
        : perBucketReadings.flat().sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());
      const allGrowSensor = perBucketReadings
        .flat()
        .sort((a, b) => new Date(b.recorded_at).getTime() - new Date(a.recorded_at).getTime());
      // Build each metric independently so sparse metrics (like pH/water level)
      // are not dropped by a global mixed-metric slice.
      setSensorTrends({
        ph: waterReadings.map((r: { ph: number | null }) => r.ph).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        ec: waterReadings.map((r: { ec: number | null }) => r.ec).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        ppm: waterReadings.map((r: { ppm: number | null }) => r.ppm).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        water_temp: waterReadings.map((r: { water_temp_f: number | null }) => r.water_temp_f).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        water_level: waterReadings.map((r: { water_level_pct: number | null }) => r.water_level_pct).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        orp: waterReadings.map((r: { orp: number | null }) => r.orp).filter((v: number | null): v is number => v != null).slice(0, 30).reverse(),
        temp: (() => {
          const tentTemps = tentReadings2.map((r: { ambient_temp_f: number | null }) => r.ambient_temp_f).filter((v: number | null): v is number => v != null).reverse();
          if (tentTemps.length > 0) return tentTemps;
          return allGrowSensor.map((r: { ambient_temp_f: number | null }) => r.ambient_temp_f).filter((v: number | null): v is number => v != null).slice(0, 30).reverse();
        })(),
        humidity: (() => {
          const tentHumidity = tentReadings2.map((r: { ambient_humidity: number | null }) => r.ambient_humidity).filter((v: number | null): v is number => v != null).reverse();
          if (tentHumidity.length > 0) return tentHumidity;
          return allGrowSensor.map((r: { ambient_humidity: number | null }) => r.ambient_humidity).filter((v: number | null): v is number => v != null).slice(0, 30).reverse();
        })(),
      });
    } catch { /* empty */ }

    try {
      const allEntries: JournalEntryResponse[] = [];
      await Promise.all(bkts.map(async (b) => {
        try {
          const entries = await listJournalEntries(token, b.id);
          allEntries.push(...entries);
        } catch { /* empty */ }
      }));
      allEntries.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      setJournalEntries(allEntries);
    } catch { /* empty */ }
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  // Compute last water change date per bucket from journal entries.
  // For RDWC grows, a water change on the header applies to all site buckets
  // (they share the same reservoir).
  const bucketWaterStatus = useMemo(() => {
    const map: Record<string, { lastChange: Date; daysSince: number } | null> = {};
    const now = new Date();

    // Find the header bucket's most recent water_change for RDWC propagation
    let headerLastChange: Date | null = null;
    if (grow?.grow_type === "rdwc") {
      const headerBucket = buckets.find((b) => b.role === "header");
      if (headerBucket) {
        const headerEntries = journalEntries.filter(
          (e) => e.bucket_id === headerBucket.id && e.event_type === "water_change"
        );
        if (headerEntries.length > 0) {
          const latest = headerEntries.reduce((a, c) =>
            new Date(c.created_at) > new Date(a.created_at) ? c : a
          );
          headerLastChange = new Date(latest.created_at);
        }
      }
    }

    for (const b of buckets) {
      const entries = journalEntries.filter(
        (e) => e.bucket_id === b.id && e.event_type === "water_change"
      );
      let lastChange: Date | null = null;
      if (entries.length > 0) {
        const latest = entries.reduce((a, c) =>
          new Date(c.created_at) > new Date(a.created_at) ? c : a
        );
        lastChange = new Date(latest.created_at);
      }
      // RDWC: site buckets inherit the header's water change if more recent
      if (grow?.grow_type === "rdwc" && b.role !== "header" && headerLastChange) {
        if (!lastChange || headerLastChange > lastChange) {
          lastChange = headerLastChange;
        }
      }
      if (!lastChange) {
        map[b.id] = null;
        continue;
      }
      const daysSince = Math.floor((now.getTime() - lastChange.getTime()) / 86_400_000);
      map[b.id] = { lastChange, daysSince };
    }
    return map;
  }, [buckets, journalEntries, grow]);

  // Tab persistence — remember last active tab across grow switches
  const TAB_STORAGE_KEY = "tendril:grow-detail-tab";
  const settingsSchemaLength = useMemo(() => grow ? getSettingsSchema(grow.grow_type, tempUnitLabel(prefs.temp_unit)).length : 0, [grow, prefs.temp_unit]);
  const validTabs = useMemo(() => {
    const tabs = ["overview", "buckets", "activity", "tasks", "nutrition", "health-photos"];
    if (grow && isOutdoor(grow.grow_type)) tabs.push("field");
    if (settingsSchemaLength > 0) tabs.push("settings");
    return tabs;
  }, [grow, settingsSchemaLength]);

  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window === "undefined") return "overview";
    const stored = sessionStorage.getItem(TAB_STORAGE_KEY);
    return stored && validTabs.includes(stored) ? stored : "overview";
  });

  const handleTabChange = useCallback((value: string) => {
    setActiveTab(value);
    sessionStorage.setItem(TAB_STORAGE_KEY, value);
  }, []);

  // Reset to overview if stored tab is invalid for this grow type
  useEffect(() => {
    if (!validTabs.includes(activeTab)) {
      setActiveTab("overview");
    }
  }, [validTabs, activeTab]);

  // --- Handlers ---

  const handleComplete = async () => {
    if (!await confirm({ title: "Complete Grow", description: "Mark this grow as completed?", confirmLabel: "Complete" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateGrow(token, id, { status: "completed" });
      fireBurst();
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to complete grow");
    }
  };

  const handleSensorSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setSensorSaving(true);
    try {
      const base: Record<string, unknown> = {};
      if (sensorForm.ph) base.ph = parseFloat(sensorForm.ph);
      if (sensorForm.ec) base.ec = parseFloat(sensorForm.ec);
      if (sensorForm.ppm) base.ppm = parseFloat(sensorForm.ppm);
      if (sensorForm.water_temp_f) base.water_temp_f = parseFloat(sensorForm.water_temp_f);
      if (sensorForm.soil_moisture) base.soil_moisture = parseFloat(sensorForm.soil_moisture);
      if (sensorForm.soil_temp) base.soil_temp = parseFloat(sensorForm.soil_temp);
      if (sensorForm.runoff_ph) base.runoff_ph = parseFloat(sensorForm.runoff_ph);
      if (sensorForm.runoff_ec) base.runoff_ec = parseFloat(sensorForm.runoff_ec);
      await Promise.all(
        sensorDialog.bucketIds.map((id) =>
          createSensorReading(token, { ...base, bucket_id: id } as Parameters<typeof createSensorReading>[1])
        )
      );
      setSensorDialog({ open: false, bucketIds: [], bucketLabel: "" });
      setSensorForm({ ph: "", ec: "", ppm: "", water_temp_f: "", soil_moisture: "", soil_temp: "", runoff_ph: "", runoff_ec: "" });
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save reading"); } finally { setSensorSaving(false); }
  };

  const handleEditGrowSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setEditGrowSaving(true);
    try {
      const payload: Parameters<typeof updateGrow>[2] = {
        name: editGrowForm.name.trim() || undefined,
        notes: editGrowForm.notes.trim() || undefined,
      };
      if (editGrowForm.started_at) {
        payload.started_at = new Date(editGrowForm.started_at).toISOString();
      }
      const ms: Record<string, string> = {};
      for (const [k, v] of Object.entries(editGrowForm.milestones)) {
        if (v) ms[k] = new Date(v).toISOString();
      }
      if (Object.keys(ms).length) {
        payload.milestones = ms;
        // Auto-advance stage to the latest milestone that has a date set
        const allMilestones = { ...(grow?.milestones || {}), ...ms };
        let latestStage: string | undefined;
        for (const s of STAGES) {
          if (allMilestones[s]) latestStage = s;
        }
        if (latestStage) payload.stage = latestStage;
      }
      await updateGrow(token, id, payload);
      setEditGrowDialog(false);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save grow"); } finally { setEditGrowSaving(false); }
  };

  const handleExport = () => {
    const token = getAccessToken();
    if (!token || !grow) return;
    const url = getGrowExportUrl(token, grow.id);
    window.open(url, "_blank");
  };

  const handleCloneGrow = async () => {
    if (!grow || !cloneName.trim()) return;
    const token = getAccessToken();
    if (!token) return;
    setCloneSaving(true);
    try {
      // Create new grow with same settings
      const newGrow = await createGrow(token, {
        tent_id: grow.tent_id,
        name: cloneName.trim(),
        grow_type: grow.grow_type,
      });
      // Copy buckets (preserve role for RDWC header buckets)
      for (const b of buckets) {
        await createBucket(token, {
          grow_cycle_id: newGrow.id,
          label: b.label || undefined,
          strain_id: b.strain_id || undefined,
          strain_name: b.strain_name || undefined,
          position: b.position,
          volume_gallons: b.volume_gallons || undefined,
          role: b.role,
        });
      }
      // Copy settings (including nutrient brand selection)
      if (grow.settings && Object.keys(grow.settings).length > 0) {
        await updateGrow(token, newGrow.id, { settings: grow.settings });
      }
      setCloneDialog(false);
      setCloneName("");
      router.push(`/dashboard/grows/${newGrow.id}`);
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to clone grow"); } finally { setCloneSaving(false); }
  };

  const handleSettingsSave = async () => {
    const token = getAccessToken();
    if (!token || !grow) return;
    setSettingsSaving(true);
    try {
      const settings: Record<string, unknown> = { ...(grow.settings || {}) };
      for (const [k, v] of Object.entries(settingsForm)) {
        if (v.trim()) settings[k] = v.trim();
        else delete settings[k];
      }
      await updateGrow(token, id, { settings } as Parameters<typeof updateGrow>[2]);
      setSettingsDialog(false);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save settings"); } finally { setSettingsSaving(false); }
  };

  // --- Render ---

  if (loadError) {
    return (
      <>
        <PageHeader
          title="Error"
          breadcrumbs={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Grows", href: "/dashboard/grows" },
            { label: "Error" },
          ]}
        />
        <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8">
          <p className="text-sm text-destructive">{loadError}</p>
          <Button variant="outline" size="sm" onClick={refresh}>Retry</Button>
        </div>
      </>
    );
  }

  if (!grow) {
    return (
      <>
        <PageHeader
          title="Loading..."
          breadcrumbs={[
            { label: "Dashboard", href: "/dashboard" },
            { label: "Grows", href: "/dashboard/grows" },
            { label: "..." },
          ]}
        />
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          <Skeleton className="h-8 w-48" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        </div>
      </>
    );
  }

  const bucketLabelMap: Record<string, string> = {};
  buckets.forEach((b) => { bucketLabelMap[b.id] = `#${b.position} ${b.label || "Unnamed"}`; });

  // Grow type specific settings schema
  const settingsSchema = getSettingsSchema(grow.grow_type, tempUnitLabel(prefs.temp_unit));
  const latestEnvTemp = tentAmbient?.ambient_temp_f ?? (sensorTrends.temp.length > 0 ? sensorTrends.temp[sensorTrends.temp.length - 1] : null);
  const latestEnvHumidity = tentAmbient?.ambient_humidity ?? (sensorTrends.humidity.length > 0 ? sensorTrends.humidity[sensorTrends.humidity.length - 1] : null);

  return (
    <Tabs value={activeTab} onValueChange={handleTabChange} className="flex flex-1 flex-col">
      <PageHeader
        title={grow.name}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Grows", href: "/dashboard/grows" },
          { label: grow.name },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleExport} disabled={buckets.length === 0}>
              <Download className="mr-1 size-4" /> Export
            </Button>
            <Button variant="outline" size="sm" onClick={() => { setCloneName(`${grow.name} (Copy)`); setCloneDialog(true); }}>
              <Copy className="mr-1 size-4" /> Clone
            </Button>
            {grow.status === "active" && (
              <Button variant="outline" size="sm" onClick={handleComplete}>
                <CheckCircle className="mr-1 size-4" /> Complete
              </Button>
            )}
          </div>
        }
      />
      <div className="sticky top-0 z-10 border-b bg-background overflow-hidden">
        <div className="overflow-x-auto scrollbar-none touch-pan-x px-4 lg:px-6">
          <TabsList className="w-max">
            <TabsTrigger value="overview" className="text-xs sm:text-sm">Overview</TabsTrigger>
            <TabsTrigger value="buckets" className="text-xs sm:text-sm">{t(grow.grow_type, "Buckets")} ({buckets.length})</TabsTrigger>
            <TabsTrigger value="activity" className="text-xs sm:text-sm">Activity</TabsTrigger>
            <TabsTrigger value="tasks" className="text-xs sm:text-sm">Tasks{openTaskCount > 0 && <Badge variant="secondary" className="ml-1 h-4 min-w-4 px-1 text-[10px]">{openTaskCount}</Badge>}</TabsTrigger>
            <TabsTrigger value="nutrition" className="text-xs sm:text-sm">Nutrition & Yield</TabsTrigger>
            <TabsTrigger value="health-photos" className="text-xs sm:text-sm">Health & Photos{healthScore != null && healthScore < 50 && <span className="ml-1 inline-block size-2 rounded-full bg-destructive" />}</TabsTrigger>
            {isOutdoor(grow.grow_type) && <TabsTrigger value="field" className="text-xs sm:text-sm">Field</TabsTrigger>}
            {settingsSchema.length > 0 && <TabsTrigger value="settings" className="text-xs sm:text-sm">Settings</TabsTrigger>}
          </TabsList>
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <TabsContent value="overview" className="mt-0 flex flex-col gap-6">
        {/* ── Hero Header ─────────────────────────────────────────────── */}
        <motion.div {...fadeUp} className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-xl border bg-card p-5">
          <div className="flex items-center gap-4 min-w-0">
            {/* Health ring */}
            <div className={cn(
              "flex size-14 shrink-0 items-center justify-center rounded-full border-2",
              healthScore != null && healthScore >= 80 ? "border-emerald-500/60 bg-emerald-500/10" :
              healthScore != null && healthScore >= 50 ? "border-yellow-500/60 bg-yellow-500/10" :
              healthScore != null ? "border-destructive/60 bg-destructive/10" : "border-muted-foreground/20 bg-muted/30"
            )}>
              <Heart className={cn("size-6", healthScore != null && healthScore >= 80 ? "text-emerald-500" : healthScore != null && healthScore >= 50 ? "text-yellow-500" : healthScore != null ? "text-destructive" : "text-muted-foreground")} />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={grow.status === "active" ? "default" : "secondary"} className="text-xs capitalize">{grow.status}</Badge>
                <Badge variant="outline" className="text-xs capitalize gap-1">
                  {(() => { const Icon = STAGE_ICONS[grow.stage] || Sprout; return <Icon className="size-3" />; })()}
                  {grow.stage}
                </Badge>
                <span className="text-xs text-muted-foreground">{grow.grow_type.replace(/_/g, " ")}</span>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
                <span className="flex items-center gap-1"><Calendar className="size-3.5" /> {formatCalendarDate(grow.started_at)}</span>
                <span>{tent?.name || "No tent"}</span>
                <span>{buckets.length} {buckets.length === 1 ? "bucket" : "buckets"}</span>
                {healthScore != null && <span className="font-medium text-foreground">Score: {healthScore}</span>}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1 shrink-0">
            <ChatButton />
            {settingsSchema.length > 0 && (
              <Button variant="ghost" size="icon" className="size-8" onClick={() => {
                const form: Record<string, string> = {};
                for (const s of settingsSchema) form[s.key] = ((grow.settings as Record<string, unknown>)?.[s.key] as string) || "";
                setSettingsForm(form);
                setSettingsDialog(true);
              }}><Settings className="size-4" /></Button>
            )}
            <Button variant="ghost" size="icon" className="size-8" onClick={() => {
              const msForm: Record<string, string> = {};
              for (const key of [...STAGES, "harvest"]) {
                const iso = grow.milestones?.[key];
                msForm[key] = iso ? new Date(iso).toISOString().slice(0, 10) : "";
              }
              setEditGrowForm({
                name: grow.name,
                notes: grow.notes || "",
                started_at: new Date(grow.started_at).toISOString().slice(0, 10),
                milestones: msForm,
              });
              setEditGrowDialog(true);
            }}><Pencil className="size-4" /></Button>
          </div>
        </motion.div>

        {/* ── Stage Progress ──────────────────────────────────────────── */}
        <motion.div {...fadeUp} transition={{ delay: 0.06 }}>
          <Card>
            <CardContent className="pt-5 pb-4">
              <div className="mb-3 flex items-center justify-between text-sm">
                <span className="font-medium">Growth Timeline</span>
                <span className="text-xs text-muted-foreground">
                  Day {Math.floor((Date.now() - new Date(grow.started_at).getTime()) / 86400000)}
                </span>
              </div>
              <div className="flex items-center gap-1">
                {STAGES.map((stage) => {
                  const isCurrent = grow.stage === stage;
                  const isPast = STAGES.indexOf(grow.stage) > STAGES.indexOf(stage);
                  const msDate = grow.milestones?.[stage];
                  const Icon = STAGE_ICONS[stage] || Sprout;
                  let pct = 0;
                  if (isPast) pct = 100;
                  else if (isCurrent) {
                    const start = msDate ? new Date(msDate).getTime() : new Date(grow.started_at).getTime();
                    const elapsed = (Date.now() - start) / 86400000;
                    pct = Math.min(100, Math.max(5, (elapsed / (STAGE_DURATIONS[stage] || 30)) * 100));
                  }
                  return (
                    <div key={stage} className="flex-1 min-w-0">
                      <div className="flex items-center gap-1 mb-1.5">
                        <Icon className={cn("size-3 shrink-0", isCurrent ? "text-primary" : isPast ? "text-emerald-500" : "text-muted-foreground/40")} />
                        <span className={cn("text-[10px] truncate", isCurrent ? "font-semibold text-foreground" : isPast ? "text-muted-foreground" : "text-muted-foreground/50")}>
                          {MILESTONE_LABELS[stage]?.split(" ")[0] || stage}
                        </span>
                      </div>
                      <Progress value={pct} className={cn("h-1.5", isCurrent ? "[&>div]:bg-primary" : isPast ? "[&>div]:bg-emerald-500" : "")} />
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* ── Camera Feed ─────────────────────────────────────────────── */}
        <CameraGrid tentId={grow.tent_id} hideEmpty />

        {/* ── Environment + Sensor Trend Cards ────────────────────────── */}
        <motion.div variants={stagger} initial="initial" animate="animate" className={cn("grid gap-3 grid-cols-2", isActiveHydro(grow.grow_type) ? "lg:grid-cols-4" : "lg:grid-cols-4")}>
          {isActiveHydro(grow.grow_type) ? (
            <>
              {/* Environment — same as main dashboard */}
              <motion.div variants={fadeUp}>
                <MultiMetricCard
                  title="Environment"
                  icon={<Thermometer className="size-5" />}
                  metrics={[
                    {
                      label: "Tent Temp",
                      value: latestEnvTemp != null ? formatTemp(latestEnvTemp, "f", prefs.temp_unit, 0) : "—",
                      status: latestEnvTemp != null ? (latestEnvTemp >= 68 && latestEnvTemp <= 82 ? "optimal" : "warning") : "unknown",
                      hint: latestEnvTemp != null && latestEnvTemp < 68 ? "Too cold — target 68–82°F" : latestEnvTemp != null && latestEnvTemp > 82 ? "Too hot — target 68–82°F" : undefined,
                    },
                    {
                      label: "Humidity",
                      value: latestEnvHumidity != null ? `${latestEnvHumidity.toFixed(0)}%` : "—",
                      status: getHumidityThreshold(latestEnvHumidity, grow?.stage).status,
                      hint: getHumidityThreshold(latestEnvHumidity, grow?.stage).hint,
                    },
                    {
                      label: "Water Temp",
                      value: sensorTrends.water_temp.length > 0 ? formatTemp(sensorTrends.water_temp[sensorTrends.water_temp.length - 1], "f", prefs.temp_unit, 0) : "—",
                      status: sensorTrends.water_temp.length > 0 ? (sensorTrends.water_temp[sensorTrends.water_temp.length - 1] >= 62 && sensorTrends.water_temp[sensorTrends.water_temp.length - 1] <= 70 ? "optimal" : "warning") : "unknown",
                      hint: sensorTrends.water_temp.length > 0 && sensorTrends.water_temp[sensorTrends.water_temp.length - 1] < 62 ? "Too cold — target 64–70°F" : sensorTrends.water_temp.length > 0 && sensorTrends.water_temp[sensorTrends.water_temp.length - 1] > 70 ? "Too warm — root rot risk above 72°F. Target 64–70°F" : undefined,
                    },
                  ]}
                />
              </motion.div>

              {/* Nutrients — same as main dashboard */}
              <motion.div variants={fadeUp}>
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
                      value: sensorTrends.ppm.length > 0 ? `${Math.round(sensorTrends.ppm[sensorTrends.ppm.length - 1])}` : "—",
                      status: sensorTrends.ppm.length > 0 ? (sensorTrends.ppm[sensorTrends.ppm.length - 1] >= 400 && sensorTrends.ppm[sensorTrends.ppm.length - 1] <= 1500 ? "optimal" : "warning") : "unknown",
                      hint: sensorTrends.ppm.length > 0 && sensorTrends.ppm[sensorTrends.ppm.length - 1] < 400 ? "Nutrients too low — target 400–1500 PPM" : sensorTrends.ppm.length > 0 && sensorTrends.ppm[sensorTrends.ppm.length - 1] > 1500 ? "Nutrients too high — target 400–1500 PPM" : undefined,
                    },
                    ...(sensorTrends.orp.length > 0 ? [{
                      label: "ORP",
                      value: `${Math.round(sensorTrends.orp[sensorTrends.orp.length - 1])} mV`,
                      status: (sensorTrends.orp[sensorTrends.orp.length - 1] >= 300 && sensorTrends.orp[sensorTrends.orp.length - 1] <= 450 ? "optimal" : "warning") as "optimal" | "warning",
                      hint: sensorTrends.orp[sensorTrends.orp.length - 1] < 300 ? "ORP low — anaerobic risk. Target 300–450 mV" : sensorTrends.orp[sensorTrends.orp.length - 1] > 450 ? "ORP high — too oxidizing. Target 300–450 mV" : undefined,
                    }] : []),
                  ]}
                />
              </motion.div>

              {/* EC */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden border-border/50 backdrop-blur-sm">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center gap-2">
                      <div className="flex size-8 items-center justify-center rounded-lg bg-blue-500/10"><Droplets className="size-4 text-blue-500" /></div>
                      <div>
                        <p className="text-[11px] text-muted-foreground">EC</p>
                        <p className="text-lg font-semibold tabular-nums">
                          {sensorTrends.ec.length > 0 ? sensorTrends.ec[sensorTrends.ec.length - 1].toFixed(2) : "—"}
                        </p>
                      </div>
                    </div>
                    {sensorTrends.ec.length > 2 && (
                      <div className="mt-2 h-8"><SensorSparkline data={sensorTrends.ec} color="#3b82f6" /></div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              {/* CO₂ placeholder */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden border-border/50 backdrop-blur-sm">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center gap-2">
                      <div className="flex size-8 items-center justify-center rounded-lg bg-muted"><Activity className="size-4 text-muted-foreground" /></div>
                      <div>
                        <p className="text-[11px] text-muted-foreground">CO₂</p>
                        <p className="text-lg font-semibold tabular-nums text-muted-foreground">—</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </>
          ) : (
            <>
              {/* Temperature (ambient) */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-orange-500/10"><Thermometer className="size-4 text-orange-500" /></div>
                        <div>
                          <p className="text-[11px] text-muted-foreground">Temperature</p>
                          <p className="text-lg font-semibold tabular-nums">
                            {tentAmbient?.ambient_temp_f != null ? formatTemp(tentAmbient.ambient_temp_f, "f", prefs.temp_unit) : "—"}
                          </p>
                        </div>
                      </div>
                    </div>
                    {sensorTrends.temp.length > 2 && (
                      <div className="mt-2 h-8"><SensorSparkline data={sensorTrends.temp} color="#f97316" /></div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              {/* Humidity (ambient) */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-blue-500/10"><Droplets className="size-4 text-blue-500" /></div>
                        <div>
                          <p className="text-[11px] text-muted-foreground">Humidity</p>
                          <p className="text-lg font-semibold tabular-nums">
                            {tentAmbient?.ambient_humidity != null ? `${tentAmbient.ambient_humidity.toFixed(0)}%` : "—"}
                          </p>
                        </div>
                      </div>
                    </div>
                    {sensorTrends.humidity.length > 2 && (
                      <div className="mt-2 h-8"><SensorSparkline data={sensorTrends.humidity} color="#3b82f6" /></div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              {/* pH */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-emerald-500/10"><FlaskConical className="size-4 text-emerald-500" /></div>
                        <div>
                          <p className="text-[11px] text-muted-foreground">pH</p>
                          <p className="text-lg font-semibold tabular-nums">
                            {sensorTrends.ph.length > 0 ? sensorTrends.ph[sensorTrends.ph.length - 1].toFixed(1) : "—"}
                          </p>
                        </div>
                      </div>
                      {sensorTrends.ph.length >= 2 && (() => {
                        const delta = sensorTrends.ph[sensorTrends.ph.length - 1] - sensorTrends.ph[sensorTrends.ph.length - 2];
                        return <Badge variant="outline" className={cn("text-[10px] gap-0.5", delta > 0 ? "text-emerald-500" : delta < 0 ? "text-orange-500" : "")}><TrendingUp className="size-2.5" />{delta >= 0 ? "+" : ""}{delta.toFixed(1)}</Badge>;
                      })()}
                    </div>
                    {sensorTrends.ph.length > 2 && (
                      <div className="mt-2 h-8"><SensorSparkline data={sensorTrends.ph} color="#10b981" /></div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>

              {/* EC */}
              <motion.div variants={fadeUp}>
                <Card className="relative overflow-hidden">
                  <CardContent className="pt-4 pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="flex size-8 items-center justify-center rounded-lg bg-violet-500/10"><Waves className="size-4 text-violet-500" /></div>
                        <div>
                          <p className="text-[11px] text-muted-foreground">EC</p>
                          <p className="text-lg font-semibold tabular-nums">
                            {sensorTrends.ec.length > 0 ? sensorTrends.ec[sensorTrends.ec.length - 1].toFixed(2) : "—"}
                          </p>
                        </div>
                      </div>
                      {sensorTrends.ec.length >= 2 && (() => {
                        const delta = sensorTrends.ec[sensorTrends.ec.length - 1] - sensorTrends.ec[sensorTrends.ec.length - 2];
                        return <Badge variant="outline" className={cn("text-[10px] gap-0.5", delta > 0 ? "text-emerald-500" : delta < 0 ? "text-orange-500" : "")}><TrendingUp className="size-2.5" />{delta >= 0 ? "+" : ""}{delta.toFixed(2)}</Badge>;
                      })()}
                    </div>
                    {sensorTrends.ec.length > 2 && (
                      <div className="mt-2 h-8"><SensorSparkline data={sensorTrends.ec} color="#8b5cf6" /></div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            </>
          )}
        </motion.div>

        {/* ── Quick Actions Row ───────────────────────────────────────── */}
        <motion.div {...fadeUp} transition={{ delay: 0.18 }} className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" className="gap-1.5" onClick={() => {
            setAmbientForm({ ambient_temp_f: "", ambient_humidity: "" });
            setAmbientDialog(true);
          }}>
            <Thermometer className="size-3.5" /> Log Ambient
          </Button>
          {buckets.length > 0 && (
            <Button variant="outline" size="sm" className="gap-1.5" onClick={() => {
              setSensorForm({ ph: "", ec: "", ppm: "", water_temp_f: "", soil_moisture: "", soil_temp: "", runoff_ph: "", runoff_ec: "" });
              setSensorDialog({ open: true, bucketIds: buckets.map((b) => b.id), bucketLabel: `All Buckets (${buckets.length})` });
            }}>
              <Droplets className="size-3.5" /> Log Reading
            </Button>
          )}
        </motion.div>

        {/* ── Bucket Water Change Status ──────────────────────────────── */}
        {buckets.length > 0 && !isOutdoor(grow.grow_type) && (
          <motion.div {...fadeUp} transition={{ delay: 0.22 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm font-medium">
                  <RefreshCw className="size-4" /> Water Change Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {buckets.map((b) => {
                    const status = bucketWaterStatus[b.id];
                    const label = bucketLabelMap[b.id] || "Unnamed";
                    let color = "text-muted-foreground";
                    if (status) {
                      if (status.daysSince <= 7) color = "text-green-600 dark:text-green-400";
                      else if (status.daysSince <= 10) color = "text-yellow-600 dark:text-yellow-400";
                      else color = "text-red-600 dark:text-red-400";
                    }
                    return (
                      <div key={b.id} className="flex items-center justify-between text-sm">
                        <span className="truncate">{label}</span>
                        <span className={cn("text-xs font-medium", color)}>
                          {status
                            ? status.daysSince === 0
                              ? "Today"
                              : `${status.daysSince}d ago`
                            : "Never"}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* ── Bucket Quick View ───────────────────────────────────────── */}
        {buckets.length > 0 && (
          <motion.div {...fadeUp} transition={{ delay: 0.24 }}>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm font-medium">
                  <Sprout className="size-4" /> Plants
                  <Badge variant="secondary" className="ml-auto text-xs">{buckets.length}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <AnimatePresence>
                  <motion.div variants={stagger} initial="initial" animate="animate" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {buckets.map((b) => {
                      const r = latestReadings[b.id];
                      return (
                        <motion.div key={b.id} variants={fadeUp} className="rounded-lg border p-3 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sm truncate">
                              #{b.position} {b.label || b.strain_name || "Unnamed"}
                            </span>
                            <Badge variant="outline" className="text-[10px] capitalize">{b.growth_stage || grow.stage}</Badge>
                          </div>
                          {r ? (
                            <div className="flex items-center gap-3 text-xs text-muted-foreground">
                              {isSoil(grow.grow_type) ? (
                                <>
                                  {r.soil_moisture != null && <span>Moisture <strong className="text-foreground">{Math.round(r.soil_moisture)}%</strong></span>}
                                  {r.soil_temp != null && <span>Soil {formatTemp(r.soil_temp, "f", prefs.temp_unit, 0)}</span>}
                                  {r.runoff_ph != null && <span>Runoff pH <strong className="text-foreground">{r.runoff_ph.toFixed(1)}</strong></span>}
                                  {r.runoff_ec != null && <span>Runoff EC <strong className="text-foreground">{r.runoff_ec.toFixed(2)}</strong></span>}
                                </>
                              ) : (
                                <>
                                  {r.ph != null && <span>pH <strong className="text-foreground">{r.ph.toFixed(1)}</strong></span>}
                                  {r.ec != null && <span>EC <strong className="text-foreground">{r.ec.toFixed(2)}</strong></span>}
                                  {r.ppm != null && <span>PPM <strong className="text-foreground">{Math.round(r.ppm)}</strong></span>}
                                  {r.water_temp_f != null && <span>{formatTemp(r.water_temp_f, "f", prefs.temp_unit, 0)}</span>}
                                </>
                              )}
                            </div>
                          ) : (
                            <p className="text-xs text-muted-foreground/60">No readings yet</p>
                          )}
                        </motion.div>
                      );
                    })}
                  </motion.div>
                </AnimatePresence>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Weather (for outdoor/greenhouse tents) */}
        {tent && <WeatherCard tentId={tent.id} tentName={tent.name} environmentType={tent.environment_type} />}
        </TabsContent>

          <TabsContent value="buckets" className="mt-0">
            <BucketsTab
              growId={id}
              growType={grow.grow_type}
              buckets={buckets}
              latestReadings={latestReadings}
              onRefresh={refresh}
              onOpenSensorDialog={(bucketId, label) => {
                setSensorForm({ ph: "", ec: "", ppm: "", water_temp_f: "", soil_moisture: "", soil_temp: "", runoff_ph: "", runoff_ec: "" });
                setSensorDialog({ open: true, bucketIds: [bucketId], bucketLabel: label });
              }}
            />
          </TabsContent>

          <TabsContent value="activity" className="mt-0">
            <ActivityTab
              growId={grow.id}
              growType={grow.grow_type}
              buckets={buckets}
              journalEntries={journalEntries}
              bucketLabelMap={bucketLabelMap}
              onRefresh={refresh}
            />
          </TabsContent>

          <TabsContent value="tasks" className="mt-0">
            <TasksTab growId={id} />
          </TabsContent>

          <TabsContent value="nutrition" className="mt-0">
            <NutritionYieldTab
              growId={id}
              growStage={grow.stage}
              growStartedAt={grow.started_at}
              milestones={grow.milestones || {}}
              settings={grow.settings || {}}
              buckets={buckets}
              onRefresh={refresh}
            />
          </TabsContent>

          <TabsContent value="health-photos" className="mt-0">
            <HealthPhotosTab grow={grow} growId={id} buckets={buckets} onRefresh={refresh} />
          </TabsContent>

          {isOutdoor(grow.grow_type) && (
            <TabsContent value="field" className="mt-0">
              <FieldTab
                growId={id}
                growType={grow.grow_type}
                tentId={grow.tent_id}
                buckets={buckets}
                devices={devices}
                growStartDate={grow.started_at}
                onRefresh={refresh}
              />
            </TabsContent>
          )}

          {settingsSchema.length > 0 && (
            <TabsContent value="settings" className="mt-0">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-sm font-medium">
                      <Settings className="size-4" /> Grow Settings
                    </CardTitle>
                    <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => {
                      const form: Record<string, string> = {};
                      for (const s of settingsSchema) form[s.key] = ((grow.settings as Record<string, unknown>)?.[s.key] as string) || "";
                      setSettingsForm(form);
                      setSettingsDialog(true);
                    }}>
                      <Pencil className="mr-1 size-3" /> Edit Settings
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {grow.settings && Object.keys(grow.settings).length > 0 ? (
                    <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-3 text-sm">
                      {settingsSchema.map((s) => {
                        const val = (grow.settings as Record<string, unknown>)?.[s.key];
                        if (!val) return null;
                        return (
                          <div key={s.key}>
                            <span className="text-muted-foreground">{s.label}</span>
                            <p className="font-medium">{String(val)}{s.unit ? ` ${s.unit}` : ""}</p>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No settings configured yet. Click Edit Settings to add your grow-type-specific configuration.</p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          )}
      </div>

      {/* --- SENSOR READING DIALOG --- */}
      <Dialog open={sensorDialog.open} onOpenChange={(open) => !open && setSensorDialog({ open: false, bucketIds: [], bucketLabel: "" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Log Sensor Reading</DialogTitle>
            <DialogDescription>Record current readings for {sensorDialog.bucketLabel}</DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">{isSoil(grow.grow_type) ? "Runoff pH" : "pH"}</Label>
              <Input type="number" step="0.1" placeholder="e.g. 5.8" value={isSoil(grow.grow_type) ? sensorForm.runoff_ph : sensorForm.ph} onChange={(e) => setSensorForm((p) => ({ ...p, [isSoil(grow.grow_type) ? "runoff_ph" : "ph"]: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">{isSoil(grow.grow_type) ? "Runoff EC (mS/cm)" : "EC (mS/cm)"}</Label>
              <Input type="number" step="0.01" placeholder="e.g. 1.20" value={isSoil(grow.grow_type) ? sensorForm.runoff_ec : sensorForm.ec} onChange={(e) => setSensorForm((p) => ({ ...p, [isSoil(grow.grow_type) ? "runoff_ec" : "ec"]: e.target.value }))} />
            </div>
            {!isSoil(grow.grow_type) && (
              <div className="space-y-1">
                <Label className="text-xs">PPM</Label>
                <Input type="number" step="1" placeholder="e.g. 850" value={sensorForm.ppm} onChange={(e) => setSensorForm((p) => ({ ...p, ppm: e.target.value }))} />
              </div>
            )}
            {isSoil(grow.grow_type) ? (
              <>
                <div className="space-y-1">
                  <Label className="text-xs">Soil Moisture (%)</Label>
                  <Input type="number" step="1" placeholder="e.g. 45" value={sensorForm.soil_moisture} onChange={(e) => setSensorForm((p) => ({ ...p, soil_moisture: e.target.value }))} />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Soil Temp {tempUnitLabel(prefs.temp_unit)}</Label>
                  <Input type="number" step="0.1" placeholder="e.g. 72.0" value={sensorForm.soil_temp} onChange={(e) => setSensorForm((p) => ({ ...p, soil_temp: e.target.value }))} />
                </div>
              </>
            ) : (
              <div className="space-y-1">
                <Label className="text-xs">Water Temp {tempUnitLabel(prefs.temp_unit)}</Label>
                <Input type="number" step="0.1" placeholder="e.g. 68.0" value={sensorForm.water_temp_f} onChange={(e) => setSensorForm((p) => ({ ...p, water_temp_f: e.target.value }))} />
              </div>
            )}
          </div>
          <p className="text-xs text-muted-foreground">Ambient temp & humidity are logged at the tent level. <button type="button" className="underline" onClick={() => { setSensorDialog({ open: false, bucketIds: [], bucketLabel: "" }); setAmbientDialog(true); }}>Log ambient reading →</button></p>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setSensorDialog({ open: false, bucketIds: [], bucketLabel: "" })}>Cancel</Button>
            <Button type="button" onClick={handleSensorSubmit} disabled={sensorSaving}>
              {sensorSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save Reading
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* --- TENT AMBIENT DIALOG --- */}
      <Dialog open={ambientDialog} onOpenChange={(open) => !open && setAmbientDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Log Tent Ambient</DialogTitle>
            <DialogDescription>Record ambient temp & humidity for the whole tent{tent ? ` (${tent.name})` : ""}</DialogDescription>
          </DialogHeader>
          {tentAmbient && (
            <div className="rounded-md border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
              Last reading: {tentAmbient.ambient_temp_f != null && formatTemp(tentAmbient.ambient_temp_f, "f", prefs.temp_unit)} {tentAmbient.ambient_humidity != null && `${tentAmbient.ambient_humidity.toFixed(0)}%`} — {formatDateTime(tentAmbient.recorded_at)}
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Ambient Temp {tempUnitLabel(prefs.temp_unit)}</Label>
              <Input type="number" step="0.1" placeholder="e.g. 78.0" value={ambientForm.ambient_temp_f} onChange={(e) => setAmbientForm((p) => ({ ...p, ambient_temp_f: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Humidity %</Label>
              <Input type="number" step="1" placeholder="e.g. 55" value={ambientForm.ambient_humidity} onChange={(e) => setAmbientForm((p) => ({ ...p, ambient_humidity: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setAmbientDialog(false)}>Cancel</Button>
            <Button type="button" disabled={ambientSaving} onClick={async () => {
              const token = getAccessToken();
              if (!token || !grow) return;
              setAmbientSaving(true);
              try {
                const data: { tent_id: string; ambient_temp_f?: number; ambient_humidity?: number } = { tent_id: grow.tent_id };
                if (ambientForm.ambient_temp_f) data.ambient_temp_f = parseFloat(ambientForm.ambient_temp_f);
                if (ambientForm.ambient_humidity) data.ambient_humidity = parseFloat(ambientForm.ambient_humidity);
                await createTentReading(token, data);
                setAmbientDialog(false);
                setAmbientForm({ ambient_temp_f: "", ambient_humidity: "" });
                refresh();
              } catch { /* empty */ } finally { setAmbientSaving(false); }
            }}>
              {ambientSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* --- EDIT GROW DIALOG --- */}
      <Dialog open={editGrowDialog} onOpenChange={(open) => !open && setEditGrowDialog(false)}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Grow</DialogTitle>
            <DialogDescription>Update grow details, dates, and milestones</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Name</Label>
              <Input value={editGrowForm.name} onChange={(e) => setEditGrowForm((p) => ({ ...p, name: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Start Date</Label>
              <Input type="date" value={editGrowForm.started_at} onChange={(e) => setEditGrowForm((p) => ({ ...p, started_at: e.target.value }))} />
            </div>
            <div className="border-t pt-3">
              <Label className="text-xs font-medium">Milestone Dates</Label>
              <div className="mt-2 grid gap-3 sm:grid-cols-2">
                {[...STAGES, "harvest"].map((key) => (
                  <div key={key} className="space-y-1">
                    <Label className="text-xs text-muted-foreground">{MILESTONE_LABELS[key] || key}</Label>
                    <Input type="date" value={editGrowForm.milestones[key] || ""} onChange={(e) => setEditGrowForm((p) => ({ ...p, milestones: { ...p.milestones, [key]: e.target.value } }))} />
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Textarea rows={3} value={editGrowForm.notes} onChange={(e) => setEditGrowForm((p) => ({ ...p, notes: e.target.value }))} placeholder="General notes about this grow..." />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setEditGrowDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleEditGrowSubmit} disabled={editGrowSaving || !editGrowForm.name.trim()}>
              {editGrowSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* --- CLONE DIALOG --- */}
      <Dialog open={cloneDialog} onOpenChange={(open) => !open && setCloneDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clone Grow</DialogTitle>
            <DialogDescription>Create a copy of this grow with all buckets and feeding schedules</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">New Grow Name</Label>
              <Input value={cloneName} onChange={(e) => setCloneName(e.target.value)} placeholder="e.g. Summer Run 2" />
            </div>
            <div className="rounded-md border bg-muted/30 p-3 text-xs text-muted-foreground">
              <p className="font-medium text-foreground mb-1">Will copy:</p>
              <ul className="space-y-0.5 list-disc list-inside">
                <li>Grow type: {grow.grow_type}</li>
                <li>{buckets.length} bucket(s) with strain & volume</li>
                <li>Grow settings (nutrient brand, etc.)</li>
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setCloneDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleCloneGrow} disabled={cloneSaving || !cloneName.trim()}>
              {cloneSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Clone Grow
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* --- SETTINGS SHEET --- */}
      <Sheet open={settingsDialog} onOpenChange={(open) => !open && setSettingsDialog(false)}>
        <SheetContent side="right" className="sm:max-w-lg w-full flex flex-col">
          <SheetHeader>
            <SheetTitle>Grow Settings</SheetTitle>
            <SheetDescription>Configuration specific to {grow.grow_type} grows</SheetDescription>
          </SheetHeader>
          <div className="flex-1 overflow-y-auto -mx-6 px-6 space-y-6">
            {settingsSchema.length === 0 ? (
              <p className="text-sm text-muted-foreground py-8 text-center">No configurable settings for this grow type</p>
            ) : (
              (() => {
                const groups = new Map<string, SettingsField[]>();
                for (const s of settingsSchema) {
                  const g = s.group || "setup";
                  if (!groups.has(g)) groups.set(g, []);
                  groups.get(g)!.push(s);
                }
                const ordered = [...groups.entries()].sort(
                  ([a], [b]) => (GROUP_ORDER.indexOf(a) === -1 ? 99 : GROUP_ORDER.indexOf(a)) - (GROUP_ORDER.indexOf(b) === -1 ? 99 : GROUP_ORDER.indexOf(b)),
                );
                return ordered.map(([groupKey, fields]) => (
                  <div key={groupKey}>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">{GROUP_LABELS[groupKey] || groupKey}</h4>
                    <div className="grid gap-3 sm:grid-cols-2">
                      {fields.map((s) => (
                        <div key={s.key} className="space-y-1">
                          <Label className="text-xs">{s.label}{s.unit ? ` (${s.unit})` : ""}</Label>
                          {s.options ? (
                            <Select value={settingsForm[s.key] || ""} onValueChange={(v) => setSettingsForm((p) => ({ ...p, [s.key]: v ?? "" }))}>
                              <SelectTrigger><SelectValue placeholder={`Select ${s.label.toLowerCase()}`} /></SelectTrigger>
                              <SelectContent>
                                {s.options.map((o) => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                              </SelectContent>
                            </Select>
                          ) : (
                            <Input
                              type={s.type || "text"}
                              step={s.step}
                              placeholder={s.placeholder}
                              value={settingsForm[s.key] || ""}
                              onChange={(e) => setSettingsForm((p) => ({ ...p, [s.key]: e.target.value }))}
                            />
                          )}
                          {s.hint && <p className="text-[11px] text-muted-foreground leading-tight">{s.hint}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                ));
              })()
            )}
          </div>
          <SheetFooter className="border-t pt-4 gap-2 sm:gap-2">
            <Button variant="outline" type="button" onClick={() => setSettingsDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleSettingsSave} disabled={settingsSaving}>
              {settingsSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save Settings
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>

    </Tabs>
  );
}

// --- Grow type-specific settings schemas ---
interface SettingsField {
  key: string;
  label: string;
  type?: string;
  step?: string;
  unit?: string;
  placeholder?: string;
  hint?: string;
  options?: string[];
  group?: string;
}

const GROUP_ORDER = ["setup", "nutrients", "lighting", "environment", "outdoor"];
const GROUP_LABELS: Record<string, string> = {
  setup: "Setup & Targets",
  nutrients: "Nutrients & Water",
  lighting: "Lighting",
  environment: "Environment",
  outdoor: "Outdoor & Protection",
};

function getSettingsSchema(growType: string, tempUnit = "°F"): SettingsField[] {
  // Common indoor light fields (hardware lives on Tent equipment; these are per-grow-cycle)
  const LIGHT_FIELDS: SettingsField[] = [
    { key: "light_schedule", label: "Light Schedule", group: "lighting", placeholder: "e.g. 18/6, 12/12", hint: "Hours on / hours off" },
    { key: "light_height_in", label: "Light Height", group: "lighting", type: "number", unit: "in", placeholder: "e.g. 24" },
  ];
  // Common environment fields
  const ENV_FIELDS: SettingsField[] = [
    { key: "target_vpd", label: "Target VPD", group: "environment", type: "number", step: "0.1", unit: "kPa", placeholder: "e.g. 1.2", hint: "Vapor Pressure Deficit target" },
    { key: "target_temp_day_f", label: "Day Temp Target", group: "environment", type: "number", step: "1", unit: tempUnit, placeholder: "e.g. 80" },
    { key: "target_temp_night_f", label: "Night Temp Target", group: "environment", type: "number", step: "1", unit: tempUnit, placeholder: "e.g. 70" },
    { key: "target_humidity_pct", label: "Target Humidity", group: "environment", type: "number", step: "1", unit: "%", placeholder: "e.g. 55" },
    { key: "co2_ppm", label: "CO₂ Target", group: "environment", type: "number", step: "50", unit: "ppm", placeholder: "e.g. 1000", hint: "Only if supplementing CO₂" },
  ];
  // Common nutrient fields
  const NUTRIENT_FIELDS: SettingsField[] = [
    { key: "nutrient_line", label: "Nutrient Brand / Line", group: "nutrients", placeholder: "e.g. General Hydroponics Flora Series, Jack's 321, Athena Pro" },
    { key: "ph_up_product", label: "pH Up Product", group: "nutrients", placeholder: "e.g. General Hydroponics pH Up" },
    { key: "ph_down_product", label: "pH Down Product", group: "nutrients", placeholder: "e.g. General Hydroponics pH Down" },
    { key: "water_source", label: "Water Source", group: "nutrients", options: ["tap", "RO", "distilled", "well", "rain", "spring"], hint: "Source water type" },
    { key: "water_source_ppm", label: "Source Water PPM", group: "nutrients", type: "number", placeholder: "e.g. 150", hint: "Baseline PPM of your tap/source water" },
  ];

  switch (growType) {
    case "dwc":
    case "deep_water_culture":
      return [
        { key: "reservoir_liters", label: "Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 20" },
        { key: "bucket_type", label: "Bucket Type", options: ["5gal_bucket", "10gal_bucket", "tote", "custom"], hint: "Container style" },
        { key: "air_stones", label: "Air Stone Type", options: ["disc", "cylinder", "flexible", "none"], hint: "Type of air diffuser" },
        { key: "water_change_days", label: "Reservoir Change Interval", type: "number", unit: "days", placeholder: "e.g. 7" },
        { key: "top_feed", label: "Top Feed During Seedling?", options: ["yes", "no"], hint: "Drip ring for early root establishment" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.2" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "rdwc":
      return [
        { key: "reservoir_liters", label: "Central Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 60" },
        { key: "connected_sites", label: "Number of Connected Sites", type: "number", placeholder: "e.g. 4" },
        { key: "return_line_size", label: "Return Line Size", placeholder: "e.g. 2 inch, 3 inch" },
        { key: "water_change_days", label: "Reservoir Change Interval", type: "number", unit: "days", placeholder: "e.g. 7" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.2" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "nft":
    case "nutrient_film":
      return [
        { key: "channel_count", label: "Channel Count", type: "number", placeholder: "e.g. 4" },
        { key: "channel_length", label: "Channel Length", type: "number", unit: "ft", placeholder: "e.g. 4" },
        { key: "flow_rate_lph", label: "Flow Rate", type: "number", unit: "L/hr", placeholder: "e.g. 2" },
        { key: "reservoir_liters", label: "Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 40" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.4" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "ebb_flow":
    case "ebb_and_flow":
      return [
        { key: "tray_size", label: "Tray Size", placeholder: "e.g. 4x4, 3x3" },
        { key: "flood_interval_min", label: "Flood Interval", type: "number", unit: "min", placeholder: "e.g. 60" },
        { key: "flood_duration_min", label: "Flood Duration", type: "number", unit: "min", placeholder: "e.g. 15" },
        { key: "media_type", label: "Media Type", options: ["hydroton", "perlite", "rockwool", "growstones", "other"] },
        { key: "reservoir_liters", label: "Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 30" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.4" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "drip":
      return [
        { key: "emitter_count", label: "Emitter Count", type: "number", placeholder: "e.g. 12" },
        { key: "drip_frequency", label: "Drip Frequency", options: ["1x_daily", "2x_daily", "3x_daily", "4x_daily", "6x_daily", "continuous"] },
        { key: "drip_duration_sec", label: "Drip Duration", type: "number", unit: "sec", placeholder: "e.g. 120" },
        { key: "media_type", label: "Growing Media", options: ["coco", "rockwool", "perlite", "clay_pebbles", "other"] },
        { key: "recirculating", label: "Recirculating?", options: ["yes", "no_drain_to_waste"], hint: "Do you recollect runoff?" },
        { key: "reservoir_liters", label: "Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 30" },
        { key: "target_runoff_pct", label: "Target Runoff %", type: "number", unit: "%", placeholder: "e.g. 20" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.4" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "aeroponics":
      return [
        { key: "spray_interval_sec", label: "Spray Interval", type: "number", unit: "sec", placeholder: "e.g. 5" },
        { key: "spray_duration_sec", label: "Spray Duration", type: "number", unit: "sec", placeholder: "e.g. 3" },
        { key: "nozzle_psi", label: "Nozzle Pressure", type: "number", unit: "PSI", placeholder: "e.g. 80" },
        { key: "nozzle_count", label: "Nozzle Count", type: "number", placeholder: "e.g. 8" },
        { key: "reservoir_liters", label: "Reservoir Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 20" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 0.8" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "kratky":
      return [
        { key: "container_type", label: "Container Type", options: ["mason_jar", "5gal_bucket", "tote", "custom"], hint: "What holds your solution" },
        { key: "container_size_liters", label: "Container Size", type: "number", step: "0.5", unit: "L", placeholder: "e.g. 19" },
        { key: "light_proof", label: "Container Light-Proof?", options: ["yes", "no_needs_wrapping"], hint: "Light causes algae" },
        { key: "refill_strategy", label: "Refill Strategy", options: ["never", "only_when_critical", "partial_topoff"], hint: "Never refill to top — air gap is critical" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 6.0" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "coco":
    case "coco_coir":
      return [
        { key: "coco_brand", label: "Coco Brand", placeholder: "e.g. Canna Coco Professional Plus" },
        { key: "pot_type", label: "Pot Type", options: ["plastic", "fabric_cloth", "air_pot", "autopot", "custom"], hint: "Fabric pots promote air pruning" },
        { key: "pot_size_gal", label: "Pot Size", type: "number", step: "0.5", unit: "gal", placeholder: "e.g. 3" },
        { key: "perlite_ratio", label: "Perlite Mix Ratio", placeholder: "e.g. 70/30 coco/perlite", hint: "Higher perlite = more drainage" },
        { key: "watering_method", label: "Watering Method", options: ["hand_water_top", "hand_water_bottom", "drip_system", "autopot_bottom", "flood_table"], hint: "How you deliver water/nutrients" },
        { key: "fertigation_frequency", label: "Fertigation Frequency", options: ["1x_daily", "2x_daily", "3x_daily", "4x_daily", "6x_daily", "as_needed"] },
        { key: "runoff_target_pct", label: "Runoff Target", type: "number", unit: "%", placeholder: "e.g. 20" },
        { key: "calmag_brand", label: "CalMag Product", placeholder: "e.g. Botanicare Cal-Mag Plus", hint: "CalMag is essential in coco" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8", hint: "Coco optimal range: 5.8–6.3" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.4" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "rockwool":
      return [
        { key: "slab_size", label: "Slab / Cube Size", placeholder: "e.g. 6x36 slab, 4 inch cube" },
        { key: "shots_per_day", label: "Irrigation Shots per Day", type: "number", placeholder: "e.g. 6" },
        { key: "shot_volume_ml", label: "Shot Volume", type: "number", unit: "ml", placeholder: "e.g. 100" },
        { key: "target_dryback_pct", label: "Target Dry-back %", type: "number", unit: "%", placeholder: "e.g. 10-15", hint: "Generative vs vegetative steering" },
        { key: "slab_covered", label: "Slab Covered?", options: ["yes", "no_exposed"], hint: "Cover exposed rockwool to prevent algae" },
        { key: "scale_for_weight", label: "Using Scale for Weight Tracking?", options: ["yes", "no"], hint: "Precise dry-back monitoring" },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.5", hint: "Rockwool optimal range: 5.5–6.0" },
        { key: "target_ec", label: "Target EC", type: "number", step: "0.1", unit: "mS/cm", placeholder: "e.g. 1.6" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "soil":
    case "living_soil":
      return [
        { key: "soil_mix", label: "Soil Mix / Brand", placeholder: "e.g. Fox Farm Ocean Forest, BuildASoil 3.0" },
        { key: "organic_or_synthetic", label: "Nutrient Approach", options: ["organic_amendments", "synthetic_liquid", "hybrid", "living_soil_no_feed"], hint: "How you feed your plants" },
        { key: "pot_type", label: "Pot Type", options: ["plastic", "fabric_cloth", "air_pot", "raised_bed", "no_till_bed", "custom"], hint: "Fabric pots air-prune roots" },
        { key: "pot_size_gal", label: "Pot Size", type: "number", step: "0.5", unit: "gal", placeholder: "e.g. 5" },
        { key: "watering_method", label: "Watering Method", options: ["hand_water_top", "hand_water_bottom", "drip_system", "wick_bottom", "blumat_carrots"], hint: "Top water vs bottom water changes nutrient distribution" },
        { key: "amendments", label: "Amendments Used", placeholder: "e.g. Perlite 30%, Worm castings, Bat guano" },
        { key: "beneficial_microbes", label: "Beneficial Microbes", placeholder: "e.g. Mycorrhizae, Recharge, Mammoth P", hint: "Beneficial bacteria and fungi" },
        { key: "compost_tea", label: "Compost Tea?", options: ["yes_regular", "occasionally", "no"] },
        { key: "mulch_cover", label: "Mulch / Cover Crop", placeholder: "e.g. Straw mulch, Clover cover crop", hint: "Protects soil biology and moisture" },
        { key: "watering_schedule", label: "Watering Schedule", options: ["daily", "every_2_days", "every_3_days", "when_pot_is_light", "moisture_meter"] },
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 6.5", hint: "Soil optimal range: 6.0–6.8" },
        ...NUTRIENT_FIELDS,
        ...LIGHT_FIELDS,
        ...ENV_FIELDS,
      ];
    case "outdoor_soil":
      return [
        { key: "plot_type", label: "Plot Type", options: ["raised_bed", "in_ground", "guerrilla", "greenhouse"], hint: "Growing location type" },
        { key: "plot_size_sqft", label: "Plot Size", type: "number", unit: "sq ft", placeholder: "e.g. 100" },
        { key: "soil_type", label: "Soil Type", placeholder: "e.g. Sandy loam, Clay, Amended" },
        { key: "amendments", label: "Amendments", placeholder: "e.g. Compost, Worm castings, Bone meal" },
        { key: "sun_exposure", label: "Sun Exposure", options: ["full_sun_8plus_hrs", "partial_sun_6_hrs", "partial_shade_4_hrs", "dappled_light"] },
        { key: "irrigation", label: "Irrigation Method", options: ["hand_water", "drip_irrigation", "soaker_hose", "sprinkler", "rain_only"] },
        { key: "companion_plants", label: "Companion Plants", placeholder: "e.g. Basil, Marigold, Lavender", hint: "Natural pest deterrents" },
        { key: "pest_deterrent", label: "Pest Deterrent Methods", placeholder: "e.g. Neem, Diatomaceous earth, Companion planting" },
        { key: "frost_protection", label: "Frost Protection", options: ["row_cover", "cold_frame", "greenhouse", "bring_inside", "none_frost_free"] },
        { key: "hardiness_zone", label: "USDA Hardiness Zone", placeholder: "e.g. 7b", hint: "Helps predict growing season" },
        ...NUTRIENT_FIELDS,
      ];
    case "outdoor_container":
      return [
        { key: "container_type", label: "Container Type", options: ["plastic_pot", "fabric_pot", "air_pot", "terracotta", "smart_pot", "custom"] },
        { key: "container_color", label: "Container Color", options: ["white", "light_colored", "dark_colored", "black"], hint: "Dark pots overheat in sun" },
        { key: "pot_size_gal", label: "Container Size", type: "number", step: "0.5", unit: "gal", placeholder: "e.g. 10" },
        { key: "media_type", label: "Growing Media", placeholder: "e.g. Soil, Coco-Perlite mix" },
        { key: "mobility", label: "Can You Move Containers?", options: ["yes_easy", "yes_with_effort", "no_permanent"], hint: "Important for weather protection" },
        { key: "sun_exposure", label: "Sun Exposure", options: ["full_sun_8plus_hrs", "partial_sun_6_hrs", "partial_shade_4_hrs", "can_move_to_shade"] },
        { key: "irrigation", label: "Irrigation Method", options: ["hand_water", "drip_irrigation", "soaker_hose", "rain_only"] },
        { key: "frost_protection", label: "Frost Protection", options: ["move_indoors", "row_cover", "garage", "none_frost_free"] },
        { key: "saucer", label: "Saucer / Drip Tray?", options: ["yes", "no", "elevated_on_stand"], hint: "Prevents root sitting in water" },
        ...NUTRIENT_FIELDS,
      ];
    default:
      return [];
  }
}
