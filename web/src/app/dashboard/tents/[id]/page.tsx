"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import { getTent, updateTent, deleteTent, listGrows, listSchedules, listDevices, listTentReadings, deleteTentReading, getTentSensorTrends, listTentCameras, createTentCamera, updateTentCamera, deleteTentCamera, type TentResponse, type GrowResponse, type ScheduleResponse, type DeviceResponse, type TentReadingResponse, type CameraResponse, type EquipmentItem } from "@/lib/api";
import { useConfirm } from "@/components/confirm-dialog";
import { CameraGrid } from "@/components/camera-grid";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { formatCalendarDate, formatDateTime } from "@/lib/utils";
import { Warehouse, MapPin, Camera, Sprout, Calendar, Cpu, Lightbulb, Fan, Snowflake, Droplets, Settings, ArrowRight, Trash2, Activity, Thermometer, Pencil, Plus, X, Loader2, LocateFixed, Search } from "lucide-react";
import { toast } from "sonner";

const EQUIPMENT_LABELS: Record<string, string> = {
  grow_light: "Grow Light",
  exhaust_fan: "Exhaust Fan",
  inline_fan: "Inline Fan",
  oscillating_fan: "Oscillating Fan",
  air_pump: "Air Pump",
  water_pump: "Water / Circulation Pump",
  water_chiller: "Water Chiller",
  carbon_filter: "Carbon Filter",
  humidifier: "Humidifier",
  dehumidifier: "Dehumidifier",
  heater: "Heater",
  ac_unit: "AC Unit",
  co2_system: "CO₂ System",
  controller: "Controller / Automation",
  custom: "Other",
};

const EQUIPMENT_TYPES = [
  { value: "grow_light", label: "Grow Light" },
  { value: "exhaust_fan", label: "Exhaust Fan" },
  { value: "inline_fan", label: "Inline Fan" },
  { value: "oscillating_fan", label: "Oscillating Fan" },
  { value: "air_pump", label: "Air Pump" },
  { value: "water_pump", label: "Water / Circulation Pump" },
  { value: "water_chiller", label: "Water Chiller" },
  { value: "carbon_filter", label: "Carbon Filter" },
  { value: "humidifier", label: "Humidifier" },
  { value: "dehumidifier", label: "Dehumidifier" },
  { value: "heater", label: "Heater" },
  { value: "ac_unit", label: "AC Unit" },
  { value: "co2_system", label: "CO₂ System" },
  { value: "controller", label: "Controller / Automation" },
  { value: "custom", label: "Other (custom)" },
] as const;

const TENT_SIZES = ["2x2", "2x4", "3x3", "4x4", "4x8", "5x5", "5x10", "8x8", "10x10"];
const ENV_TYPES = ["indoor", "outdoor", "greenhouse"];

interface CameraFormItem {
  id?: string;
  label: string;
  url: string;
  is_primary: boolean;
}

function emptyEquipment(): EquipmentItem {
  return { type: "exhaust_fan", brand: "", model: "", specs: "", quantity: 1 };
}

function emptyCamera(): CameraFormItem {
  return { label: "Camera", url: "", is_primary: false };
}

const scheduleTypeIcon: Record<string, React.ReactNode> = {
  light: <Lightbulb className="size-4" />,
  fan: <Fan className="size-4" />,
  hvac: <Snowflake className="size-4" />,
  pump: <Droplets className="size-4" />,
};

