"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import { listTents, createTent, updateTent, deleteTent, listTentCameras, createTentCamera, updateTentCamera, deleteTentCamera } from "@/lib/api";
import type { TentResponse, EquipmentItem, CameraResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, MoreHorizontal, Pencil, Trash2, MapPin, Warehouse, Loader2, LocateFixed, Search, Camera, Fan, X } from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useConfirm } from "@/components/confirm-dialog";

// Equipment presets
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

const BRAND_SUGGESTIONS: Record<string, string[]> = {
  grow_light: ["Spider Farmer", "HLG (Horticulture Lighting Group)", "Mars Hydro", "AC Infinity", "Vivosun", "Gavita", "Luxx", "Growers Choice", "Kind LED", "Fluence"],
  exhaust_fan: ["AC Infinity", "Vivosun", "TerraBloom", "Can-Fan", "Hurricane", "iPower"],
  inline_fan: ["AC Infinity", "Vivosun", "TerraBloom", "Can-Fan", "Hurricane", "iPower"],
  oscillating_fan: ["Secret Jardin", "Hurricane", "AC Infinity", "Vivosun", "Honeywell", "Lasko"],
  air_pump: ["EcoPlus", "Active Aqua", "Vivosun", "Hydrofarm", "Pawfly", "Tetra"],
  water_pump: ["Active Aqua", "EcoPlus", "Hydrofarm", "Vivosun", "Aquatec", "Danner"],
  water_chiller: ["Active Aqua", "EcoPlus", "Hydrofarm", "JBJ", "IceProbe"],
  carbon_filter: ["Phresh", "Can-Fan", "AC Infinity", "Vivosun", "TerraBloom", "Fox Carbon"],
  humidifier: ["Levoit", "TaoTronics", "AC Infinity", "Vivosun", "hOmeLabs"],
  dehumidifier: ["hOmeLabs", "Frigidaire", "Midea", "Tosot", "AC Infinity"],
  heater: ["Dr. Infrared", "Lasko", "Vornado", "De'Longhi", "Bio Green"],
  ac_unit: ["Midea", "LG", "Frigidaire", "Black+Decker", "Whynter"],
  co2_system: ["Titan Controls", "Autopilot", "Hydrofarm", "ExHale"],
  controller: ["AC Infinity Controller 69 Pro", "Vivosun GrowHub", "Trolmaster Hydro-X", "Pulse One", "Inkbird", "Niwa"],
};

const TENT_SIZES = ["2x2", "2x4", "3x3", "4x4", "4x8", "5x5", "5x10", "8x8", "10x10"];

type ModalState =
  | { type: "closed" }
  | { type: "create" }
  | { type: "edit"; tent: TentResponse };

const ENV_TYPES = ["indoor", "outdoor", "greenhouse"];

function emptyEquipment(): EquipmentItem {
  return { type: "exhaust_fan", brand: "", model: "", specs: "", quantity: 1 };
}

interface CameraFormItem {
  id?: string; // present if existing camera
  label: string;
  url: string;
  is_primary: boolean;
}

function emptyCamera(): CameraFormItem {
  return { label: "Camera", url: "", is_primary: false };
}

function equipmentLabel(type: string) {
  return EQUIPMENT_TYPES.find((t) => t.value === type)?.label ?? type;
}

