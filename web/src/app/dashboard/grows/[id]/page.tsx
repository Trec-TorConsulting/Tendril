"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/auth";
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
  listFeedingSchedules,
  createFeedingSchedule,
  listJournalEntries,
  getExportUrl,
  type GrowResponse,
  type BucketResponse,
  type SensorReadingResponse,
  type TentReadingResponse,
  type TentResponse,
  type FeedingScheduleResponse,
  type JournalEntryResponse,
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
  Camera,
  Droplets,
  Loader2,
  Pencil,
  CalendarDays,
  Download,
  Copy,
  Settings,
  Thermometer,
} from "lucide-react";

import { BrandTemplateDialog } from "./brand-template-dialog";
import { BucketsTab } from "./buckets-tab";
import { FeedingTab } from "./feeding-tab";
import { JournalTab } from "./journal-tab";
import { HarvestTab } from "./harvest-tab";
import { SensorsTab } from "./sensors-tab";
import { PhotosTab } from "./photos-tab";
import { TasksTab } from "./tasks-tab";
import { WeatherCard } from "./weather-card";

const STAGES = ["seedling", "vegetative", "flowering", "ripening", "drying", "curing"];
const MILESTONE_LABELS: Record<string, string> = {
  seedling: "Seedling / Germ",
  vegetative: "Veg Started",
  flowering: "Flower Started",
  ripening: "Ripening",
  drying: "Drying",
  curing: "Curing",
  harvest: "Harvest",
};