export default function TentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { data: rawData, isLoading: loading, mutate } = useApiSWR(
    ["tent-detail", id],
    async (token) => {
      const [t, g, s, d, readings, trends, cams] = await Promise.all([
        getTent(token, id),
        listGrows(token, { tent_id: id }).catch(() => [] as GrowResponse[]),
        listSchedules(token, id).catch(() => [] as ScheduleResponse[]),
        listDevices(token).catch(() => [] as DeviceResponse[]),
        listTentReadings(token, id, 50).catch(() => [] as TentReadingResponse[]),
        getTentSensorTrends(token, id).catch(() => null),
        listTentCameras(token, id).catch(() => [] as CameraResponse[]),
      ]);
      return {
        tent: t,
        grows: g,
        schedules: s,
        devices: d.filter((dev) => dev.tent_id === id),
        tentReadings: readings,
        tentTrends: trends,
        cameras: cams,
      };
    },
  );
  const tent = rawData?.tent ?? null;
  const grows = rawData?.grows ?? [];
  const schedules = rawData?.schedules ?? [];
  const devices = rawData?.devices ?? [];
  const tentReadings = rawData?.tentReadings ?? [];
  const tentTrends = rawData?.tentTrends ?? null;
  const cameras = rawData?.cameras ?? [];
  const refresh = mutate;
  const confirm = useConfirm();

  // Edit sheet state
  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editEnvType, setEditEnvType] = useState("indoor");
  const [editSize, setEditSize] = useState("");
  const [editLatitude, setEditLatitude] = useState("");
  const [editLongitude, setEditLongitude] = useState("");
  const [editZipCode, setEditZipCode] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editEquipment, setEditEquipment] = useState<EquipmentItem[]>([]);
  const [editCameras, setEditCameras] = useState<CameraFormItem[]>([]);
  const [existingCameraIds, setExistingCameraIds] = useState<string[]>([]);
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState("");
  const [geoLoading, setGeoLoading] = useState(false);
  const [zipLoading, setZipLoading] = useState(false);

  const openEdit = () => {
    if (!tent) return;
    setEditName(tent.name);
    setEditEnvType(tent.environment_type);
    setEditSize(tent.size ?? "");
    setEditLatitude(tent.latitude?.toString() ?? "");
    setEditLongitude(tent.longitude?.toString() ?? "");
    setEditZipCode("");
    setEditNotes(tent.notes ?? "");
    setEditEquipment((tent.equipment ?? []).map((e) => ({ ...e, quantity: e.quantity ?? 1 })));
    const items = cameras.map((c) => ({ id: c.id, label: c.label, url: c.url, is_primary: c.is_primary }));
    setEditCameras(items);
    setExistingCameraIds(cameras.map((c) => c.id));
    setEditError("");
    setEditOpen(true);
  };

  const handleEditSave = async () => {
    const token = getAccessToken();
    if (!token || !editName.trim()) return;
    setEditSaving(true);
    setEditError("");
    try {
      const cleanEquipment = editEquipment.filter((e) => e.type);
      const validCameras = editCameras.filter((c) => c.url.trim());

      await updateTent(token, id, {
        name: editName.trim(),
        environment_type: editEnvType,
        size: editSize.trim() || null,
        ...(editLatitude ? { latitude: parseFloat(editLatitude) } : {}),
        ...(editLongitude ? { longitude: parseFloat(editLongitude) } : {}),
        equipment: cleanEquipment,
        notes: editNotes.trim() || null,
      });

      // Sync cameras
      const keptIds = validCameras.filter((c) => c.id).map((c) => c.id!);
      const toDelete = existingCameraIds.filter((cid) => !keptIds.includes(cid));
      await Promise.all(toDelete.map((cid) => deleteTentCamera(token, id, cid)));
      for (const cam of validCameras) {
        if (cam.id) {
          await updateTentCamera(token, id, cam.id, { label: cam.label, url: cam.url, is_primary: cam.is_primary });
        } else {
          await createTentCamera(token, id, { label: cam.label, url: cam.url, is_primary: cam.is_primary });
        }
      }

      setEditOpen(false);
      refresh();
    } catch (e: unknown) {
      setEditError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setEditSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!await confirm({ title: "Delete Space", description: "This will permanently delete this grow space and all its data. Are you sure?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteTent(token, id);
      router.push("/dashboard/tents");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to delete grow space");
    }
  };

  const handleAutoLocate = () => {
    if (!navigator.geolocation) return;
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => { setEditLatitude(pos.coords.latitude.toFixed(6)); setEditLongitude(pos.coords.longitude.toFixed(6)); setGeoLoading(false); },
      () => { setGeoLoading(false); },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const handleZipLookup = async () => {
    const zip = editZipCode.trim();
    if (!zip) return;
    setZipLoading(true);
    try {
      const res = await fetch(`https://api.zippopotam.us/us/${encodeURIComponent(zip)}`);
      if (!res.ok) throw new Error("Invalid zip code");
      const data = await res.json();
      const place = data.places?.[0];
      if (place) { setEditLatitude(parseFloat(place.latitude).toFixed(6)); setEditLongitude(parseFloat(place.longitude).toFixed(6)); }
    } catch { /* empty */ } finally { setZipLoading(false); }
  };

  if (loading) return <PageSkeleton rows={4} cards />;
  if (!tent) return <p className="p-6 text-muted-foreground">Grow space not found.</p>;

  const activeGrows = grows.filter((g) => g.status === "active");
  const pastGrows = grows.filter((g) => g.status !== "active");
  const hasEquipmentOrCameras = (tent.equipment && tent.equipment.length > 0) || cameras.length > 0;

  return (
    <>
      <PageHeader
        title={tent.name}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Grow Spaces", href: "/dashboard/tents" },
          { label: tent.name },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={openEdit}>
              <Pencil className="mr-1 size-4" /> Edit
            </Button>
            <Button variant="outline" size="sm" className="text-destructive hover:text-destructive" onClick={handleDelete}>
              <Trash2 className="mr-1 size-4" /> Delete
            </Button>
          </div>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Space Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Warehouse className="size-4" /> Space Details
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="capitalize">{tent.environment_type}</Badge>
              {tent.size && <Badge variant="outline">{tent.size}</Badge>}
            </div>
            {(tent.latitude || tent.longitude) && (
              <p className="flex items-center gap-1 text-sm text-muted-foreground">
                <MapPin className="size-3" />
                {tent.latitude?.toFixed(4)}, {tent.longitude?.toFixed(4)}
              </p>
            )}
            {tent.notes && (
              <p className="text-sm text-muted-foreground whitespace-pre-line">{tent.notes}</p>
            )}
          </CardContent>
        </Card>

        {/* Equipment & Cameras */}
        {hasEquipmentOrCameras && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Settings className="size-4" /> Equipment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {cameras.length > 0 && (
                <CameraGrid tentId={tent.id} />
              )}
              {tent.equipment && tent.equipment.length > 0 && (
                <div className="grid gap-2 sm:grid-cols-2">
                  {tent.equipment.map((e, i) => (
                    <div key={i} className="flex items-center gap-3 rounded-lg border p-3">
                      <Fan className="size-4 shrink-0 text-muted-foreground" />
                      <div className="min-w-0">
                        <p className="text-sm font-medium">
                          {e.quantity > 1 ? `${e.quantity}× ` : ""}{EQUIPMENT_LABELS[e.type] || e.type}
                        </p>
                        {(e.brand || e.model) && (
                          <p className="text-xs text-muted-foreground truncate">
                            {[e.brand, e.model].filter(Boolean).join(" · ")}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Active Grows */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sprout className="size-4" /> Grows in this Space
            </CardTitle>
            {grows.length > 0 && (
              <Button variant="ghost" size="sm" render={<Link href="/dashboard/grows" />}>
                All Grows <ArrowRight className="ml-1 size-3" />
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {grows.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Sprout className="size-8 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">No grows in this space yet.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activeGrows.map((g) => (
                  <Link key={g.id} href={`/dashboard/grows/${g.id}`} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50">
                    <div>
                      <p className="font-medium">{g.name}</p>
                      <p className="text-xs text-muted-foreground">{g.grow_type} · Stage: {g.stage} · Started {formatCalendarDate(g.started_at)}</p>
                    </div>
                    <Badge variant="default">{g.status}</Badge>
                  </Link>
                ))}
                {pastGrows.length > 0 && (
                  <>
                    <p className="pt-2 text-xs font-medium text-muted-foreground">Past ({pastGrows.length})</p>
                    {pastGrows.slice(0, 5).map((g) => (
                      <Link key={g.id} href={`/dashboard/grows/${g.id}`} className="flex items-center justify-between rounded-lg border p-3 opacity-60 transition-colors hover:bg-muted/50">
                        <div>
                          <p className="font-medium">{g.name}</p>
                          <p className="text-xs text-muted-foreground">{g.grow_type}</p>
                        </div>
                        <Badge variant="secondary">{g.status}</Badge>
                      </Link>
                    ))}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Schedules */}
        {schedules.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Calendar className="size-4" /> Schedules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {schedules.map((s) => (
                  <div key={s.id} className="flex items-center gap-3 rounded-lg border p-3">
                    {scheduleTypeIcon[s.schedule_type] || <Settings className="size-4" />}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{s.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {s.on_time} → {s.off_time}
                        {s.stage && ` · ${s.stage}`}
                      </p>
                    </div>
                    <Badge variant={s.enabled ? "default" : "outline"} className="text-xs">
                      {s.enabled ? "On" : "Off"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Devices */}
        {devices.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="size-4" /> Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {devices.map((d) => (
                  <div key={d.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="text-sm font-medium">{d.label || d.device_id}</p>
                      {d.firmware_version && (
                        <p className="text-xs text-muted-foreground">FW {d.firmware_version}</p>
                      )}
                    </div>
                    <Badge variant={d.status === "online" ? "default" : "outline"} className="text-xs">
                      {d.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tent Readings History */}
        {tentReadings.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Thermometer className="size-4" /> Ambient Readings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="p-2 text-left font-medium">Time</th>
                      <th className="p-2 text-right font-medium">Temp °F</th>
                      <th className="p-2 text-right font-medium">Humidity %</th>
                      <th className="p-2 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tentReadings.slice(0, 20).map((r) => (
                      <tr key={r.id} className="border-b last:border-0 hover:bg-muted/50">
                        <td className="p-2 text-muted-foreground">{formatDateTime(r.recorded_at)}</td>
                        <td className="p-2 text-right font-mono">{r.ambient_temp_f?.toFixed(1) ?? "—"}</td>
                        <td className="p-2 text-right font-mono">{r.ambient_humidity?.toFixed(0) ?? "—"}</td>
                        <td className="p-2 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                            onClick={async () => {
                              if (!await confirm({ title: "Delete Reading", description: "Permanently delete this ambient reading?", confirmLabel: "Delete", variant: "destructive" })) return;
                              const token = getAccessToken();
                              if (!token) return;
                              await deleteTentReading(token, r.id);
                              refresh();
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
              {tentReadings.length > 20 && (
                <p className="mt-2 text-center text-xs text-muted-foreground">Showing 20 of {tentReadings.length} readings</p>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Edit Sheet */}
      <Sheet open={editOpen} onOpenChange={(open) => !open && setEditOpen(false)}>
        <SheetContent side="right" className="sm:max-w-lg w-full flex flex-col">
          <SheetHeader>
            <SheetTitle>Edit Grow Space</SheetTitle>
            <SheetDescription>Update your grow space details, equipment, and cameras.</SheetDescription>
          </SheetHeader>
          {editError && (
            <p className="text-sm text-destructive">{editError}</p>
          )}
          <div className="flex-1 overflow-y-auto -mx-6 px-6 space-y-6 pb-4">
            {/* Basics */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Basics</h4>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label className="text-xs">Name</Label>
                  <Input value={editName} onChange={(e) => setEditName(e.target.value)} placeholder="e.g. Veg Tent" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Environment</Label>
                  <Select value={editEnvType} onValueChange={(v) => setEditEnvType(v ?? "indoor")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {ENV_TYPES.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Size</Label>
                  <Select value={editSize || "__custom__"} onValueChange={(v) => setEditSize(!v || v === "__custom__" ? "" : v)}>
                    <SelectTrigger><SelectValue placeholder="Select size" /></SelectTrigger>
                    <SelectContent>
                      {TENT_SIZES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      <SelectItem value="__custom__">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                  {(!editSize || !TENT_SIZES.includes(editSize)) && (
                    <Input className="mt-1" value={editSize} onChange={(e) => setEditSize(e.target.value)} placeholder="e.g. 4x4x8" />
                  )}
                </div>
                <div className="space-y-1 sm:col-span-2">
                  <Label className="text-xs">Notes</Label>
                  <Textarea value={editNotes} onChange={(e) => setEditNotes(e.target.value)} placeholder="Any extra details..." rows={2} className="text-xs" />
                </div>
              </div>
            </div>

            {/* Location */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Location</h4>
                <Button type="button" variant="ghost" size="sm" onClick={handleAutoLocate} disabled={geoLoading} className="h-6 gap-1 text-xs">
                  {geoLoading ? <Loader2 className="size-3 animate-spin" /> : <LocateFixed className="size-3" />}
                  {geoLoading ? "Locating…" : "Auto-detect"}
                </Button>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Zip Code</Label>
                  <div className="flex gap-1">
                    <Input placeholder="e.g. 90210" value={editZipCode} onChange={(e) => setEditZipCode(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleZipLookup())} />
                    <Button type="button" variant="outline" size="icon" className="shrink-0" onClick={handleZipLookup} disabled={zipLoading || !editZipCode.trim()}>
                      {zipLoading ? <Loader2 className="size-3.5 animate-spin" /> : <Search className="size-3.5" />}
                    </Button>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Latitude</Label>
                  <Input type="number" step="any" value={editLatitude} onChange={(e) => setEditLatitude(e.target.value)} placeholder="34.0522" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Longitude</Label>
                  <Input type="number" step="any" value={editLongitude} onChange={(e) => setEditLongitude(e.target.value)} placeholder="-118.2437" />
                </div>
              </div>
            </div>

            {/* Cameras */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <Camera className="inline size-3 mr-1" />Cameras
                </h4>
                <Button type="button" variant="outline" size="sm" className="h-7 text-xs" onClick={() => setEditCameras((prev) => [...prev, emptyCamera()])}>
                  <Plus className="mr-1 size-3" /> Add Camera
                </Button>
              </div>
              {editCameras.length === 0 ? (
                <p className="text-xs text-muted-foreground py-1">No cameras. Click Add Camera to connect a feed.</p>
              ) : (
                <div className="space-y-2">
                  {editCameras.map((cam, idx) => (
                    <div key={idx} className="rounded-lg border p-3 space-y-2 relative">
                      <Button type="button" variant="ghost" size="icon" className="absolute top-1 right-1 size-6" onClick={() => setEditCameras((prev) => prev.filter((_, i) => i !== idx))}>
                        <X className="size-3.5" />
                      </Button>
                      <div className="grid gap-2 sm:grid-cols-2 pr-6">
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Label</Label>
                          <Input className="h-8 text-xs" value={cam.label} onChange={(e) => setEditCameras((prev) => prev.map((c, i) => i === idx ? { ...c, label: e.target.value } : c))} placeholder="e.g. Top-down" />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">URL</Label>
                          <Input className="h-8 text-xs" value={cam.url} onChange={(e) => setEditCameras((prev) => prev.map((c, i) => i === idx ? { ...c, url: e.target.value } : c))} placeholder="http://192.168.1.50/snap" />
                        </div>
                      </div>
                      <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer">
                        <input type="checkbox" checked={cam.is_primary} onChange={(e) => setEditCameras((prev) => prev.map((c, i) => i === idx ? { ...c, is_primary: e.target.checked } : c))} className="size-3.5 rounded" />
                        Primary camera
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Equipment */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <Fan className="inline size-3 mr-1" />Equipment
                </h4>
                <Button type="button" variant="outline" size="sm" className="h-7 text-xs" onClick={() => setEditEquipment((prev) => [...prev, emptyEquipment()])}>
                  <Plus className="mr-1 size-3" /> Add Equipment
                </Button>
              </div>
              {editEquipment.length === 0 ? (
                <p className="text-xs text-muted-foreground py-2">No equipment added yet.</p>
              ) : (
                <div className="space-y-3">
                  {editEquipment.map((item, idx) => (
                    <div key={idx} className="rounded-lg border p-3 space-y-2 relative">
                      <Button type="button" variant="ghost" size="icon" className="absolute top-1 right-1 size-6" onClick={() => setEditEquipment((prev) => prev.filter((_, i) => i !== idx))}>
                        <X className="size-3.5" />
                      </Button>
                      <div className="grid gap-2 sm:grid-cols-2 pr-6">
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Type</Label>
                          <Select value={item.type} onValueChange={(v) => { if (v) setEditEquipment((prev) => prev.map((e, i) => i === idx ? { ...e, type: v } : e)); }}>
                            <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {EQUIPMENT_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Brand</Label>
                          <Input className="h-8 text-xs" value={item.brand ?? ""} onChange={(e) => setEditEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, brand: e.target.value } : eq))} placeholder="Brand name" />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Model</Label>
                          <Input className="h-8 text-xs" value={item.model ?? ""} onChange={(e) => setEditEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, model: e.target.value } : eq))} placeholder="e.g. Cloudline T6" />
                        </div>
                        <div className="grid grid-cols-[1fr_60px] gap-2">
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">Specs</Label>
                            <Input className="h-8 text-xs" value={item.specs ?? ""} onChange={(e) => setEditEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, specs: e.target.value } : eq))} placeholder="e.g. 402 CFM" />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">Qty</Label>
                            <Input className="h-8 text-xs" type="number" min={1} max={20} value={item.quantity} onChange={(e) => setEditEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, quantity: Math.max(1, parseInt(e.target.value) || 1) } : eq))} />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
          <SheetFooter className="border-t pt-4 -mx-6 px-6">
            <Button variant="outline" type="button" onClick={() => setEditOpen(false)}>Cancel</Button>
            <Button type="button" onClick={handleEditSave} disabled={editSaving || !editName.trim()}>
              {editSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editSaving ? "Saving…" : "Save"}
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </>
  );
}