export default function TentsPage() {
  const router = useRouter();
  const confirm = useConfirm();
  const { data: rawTents, isLoading: pageLoading, mutate } = useApiSWR(
    ["tents"],
    (token) => listTents(token),
  );
  const tents = rawTents ?? [];
  const refresh = mutate;
  const [modal, setModal] = useState<ModalState>({ type: "closed" });
  const [name, setName] = useState("");
  const [envType, setEnvType] = useState("indoor");
  const [size, setSize] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [zipCode, setZipCode] = useState("");
  const [zipLoading, setZipLoading] = useState(false);
  const [cameras, setCameras] = useState<CameraFormItem[]>([]);
  const [existingCameraIds, setExistingCameraIds] = useState<string[]>([]);
  const [equipment, setEquipment] = useState<EquipmentItem[]>([]);
  const [notes, setNotes] = useState("");

  function openCreate() {
    setName("");
    setEnvType("indoor");
    setSize("");
    setLatitude("");
    setLongitude("");
    setZipCode("");
    setCameras([]);
    setExistingCameraIds([]);
    setEquipment([]);
    setNotes("");
    setError("");
    setModal({ type: "create" });
  }

  function openEdit(tent: TentResponse) {
    setName(tent.name);
    setEnvType(tent.environment_type);
    setSize(tent.size ?? "");
    setLatitude(tent.latitude?.toString() ?? "");
    setLongitude(tent.longitude?.toString() ?? "");
    setZipCode("");
    setEquipment((tent.equipment ?? []).map((e) => ({ ...e, quantity: e.quantity ?? 1 })));
    setNotes(tent.notes ?? "");
    setError("");
    // Load existing cameras
    const token = getAccessToken();
    if (token) {
      listTentCameras(token, tent.id).then((cams) => {
        const items = cams.map((c) => ({ id: c.id, label: c.label, url: c.url, is_primary: c.is_primary }));
        setCameras(items);
        setExistingCameraIds(cams.map((c) => c.id));
      }).catch(() => {
        setCameras([]);
        setExistingCameraIds([]);
      });
    } else {
      setCameras([]);
      setExistingCameraIds([]);
    }
    setModal({ type: "edit", tent });
  }

  async function handleSave() {
    const token = getAccessToken();
    if (!token || !name.trim()) return;
    setLoading(true);
    setError("");
    const cleanEquipment = equipment.filter((e) => e.type);
    const validCameras = cameras.filter((c) => c.url.trim());
    try {
      let tentId: string;
      if (modal.type === "create") {
        const created = await createTent(token, {
          name: name.trim(),
          environment_type: envType,
          ...(size.trim() ? { size: size.trim() } : {}),
          ...(latitude ? { latitude: parseFloat(latitude) } : {}),
          ...(longitude ? { longitude: parseFloat(longitude) } : {}),
          equipment: cleanEquipment,
          ...(notes.trim() ? { notes: notes.trim() } : {}),
        });
        tentId = created.id;
      } else if (modal.type === "edit") {
        tentId = modal.tent.id;
        await updateTent(token, tentId, {
          name: name.trim(),
          environment_type: envType,
          size: size.trim() || null,
          ...(latitude ? { latitude: parseFloat(latitude) } : {}),
          ...(longitude ? { longitude: parseFloat(longitude) } : {}),
          equipment: cleanEquipment,
          notes: notes.trim() || null,
        });
      } else {
        return;
      }

      // Sync cameras: delete removed, update existing, create new
      const keptIds = validCameras.filter((c) => c.id).map((c) => c.id!);
      const toDelete = existingCameraIds.filter((id) => !keptIds.includes(id));
      await Promise.all(toDelete.map((id) => deleteTentCamera(token, tentId, id)));
      for (const cam of validCameras) {
        if (cam.id) {
          await updateTentCamera(token, tentId, cam.id, { label: cam.label, url: cam.url, is_primary: cam.is_primary });
        } else {
          await createTentCamera(token, tentId, { label: cam.label, url: cam.url, is_primary: cam.is_primary });
        }
      }

      setModal({ type: "closed" });
      toast.success(modal.type === "create" ? "Tent created" : "Tent updated");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    const ok = await confirm({ title: "Delete Tent", description: "This tent and its data will be permanently deleted.", confirmText: "Delete", variant: "destructive" });
    if (!ok) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteTent(token, id);
      toast.success("Tent deleted");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to delete tent");
    }
  }

  function handleAutoLocate() {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(pos.coords.latitude.toFixed(6));
        setLongitude(pos.coords.longitude.toFixed(6));
        setGeoLoading(false);
      },
      (err) => {
        setError(`Location access denied: ${err.message}`);
        setGeoLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }

  async function handleZipLookup() {
    const zip = zipCode.trim();
    if (!zip) return;
    setZipLoading(true);
    setError("");
    try {
      const res = await fetch(`https://api.zippopotam.us/us/${encodeURIComponent(zip)}`);
      if (!res.ok) throw new Error("Invalid zip code");
      const data = await res.json();
      const place = data.places?.[0];
      if (!place) throw new Error("No results for this zip code");
      setLatitude(parseFloat(place.latitude).toFixed(6));
      setLongitude(parseFloat(place.longitude).toFixed(6));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Zip lookup failed");
    } finally {
      setZipLoading(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Grow Spaces"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Grow Spaces" }]}
        actions={
          <Button size="sm" onClick={openCreate}>
            <Plus className="mr-1 size-4" />
            New Space
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        {error && modal.type === "closed" && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {pageLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-4">
                <Skeleton className="mb-2 h-5 w-32" />
                <Skeleton className="h-4 w-20" />
              </Card>
            ))}
          </div>
        ) : tents.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Warehouse className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No grow spaces yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Create your first indoor tent, outdoor plot, or greenhouse.
            </p>
            <Button className="mt-4" onClick={openCreate}>
              <Plus className="mr-1 size-4" />
              Create your first space
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tents.map((tent) => (
              <motion.div key={tent.id} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
              <Card className="p-4 transition-colors hover:border-primary/50 cursor-pointer" onClick={() => router.push(`/dashboard/tents/${tent.id}`)}>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium">{tent.name}</h3>
                    <div className="mt-1 flex flex-wrap items-center gap-1">
                      <Badge variant="secondary">{tent.environment_type}</Badge>
                      {tent.size && <Badge variant="outline">{tent.size}</Badge>}
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" onClick={(e: React.MouseEvent) => e.stopPropagation()} />}>
                      <MoreHorizontal className="size-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => openEdit(tent)}>
                        <Pencil className="mr-2 size-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleDelete(tent.id)}
                        className="text-destructive focus:text-destructive"
                      >
                        <Trash2 className="mr-2 size-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                {(tent.latitude || tent.longitude) && (
                  <p className="mt-3 flex items-center gap-1 text-xs text-muted-foreground">
                    <MapPin className="size-3" />
                    {tent.latitude?.toFixed(4)}, {tent.longitude?.toFixed(4)}
                  </p>
                )}
                {((tent.equipment && tent.equipment.length > 0) || tent.camera_url) && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {tent.camera_url && (
                      <Badge variant="outline" className="text-[10px] font-normal">
                        <Camera className="mr-0.5 size-2.5" /> Camera
                      </Badge>
                    )}
                    {tent.equipment?.map((e, i) => (
                      <Badge key={i} variant="outline" className="text-[10px] font-normal">
                        {e.quantity > 1 ? `${e.quantity}× ` : ""}{equipmentLabel(e.type)}{e.brand ? ` (${e.brand})` : ""}
                      </Badge>
                    ))}
                  </div>
                )}
              </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Create / Edit Sheet */}
      <Sheet open={modal.type !== "closed"} onOpenChange={(open) => !open && setModal({ type: "closed" })}>
        <SheetContent side="right" className="sm:max-w-lg w-full flex flex-col">
          <SheetHeader>
            <SheetTitle>
              {modal.type === "create" ? "New Grow Space" : "Edit Grow Space"}
            </SheetTitle>
            <SheetDescription>
              {modal.type === "create"
                ? "Set up a new growing environment."
                : "Update your grow space details."}
            </SheetDescription>
          </SheetHeader>
          {error && modal.type !== "closed" && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <div className="flex-1 overflow-y-auto -mx-6 px-6 space-y-6 pb-4">
            {/* --- Basics --- */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Basics</h4>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label className="text-xs">Name</Label>
                  <Input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Veg Tent, Flower Room"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Environment</Label>
                  <Select value={envType} onValueChange={(v) => setEnvType(v ?? "indoor")}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {ENV_TYPES.map((t) => (
                        <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Size</Label>
                  <Select value={size || "__custom__"} onValueChange={(v) => setSize(!v || v === "__custom__" ? "" : v)}>
                    <SelectTrigger><SelectValue placeholder="Select size" /></SelectTrigger>
                    <SelectContent>
                      {TENT_SIZES.map((s) => (
                        <SelectItem key={s} value={s}>{s}</SelectItem>
                      ))}
                      <SelectItem value="__custom__">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                  {(!size || !TENT_SIZES.includes(size)) && (
                    <Input
                      className="mt-1"
                      value={size}
                      onChange={(e) => setSize(e.target.value)}
                      placeholder="e.g. 4x4x8, 6x3"
                    />
                  )}
                </div>
                <div className="space-y-1 sm:col-span-2">
                  <Label className="text-xs">Notes (optional)</Label>
                  <Textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Any extra details about this grow space..."
                    rows={2}
                    className="text-xs"
                  />
                </div>
              </div>
            </div>

            {/* --- Location --- */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Location</h4>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleAutoLocate}
                  disabled={geoLoading}
                  className="h-6 gap-1 text-xs"
                >
                  {geoLoading ? <Loader2 className="size-3 animate-spin" /> : <LocateFixed className="size-3" />}
                  {geoLoading ? "Locating…" : "Auto-detect"}
                </Button>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Zip Code</Label>
                  <div className="flex gap-1">
                    <Input
                      placeholder="e.g. 90210"
                      value={zipCode}
                      onChange={(e) => setZipCode(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleZipLookup())}
                    />
                    <Button type="button" variant="outline" size="icon" className="shrink-0" onClick={handleZipLookup} disabled={zipLoading || !zipCode.trim()}>
                      {zipLoading ? <Loader2 className="size-3.5 animate-spin" /> : <Search className="size-3.5" />}
                    </Button>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Latitude</Label>
                  <Input type="number" step="any" value={latitude} onChange={(e) => setLatitude(e.target.value)} placeholder="34.0522" />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Longitude</Label>
                  <Input type="number" step="any" value={longitude} onChange={(e) => setLongitude(e.target.value)} placeholder="-118.2437" />
                </div>
              </div>
            </div>

            {/* --- Equipment --- */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <Fan className="inline size-3 mr-1" />Equipment & Cameras
                </h4>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => setEquipment((prev) => [...prev, emptyEquipment()])}
                >
                  <Plus className="mr-1 size-3" /> Equipment
                </Button>
              </div>
              {/* Cameras */}
              <div className="space-y-2 mb-3">
                <div className="flex items-center justify-between">
                  <Label className="text-xs"><Camera className="inline size-3 mr-1" />Cameras</Label>
                  <Button type="button" variant="ghost" size="sm" className="h-6 text-xs" onClick={() => setCameras((prev) => [...prev, emptyCamera()])}>
                    <Plus className="mr-1 size-3" /> Add Camera
                  </Button>
                </div>
                {cameras.length === 0 ? (
                  <p className="text-xs text-muted-foreground py-1">No cameras. Click Add Camera to connect a feed.</p>
                ) : (
                  <div className="space-y-2">
                    {cameras.map((cam, idx) => (
                      <div key={idx} className="rounded-lg border p-3 space-y-2 relative">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="absolute top-1 right-1 size-6"
                          onClick={() => setCameras((prev) => prev.filter((_, i) => i !== idx))}
                        >
                          <X className="size-3.5" />
                        </Button>
                        <div className="grid gap-2 sm:grid-cols-2 pr-6">
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">Label</Label>
                            <Input className="h-8 text-xs" value={cam.label} onChange={(e) => setCameras((prev) => prev.map((c, i) => i === idx ? { ...c, label: e.target.value } : c))} placeholder="e.g. Top-down, Side view" />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">URL</Label>
                            <Input className="h-8 text-xs" value={cam.url} onChange={(e) => setCameras((prev) => prev.map((c, i) => i === idx ? { ...c, url: e.target.value } : c))} placeholder="http://192.168.1.50/snap" />
                          </div>
                        </div>
                        <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer">
                          <input
                            type="checkbox"
                            checked={cam.is_primary}
                            onChange={(e) => setCameras((prev) => prev.map((c, i) => i === idx ? { ...c, is_primary: e.target.checked } : c))}
                            className="size-3.5 rounded"
                          />
                          Primary camera
                        </label>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {equipment.length === 0 ? (
                <p className="text-xs text-muted-foreground py-2">No equipment added yet. Click Add to configure fans, filters, humidity control, etc.</p>
              ) : (
                <div className="space-y-3">
                  {equipment.map((item, idx) => (
                    <div key={idx} className="rounded-lg border p-3 space-y-2 relative">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute top-1 right-1 size-6"
                        onClick={() => setEquipment((prev) => prev.filter((_, i) => i !== idx))}
                      >
                        <X className="size-3.5" />
                      </Button>
                      <div className="grid gap-2 sm:grid-cols-2 pr-6">
                        {/* Type */}
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Type</Label>
                          <Select
                            value={item.type}
                            onValueChange={(v) => { if (v) setEquipment((prev) => prev.map((e, i) => i === idx ? { ...e, type: v } : e)); }}
                          >
                            <SelectTrigger className="h-8 text-xs"><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {EQUIPMENT_TYPES.map((t) => (
                                <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        {/* Brand */}
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Brand</Label>
                          {BRAND_SUGGESTIONS[item.type] ? (
                            <Select
                              value={item.brand && BRAND_SUGGESTIONS[item.type]?.includes(item.brand) ? item.brand : "__custom__"}
                              onValueChange={(v) => setEquipment((prev) => prev.map((e, i) => i === idx ? { ...e, brand: !v || v === "__custom__" ? "" : v } : e))}
                            >
                              <SelectTrigger className="h-8 text-xs"><SelectValue placeholder="Select brand" /></SelectTrigger>
                              <SelectContent>
                                {BRAND_SUGGESTIONS[item.type]!.map((b) => (
                                  <SelectItem key={b} value={b}>{b}</SelectItem>
                                ))}
                                <SelectItem value="__custom__">Other…</SelectItem>
                              </SelectContent>
                            </Select>
                          ) : (
                            <Input className="h-8 text-xs" value={item.brand ?? ""} onChange={(e) => setEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, brand: e.target.value } : eq))} placeholder="Brand name" />
                          )}
                          {BRAND_SUGGESTIONS[item.type] && item.brand !== undefined && !BRAND_SUGGESTIONS[item.type]?.includes(item.brand ?? "") && (
                            <Input className="h-8 text-xs mt-1" value={item.brand ?? ""} onChange={(e) => setEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, brand: e.target.value } : eq))} placeholder="Enter brand name" />
                          )}
                        </div>
                        {/* Model */}
                        <div className="space-y-1">
                          <Label className="text-[11px] text-muted-foreground">Model</Label>
                          <Input className="h-8 text-xs" value={item.model ?? ""} onChange={(e) => setEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, model: e.target.value } : eq))} placeholder="e.g. Cloudline T6" />
                        </div>
                        {/* Specs */}
                        <div className="grid grid-cols-[1fr_60px] gap-2">
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">Specs</Label>
                            <Input className="h-8 text-xs" value={item.specs ?? ""} onChange={(e) => setEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, specs: e.target.value } : eq))} placeholder="e.g. 402 CFM" />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-[11px] text-muted-foreground">Qty</Label>
                            <Input className="h-8 text-xs" type="number" min={1} max={20} value={item.quantity} onChange={(e) => setEquipment((prev) => prev.map((eq, i) => i === idx ? { ...eq, quantity: Math.max(1, parseInt(e.target.value) || 1) } : eq))} />
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
            <Button variant="outline" type="button" onClick={() => setModal({ type: "closed" })}>
              Cancel
            </Button>
            <Button type="button" onClick={handleSave} disabled={loading || !name.trim()}>
              {loading && <Loader2 className="mr-2 size-4 animate-spin" />}
              {loading ? "Saving…" : "Save"}
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </>
  );
}
