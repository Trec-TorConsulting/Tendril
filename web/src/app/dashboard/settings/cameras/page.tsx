"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  listTents,
  listTentCameras,
  createTentCamera,
  updateTentCamera,
  deleteTentCamera,
  type TentResponse,
  type CameraResponse,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Camera, Plus, Pencil, Trash2, Star, Loader2 } from "lucide-react";
import { toast } from "sonner";

interface TentWithCameras {
  tent: TentResponse;
  cameras: CameraResponse[];
}

interface CameraFormData {
  label: string;
  url: string;
  camera_type: string;
  is_primary: boolean;
}

const CAMERA_TYPES = [
  { value: "rtsp", label: "RTSP Stream" },
  { value: "http", label: "HTTP Snapshot" },
  { value: "usb", label: "USB Camera" },
  { value: "esp32cam", label: "ESP32-CAM" },
  { value: "rpi", label: "Raspberry Pi Camera" },
  { value: "other", label: "Other" },
];

export default function CameraManagementPage() {
  const { data: rawData, isLoading: loading, mutate } = useApiSWR(
    ["cameras-management"],
    async (token) => {
      const tents = await listTents(token);
      const results: TentWithCameras[] = [];
      for (const tent of tents) {
        try {
          const cameras = await listTentCameras(token, tent.id);
          results.push({ tent, cameras });
        } catch {
          results.push({ tent, cameras: [] });
        }
      }
      return results;
    },
  );
  const tentsWithCameras = rawData ?? [];
  const loadData = mutate;
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCamera, setEditingCamera] = useState<{ tentId: string; camera?: CameraResponse } | null>(null);
  const [formData, setFormData] = useState<CameraFormData>({ label: "", url: "", camera_type: "http", is_primary: false });
  const [saving, setSaving] = useState(false);

  const openAddDialog = (tentId: string) => {
    setEditingCamera({ tentId });
    setFormData({ label: "", url: "", camera_type: "http", is_primary: false });
    setDialogOpen(true);
  };

  const openEditDialog = (tentId: string, camera: CameraResponse) => {
    setEditingCamera({ tentId, camera });
    setFormData({
      label: camera.label,
      url: camera.url,
      camera_type: camera.camera_type,
      is_primary: camera.is_primary,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!editingCamera || !formData.label || !formData.url) return;
    const token = getAccessToken();
    if (!token) return;

    setSaving(true);
    try {
      if (editingCamera.camera) {
        await updateTentCamera(token, editingCamera.tentId, editingCamera.camera.id, formData);
        toast.success("Camera updated");
      } else {
        await createTentCamera(token, editingCamera.tentId, formData);
        toast.success("Camera added");
      }
      setDialogOpen(false);
      await loadData();
    } catch {
      toast.error("Failed to save camera");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (tentId: string, cameraId: string) => {
    const token = getAccessToken();
    if (!token) return;

    try {
      await deleteTentCamera(token, tentId, cameraId);
      toast.success("Camera removed");
      await loadData();
    } catch {
      toast.error("Failed to delete camera");
    }
  };

  const handleSetPrimary = async (tentId: string, cameraId: string) => {
    const token = getAccessToken();
    if (!token) return;

    try {
      await updateTentCamera(token, tentId, cameraId, { is_primary: true });
      toast.success("Set as primary camera");
      await loadData();
    } catch {
      toast.error("Failed to update camera");
    }
  };

  if (loading) {
    return (
      <>
        <PageHeader title="Camera Management" />
        <div className="p-6 space-y-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader title="Camera Management" />
      <div className="p-6 space-y-6">
        {tentsWithCameras.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center py-12 gap-3">
              <Camera className="size-10 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No tents found. Create a tent first to add cameras.</p>
            </CardContent>
          </Card>
        ) : (
          tentsWithCameras.map(({ tent, cameras }) => (
            <Card key={tent.id}>
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-base">{tent.name}</CardTitle>
                <Button size="sm" variant="outline" className="gap-1.5" onClick={() => openAddDialog(tent.id)}>
                  <Plus className="size-3.5" />
                  Add Camera
                </Button>
              </CardHeader>
              <CardContent>
                {cameras.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">No cameras configured</p>
                ) : (
                  <div className="space-y-3">
                    {cameras.map((cam) => (
                      <div
                        key={cam.id}
                        className="flex items-center justify-between gap-3 rounded-lg border p-3"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <Camera className="size-4 shrink-0 text-muted-foreground" />
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-medium truncate">{cam.label}</p>
                              {cam.is_primary && <Badge variant="secondary" className="text-[10px]">Primary</Badge>}
                            </div>
                            <p className="text-xs text-muted-foreground truncate">{cam.url}</p>
                            <p className="text-[10px] text-muted-foreground capitalize">{cam.camera_type}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          {!cam.is_primary && (
                            <Button size="icon" variant="ghost" className="size-7" onClick={() => handleSetPrimary(tent.id, cam.id)} title="Set as primary">
                              <Star className="size-3.5" />
                            </Button>
                          )}
                          <Button size="icon" variant="ghost" className="size-7" onClick={() => openEditDialog(tent.id, cam)}>
                            <Pencil className="size-3.5" />
                          </Button>
                          <Button size="icon" variant="ghost" className="size-7 text-destructive" onClick={() => handleDelete(tent.id, cam.id)}>
                            <Trash2 className="size-3.5" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Add/Edit Camera Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCamera?.camera ? "Edit Camera" : "Add Camera"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Label</Label>
              <Input
                placeholder="e.g. Main Tent Overhead"
                value={formData.label}
                onChange={(e) => setFormData((f) => ({ ...f, label: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>URL / Address</Label>
              <Input
                placeholder="rtsp://192.168.1.100:554/stream or http://..."
                value={formData.url}
                onChange={(e) => setFormData((f) => ({ ...f, url: e.target.value }))}
              />
            </div>
            <div className="space-y-1.5">
              <Label>Camera Type</Label>
              <Select value={formData.camera_type} onValueChange={(v) => setFormData((f) => ({ ...f, camera_type: v }))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CAMERA_TYPES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} disabled={saving || !formData.label || !formData.url}>
              {saving && <Loader2 className="size-4 animate-spin mr-2" />}
              {editingCamera?.camera ? "Save" : "Add"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