export default function GrowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [grow, setGrow] = useState<GrowResponse | null>(null);
  const [tent, setTent] = useState<TentResponse | null>(null);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, SensorReadingResponse | null>>({});
  const [feedingSchedules, setFeedingSchedules] = useState<FeedingScheduleResponse[]>([]);
  const [journalEntries, setJournalEntries] = useState<JournalEntryResponse[]>([]);

  // Sensor reading dialog
  const [sensorDialog, setSensorDialog] = useState<{ open: boolean; bucketId: string; bucketLabel: string }>({ open: false, bucketId: "", bucketLabel: "" });
  const [sensorForm, setSensorForm] = useState({ ph: "", ec: "", ppm: "", water_temp_f: "" });
  const [sensorSaving, setSensorSaving] = useState(false);

  // Tent ambient dialog
  const [ambientDialog, setAmbientDialog] = useState(false);
  const [ambientForm, setAmbientForm] = useState({ ambient_temp_f: "", ambient_humidity: "" });
  const [ambientSaving, setAmbientSaving] = useState(false);
  const [tentAmbient, setTentAmbient] = useState<TentReadingResponse | null>(null);

  // Edit grow dialog
  const [editGrowDialog, setEditGrowDialog] = useState(false);
  const [editGrowForm, setEditGrowForm] = useState({ name: "", notes: "", started_at: "", milestones: {} as Record<string, string> });
  const [editGrowSaving, setEditGrowSaving] = useState(false);

  // Brand template dialog
  const [brandDialog, setBrandDialog] = useState(false);

  // Clone dialog
  const [cloneDialog, setCloneDialog] = useState(false);
  const [cloneName, setCloneName] = useState("");
  const [cloneSaving, setCloneSaving] = useState(false);

  // Settings dialog
  const [settingsDialog, setSettingsDialog] = useState(false);
  const [settingsForm, setSettingsForm] = useState<Record<string, string>>({});
  const [settingsSaving, setSettingsSaving] = useState(false);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const [g, bkts] = await Promise.all([
      getGrow(token, id),
      listBuckets(token, id),
    ]);
    setGrow(g);
    setBuckets(bkts);

    try { setTent(await getTent(token, g.tent_id)); } catch { setTent(null); }

    try { setTentAmbient(await getLatestTentReading(token, g.tent_id)); } catch { setTentAmbient(null); }

    const readings: Record<string, SensorReadingResponse | null> = {};
    await Promise.all(
      bkts.map(async (b) => {
        try { readings[b.id] = await getLatestReading(token, b.id); } catch { readings[b.id] = null; }
      }),
    );
    setLatestReadings(readings);

    try { setFeedingSchedules(await listFeedingSchedules(token, id)); } catch { /* empty */ }

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

  // --- Handlers ---

  const handleComplete = async () => {
    if (!confirm("Mark this grow as completed?")) return;
    const token = getAccessToken();
    if (!token) return;
    await updateGrow(token, id, { status: "completed" });
    refresh();
  };

  const handleSensorSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setSensorSaving(true);
    try {
      const data: Record<string, unknown> = { bucket_id: sensorDialog.bucketId };
      if (sensorForm.ph) data.ph = parseFloat(sensorForm.ph);
      if (sensorForm.ec) data.ec = parseFloat(sensorForm.ec);
      if (sensorForm.ppm) data.ppm = parseFloat(sensorForm.ppm);
      if (sensorForm.water_temp_f) data.water_temp_f = parseFloat(sensorForm.water_temp_f);
      await createSensorReading(token, data as Parameters<typeof createSensorReading>[1]);
      setSensorDialog({ open: false, bucketId: "", bucketLabel: "" });
      setSensorForm({ ph: "", ec: "", ppm: "", water_temp_f: "" });
      refresh();
    } catch { /* empty */ } finally { setSensorSaving(false); }
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
      if (Object.keys(ms).length) payload.milestones = ms;
      await updateGrow(token, id, payload);
      setEditGrowDialog(false);
      refresh();
    } catch { /* empty */ } finally { setEditGrowSaving(false); }
  };

  const handleExport = () => {
    const token = getAccessToken();
    if (!token || buckets.length === 0) return;
    // Export all buckets
    for (const b of buckets) {
      const url = getExportUrl(token, b.id);
      window.open(url, "_blank");
    }
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
      // Copy buckets
      for (const b of buckets) {
        await createBucket(token, {
          grow_cycle_id: newGrow.id,
          label: b.label || undefined,
          strain_id: b.strain_id || undefined,
          strain_name: b.strain_name || undefined,
          position: b.position,
          volume_gallons: b.volume_gallons || undefined,
        });
      }
      // Copy feeding schedules
      for (const fs of feedingSchedules) {
        await createFeedingSchedule(token, {
          grow_cycle_id: newGrow.id,
          name: fs.name,
          stage: fs.stage,
          nutrients: fs.nutrients,
          notes: fs.notes || undefined,
        });
      }
      setCloneDialog(false);
      setCloneName("");
      router.push(`/dashboard/grows/${newGrow.id}`);
    } catch { /* empty */ } finally { setCloneSaving(false); }
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
    } catch { /* empty */ } finally { setSettingsSaving(false); }
  };

  // --- Render ---

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
  const settingsSchema = getSettingsSchema(grow.grow_type);

  return (
    <>
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
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Grow Info Card */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">Grow Info</CardTitle>
              <div className="flex items-center gap-1">
                {settingsSchema.length > 0 && (
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => {
                    const form: Record<string, string> = {};
                    for (const s of settingsSchema) form[s.key] = ((grow.settings as Record<string, unknown>)?.[s.key] as string) || "";
                    setSettingsForm(form);
                    setSettingsDialog(true);
                  }}>
                    <Settings className="mr-1 size-3" /> Settings
                  </Button>
                )}
                <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => {
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
                }}>
                  <Pencil className="mr-1 size-3" /> Edit
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-x-6 gap-y-2 sm:grid-cols-2 lg:grid-cols-3 text-sm">
              <div><span className="text-muted-foreground">Type</span><p className="font-medium">{grow.grow_type}</p></div>
              <div><span className="text-muted-foreground">Stage</span><p className="font-medium capitalize">{grow.stage}</p></div>
              <div><span className="text-muted-foreground">Status</span><p className="font-medium"><Badge variant={grow.status === "active" ? "default" : "secondary"} className="text-xs">{grow.status}</Badge></p></div>
              <div><span className="text-muted-foreground">Tent</span><p className="font-medium">{tent?.name || "\u2014"}</p></div>
              <div><span className="text-muted-foreground">Started</span><p className="font-medium">{new Date(grow.started_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</p></div>
              {grow.ended_at && <div><span className="text-muted-foreground">Ended</span><p className="font-medium">{new Date(grow.ended_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</p></div>}
              <div><span className="text-muted-foreground">Buckets</span><p className="font-medium">{buckets.length}</p></div>
            </div>

            {/* Type-specific settings display */}
            {grow.settings && Object.keys(grow.settings).length > 0 && (
              <div className="mt-3 border-t pt-3">
                <div className="mb-1.5 flex items-center gap-1 text-xs font-medium text-muted-foreground">
                  <Settings className="size-3" /> Grow Settings
                </div>
                <div className="grid gap-x-6 gap-y-1 sm:grid-cols-2 lg:grid-cols-3 text-sm">
                  {settingsSchema.map((s) => {
                    const val = (grow.settings as Record<string, unknown>)?.[s.key];
                    if (!val) return null;
                    return (
                      <div key={s.key}>
                        <span className="text-muted-foreground">{s.label}</span>
                        <p className="font-medium">{String(val)}{s.unit || ""}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Milestone dates */}
            {grow.milestones && Object.keys(grow.milestones).length > 0 && (
              <div className="mt-3 border-t pt-3">
                <div className="mb-1.5 flex items-center gap-1 text-xs font-medium text-muted-foreground">
                  <CalendarDays className="size-3" /> Milestones
                </div>
                <div className="grid gap-x-6 gap-y-1 sm:grid-cols-2 lg:grid-cols-3 text-sm">
                  {[...STAGES, "harvest"].map((key) => {
                    const iso = grow.milestones?.[key];
                    if (!iso) return null;
                    return (
                      <div key={key}>
                        <span className="text-muted-foreground">{MILESTONE_LABELS[key] || key}</span>
                        <p className="font-medium">{new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {grow.notes && (
              <div className="mt-3 border-t pt-3 text-sm">
                <span className="text-muted-foreground">Notes</span>
                <p className="mt-0.5 whitespace-pre-wrap">{grow.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tent Ambient */}
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Thermometer className="size-4" /> Tent Environment
              </CardTitle>
              <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => {
                setAmbientForm({ ambient_temp_f: "", ambient_humidity: "" });
                setAmbientDialog(true);
              }}>
                <Droplets className="mr-1 size-3" /> Log Ambient
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {tentAmbient ? (
              <div className="flex items-center gap-4 text-sm">
                {tentAmbient.ambient_temp_f != null && <span>🌡 {tentAmbient.ambient_temp_f.toFixed(1)}°F</span>}
                {tentAmbient.ambient_humidity != null && <span>💧 {tentAmbient.ambient_humidity.toFixed(0)}%</span>}
                <span className="text-xs text-muted-foreground">{new Date(tentAmbient.recorded_at).toLocaleString()}</span>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No ambient readings yet</p>
            )}
          </CardContent>
        </Card>

        {/* Weather (for outdoor/greenhouse tents) */}
        {tent && <WeatherCard tentId={tent.id} tentName={tent.name} environmentType={tent.environment_type} />}

        {/* Camera Snapshot */}
        {tent?.camera_url && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-sm font-medium">
                <Camera className="size-4" /> Camera Snapshot
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-hidden rounded-lg border bg-black">
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1"}/tents/${grow.tent_id}/camera-snapshot?token=${encodeURIComponent(getAccessToken() || "")}&t=${Date.now()}`}
                  alt="Camera snapshot"
                  className="aspect-video w-full object-contain"
                />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">Latest snapshot from {tent.name}</p>
            </CardContent>
          </Card>
        )}

        {/* Tabbed sections */}
        <Tabs defaultValue="buckets">
          <TabsList className="flex-wrap">
            <TabsTrigger value="buckets">Buckets ({buckets.length})</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="feeding">Feeding</TabsTrigger>
            <TabsTrigger value="journal">Journal</TabsTrigger>
            <TabsTrigger value="harvest">Harvest</TabsTrigger>
            <TabsTrigger value="sensors">Sensors</TabsTrigger>
            <TabsTrigger value="photos">Photos</TabsTrigger>
          </TabsList>

          <TabsContent value="buckets" className="mt-4">
            <BucketsTab
              growId={id}
              buckets={buckets}
              latestReadings={latestReadings}
              onRefresh={refresh}
              onOpenSensorDialog={(bucketId, label) => {
                setSensorForm({ ph: "", ec: "", ppm: "", water_temp_f: "" });
                setSensorDialog({ open: true, bucketId, bucketLabel: label });
              }}
            />
          </TabsContent>

          <TabsContent value="tasks" className="mt-4">
            <TasksTab growId={id} />
          </TabsContent>

          <TabsContent value="feeding" className="mt-4">
            <FeedingTab
              growId={id}
              growStage={grow.stage}
              buckets={buckets}
              feedingSchedules={feedingSchedules}
              onRefresh={refresh}
              onOpenBrandDialog={() => setBrandDialog(true)}
            />
          </TabsContent>

          <TabsContent value="journal" className="mt-4">
            <JournalTab
              buckets={buckets}
              journalEntries={journalEntries}
              bucketLabelMap={bucketLabelMap}
              onRefresh={refresh}
            />
          </TabsContent>

          <TabsContent value="harvest" className="mt-4">
            <HarvestTab growId={id} buckets={buckets} />
          </TabsContent>

          <TabsContent value="sensors" className="mt-4">
            <SensorsTab buckets={buckets} />
          </TabsContent>

          <TabsContent value="photos" className="mt-4">
            <PhotosTab growId={id} buckets={buckets} />
          </TabsContent>
        </Tabs>
      </div>

      {/* --- SENSOR READING DIALOG --- */}
      <Dialog open={sensorDialog.open} onOpenChange={(open) => !open && setSensorDialog({ open: false, bucketId: "", bucketLabel: "" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Log Sensor Reading</DialogTitle>
            <DialogDescription>Record current readings for {sensorDialog.bucketLabel}</DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">pH</Label>
              <Input type="number" step="0.1" placeholder="e.g. 5.8" value={sensorForm.ph} onChange={(e) => setSensorForm((p) => ({ ...p, ph: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">EC (mS/cm)</Label>
              <Input type="number" step="0.01" placeholder="e.g. 1.20" value={sensorForm.ec} onChange={(e) => setSensorForm((p) => ({ ...p, ec: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">PPM</Label>
              <Input type="number" step="1" placeholder="e.g. 850" value={sensorForm.ppm} onChange={(e) => setSensorForm((p) => ({ ...p, ppm: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Water Temp °F</Label>
              <Input type="number" step="0.1" placeholder="e.g. 68.0" value={sensorForm.water_temp_f} onChange={(e) => setSensorForm((p) => ({ ...p, water_temp_f: e.target.value }))} />
            </div>
          </div>
          <p className="text-xs text-muted-foreground">Ambient temp & humidity are logged at the tent level. <button type="button" className="underline" onClick={() => { setSensorDialog({ open: false, bucketId: "", bucketLabel: "" }); setAmbientDialog(true); }}>Log ambient reading →</button></p>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setSensorDialog({ open: false, bucketId: "", bucketLabel: "" })}>Cancel</Button>
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
              Last reading: {tentAmbient.ambient_temp_f != null && `${tentAmbient.ambient_temp_f.toFixed(1)}°F`} {tentAmbient.ambient_humidity != null && `${tentAmbient.ambient_humidity.toFixed(0)}%`} — {new Date(tentAmbient.recorded_at).toLocaleString()}
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Ambient Temp °F</Label>
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
                <li>{feedingSchedules.length} feeding schedule(s)</li>
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

      {/* --- BRAND TEMPLATE DIALOG --- */}
      <BrandTemplateDialog
        open={brandDialog}
        onOpenChange={setBrandDialog}
        growCycleId={id}
        onComplete={refresh}
      />
    </>
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

function getSettingsSchema(growType: string): SettingsField[] {
  // Common indoor light fields (hardware lives on Tent equipment; these are per-grow-cycle)
  const LIGHT_FIELDS: SettingsField[] = [
    { key: "light_schedule", label: "Light Schedule", group: "lighting", placeholder: "e.g. 18/6, 12/12", hint: "Hours on / hours off" },
    { key: "light_height_in", label: "Light Height", group: "lighting", type: "number", unit: "in", placeholder: "e.g. 24" },
  ];
  // Common environment fields
  const ENV_FIELDS: SettingsField[] = [
    { key: "target_vpd", label: "Target VPD", group: "environment", type: "number", step: "0.1", unit: "kPa", placeholder: "e.g. 1.2", hint: "Vapor Pressure Deficit target" },
    { key: "target_temp_day_f", label: "Day Temp Target", group: "environment", type: "number", step: "1", unit: "°F", placeholder: "e.g. 80" },
    { key: "target_temp_night_f", label: "Night Temp Target", group: "environment", type: "number", step: "1", unit: "°F", placeholder: "e.g. 70" },
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
        { key: "target_ph", label: "Target pH", type: "number", step: "0.1", placeholder: "e.g. 5.8", hint: "Coco optimal range: 5.5–6.5" },
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
