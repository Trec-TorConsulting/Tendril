"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listTents, createTent, updateTent, deleteTent } from "@/lib/api";
import type { TentResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, MoreHorizontal, Pencil, Trash2, MapPin, Warehouse, Loader2, LocateFixed, Search, Camera } from "lucide-react";

type ModalState =
  | { type: "closed" }
  | { type: "create" }
  | { type: "edit"; tent: TentResponse };

const ENV_TYPES = ["indoor", "outdoor", "greenhouse"];

export default function TentsPage() {
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [modal, setModal] = useState<ModalState>({ type: "closed" });
  const [name, setName] = useState("");
  const [envType, setEnvType] = useState("indoor");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [geoLoading, setGeoLoading] = useState(false);
  const [zipCode, setZipCode] = useState("");
  const [zipLoading, setZipLoading] = useState(false);
  const [cameraUrl, setCameraUrl] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setTents(await listTents(token));
    } catch {
      /* empty */
    } finally {
      setPageLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function openCreate() {
    setName("");
    setEnvType("indoor");
    setLatitude("");
    setLongitude("");
    setZipCode("");
    setCameraUrl("");
    setError("");
    setModal({ type: "create" });
  }

  function openEdit(tent: TentResponse) {
    setName(tent.name);
    setEnvType(tent.environment_type);
    setLatitude(tent.latitude?.toString() ?? "");
    setLongitude(tent.longitude?.toString() ?? "");
    setZipCode("");
    setCameraUrl(tent.camera_url ?? "");
    setError("");
    setModal({ type: "edit", tent });
  }

  async function handleSave() {
    const token = getAccessToken();
    if (!token || !name.trim()) return;
    setLoading(true);
    setError("");
    try {
      if (modal.type === "create") {
        await createTent(token, {
          name: name.trim(),
          environment_type: envType,
          ...(latitude ? { latitude: parseFloat(latitude) } : {}),
          ...(longitude ? { longitude: parseFloat(longitude) } : {}),
          ...(cameraUrl.trim() ? { camera_url: cameraUrl.trim() } : {}),
        });
      } else if (modal.type === "edit") {
        await updateTent(token, modal.tent.id, {
          name: name.trim(),
          environment_type: envType,
          ...(latitude ? { latitude: parseFloat(latitude) } : {}),
          ...(longitude ? { longitude: parseFloat(longitude) } : {}),
          camera_url: cameraUrl.trim() || null,
        });
      }
      setModal({ type: "closed" });
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteTent(token, id);
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to delete");
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
              <Card key={tent.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-medium">{tent.name}</h3>
                    <Badge variant="secondary" className="mt-1">
                      {tent.environment_type}
                    </Badge>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" />}>
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
                {tent.camera_url && (
                  <p className="mt-1 flex items-center gap-1 text-xs text-muted-foreground">
                    <Camera className="size-3" />
                    Camera linked
                  </p>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Create / Edit Dialog */}
      <Dialog open={modal.type !== "closed"} onOpenChange={(open) => !open && setModal({ type: "closed" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {modal.type === "create" ? "New Grow Space" : "Edit Grow Space"}
            </DialogTitle>
            <DialogDescription>
              {modal.type === "create"
                ? "Set up a new growing environment."
                : "Update your grow space details."}
            </DialogDescription>
          </DialogHeader>
          {error && modal.type !== "closed" && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Veg Tent, Flower Room"
              />
            </div>
            <div className="space-y-2">
              <Label>Environment</Label>
              <Select value={envType} onValueChange={(v) => setEnvType(v ?? "indoor")}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ENV_TYPES.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t.charAt(0).toUpperCase() + t.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Location (optional)</Label>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleAutoLocate}
                  disabled={geoLoading}
                  className="h-7 gap-1 text-xs"
                >
                  {geoLoading ? (
                    <Loader2 className="size-3 animate-spin" />
                  ) : (
                    <LocateFixed className="size-3" />
                  )}
                  {geoLoading ? "Locating…" : "Auto-detect"}
                </Button>
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1 space-y-1">
                  <Label className="text-xs text-muted-foreground">Zip Code</Label>
                  <Input
                    placeholder="e.g. 90210"
                    value={zipCode}
                    onChange={(e) => setZipCode(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleZipLookup())}
                  />
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleZipLookup}
                  disabled={zipLoading || !zipCode.trim()}
                  className="h-8"
                >
                  {zipLoading ? (
                    <Loader2 className="size-3.5 animate-spin" />
                  ) : (
                    <Search className="size-3.5" />
                  )}
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Latitude</Label>
                  <Input
                    type="number"
                    step="any"
                    value={latitude}
                    onChange={(e) => setLatitude(e.target.value)}
                    placeholder="e.g. 34.0522"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Longitude</Label>
                  <Input
                    type="number"
                    step="any"
                    value={longitude}
                    onChange={(e) => setLongitude(e.target.value)}
                    placeholder="e.g. -118.2437"
                  />
                </div>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Camera Stream URL (optional)</Label>
              <Input
                value={cameraUrl}
                onChange={(e) => setCameraUrl(e.target.value)}
                placeholder="e.g. http://192.168.1.50:8554/tent-cam"
              />
              <p className="text-xs text-muted-foreground">
                RTSP, MJPEG, or snapshot URL for visual health checks
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setModal({ type: "closed" })}>
              Cancel
            </Button>
            <Button type="button" onClick={handleSave} disabled={loading || !name.trim()}>
              {loading && <Loader2 className="mr-2 size-4 animate-spin" />}
              {loading ? "Saving…" : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
