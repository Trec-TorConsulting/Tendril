"use client";

import { useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import { formatDate } from "@/lib/utils";
import {
  listGrowPhotos,
  uploadGrowPhoto,
  updateGrowPhoto,
  deleteGrowPhoto,
  growPhotoUrl,
  timelapseUrl,
  type GrowPhotoResponse,
  type BucketResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import { ImageIcon, Plus, Trash2, Pencil, Loader2, Upload, Camera, Film, Stethoscope, ScanSearch } from "lucide-react";
import { toast } from "sonner";
import { PhotoAIDialog } from "@/components/photo-ai-dialog";
import { VisionScanPanel } from "@/components/vision/vision-scan-panel";
import { useApiSWR } from "@/lib/swr";

/** Image component with retry logic for signed URLs. */
function RetryImage({ url, alt, className, maxRetries = 3 }: { url: string; alt: string; className?: string; maxRetries?: number }) {
  const [retries, setRetries] = useState(0);
  const [failed, setFailed] = useState(false);
  const [loaded, setLoaded] = useState(false);

  if (!url || failed) return <div className={`${className} bg-muted flex items-center justify-center`}><ImageIcon className="size-6 text-muted-foreground/40" /></div>;

  return (
    <div className="relative">
      {!loaded && (
        <div className={`${className} absolute inset-0 bg-muted flex items-center justify-center`}>
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </div>
      )}
      <img
        src={url}
        alt={alt}
        className={className}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        onError={(e) => {
          if (retries < maxRetries) {
            setRetries((r) => r + 1);
            // Force re-fetch by appending a cache-buster
            const target = e.currentTarget;
            const sep = url.includes("?") ? "&" : "?";
            target.src = `${url}${sep}_r=${retries + 1}`;
          } else {
            setFailed(true);
          }
        }}
      />
    </div>
  );
}

interface PhotosTabProps {
  growId: string;
  buckets: BucketResponse[];
}

export function PhotosTab({ growId, buckets }: PhotosTabProps) {
  const {
    data: rawPhotos,
    isLoading: loading,
    mutate,
  } = useApiSWR(["grow", "photos", growId], (token) => listGrowPhotos(token, growId));
  const photos: GrowPhotoResponse[] = rawPhotos ?? [];
  const [addDialog, setAddDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [addForm, setAddForm] = useState({ bucket_id: "", caption: "" });
  const [saving, setSaving] = useState(false);
  const [viewPhoto, setViewPhoto] = useState<GrowPhotoResponse | null>(null);
  const [editCaption, setEditCaption] = useState("");
  const [editSaving, setEditSaving] = useState(false);
  const [photoScanMode, setPhotoScanMode] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [timelapseDialog, setTimelapseDialog] = useState(false);
  const [aiDialog, setAiDialog] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const bucketLabelMap: Record<string, string> = {};
  buckets.forEach((b) => { bucketLabelMap[b.id] = `#${b.position} ${b.label || "Unnamed"}`; });

  const loadPhotos = mutate;

  // Clean up object URLs on unmount
  useEffect(() => {
    return () => { if (previewUrl) URL.revokeObjectURL(previewUrl); };
  }, [previewUrl]);

  const handleFileSelect = (file: File) => {
    if (!file.type.match(/^image\/(jpeg|png|webp)$/)) {
      alert("Only JPEG, PNG, and WebP images are allowed");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert("Image must be under 10 MB");
      return;
    }
    setSelectedFile(file);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const objectUrl = URL.createObjectURL(file);
    // Only allow blob: URLs to prevent injection via crafted URLs
    setPreviewUrl(objectUrl.startsWith("blob:") ? objectUrl : "");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleAdd = async () => {
    const token = getAccessToken();
    if (!token || !selectedFile) return;
    setSaving(true);
    try {
      await uploadGrowPhoto(
        token,
        selectedFile,
        growId,
        addForm.bucket_id || undefined,
        addForm.caption.trim() || undefined,
      );
      setAddDialog(false);
      resetAddForm();
      loadPhotos();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Upload failed");
    } finally { setSaving(false); }
  };

  const resetAddForm = () => {
    setSelectedFile(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl("");
    setAddForm({ bucket_id: "", caption: "" });
  };

  const handleUpdateCaption = async () => {
    if (!viewPhoto) return;
    const token = getAccessToken();
    if (!token) return;
    setEditSaving(true);
    try {
      await updateGrowPhoto(token, viewPhoto.id, { caption: editCaption.trim() });
      setViewPhoto(null);
      loadPhotos();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to update caption"); } finally { setEditSaving(false); }
  };

  const confirm = useConfirm();

  const handleDelete = async (photoId: string) => {
    if (!await confirm({ title: "Delete Photo", description: "Delete this photo?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteGrowPhoto(token, photoId);
      if (viewPhoto?.id === photoId) setViewPhoto(null);
      loadPhotos();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete photo"); }
  };

  const getImageSrc = (photo: GrowPhotoResponse) => {
    if (photo.url) return photo.url;
    // Fallback for photos without signed URL (e.g. freshly uploaded before list refresh)
    const token = getAccessToken();
    if (!token) return "";
    return growPhotoUrl(token, photo.id);
  };

  const snapshotCount = photos.filter((p) => p.source === "health_check").length;
  const hasTimelapse = snapshotCount >= 2;

  const getTimelapseSrc = () => {
    const token = getAccessToken();
    if (!token) return "";
    return timelapseUrl(token, growId);
  };

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Photo Gallery ({photos.length})</h3>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={() => setAiDialog(true)}>
            <Stethoscope className="mr-1 size-3" /> AI Analysis
          </Button>
          {hasTimelapse && (
            <Button size="sm" variant="outline" onClick={() => setTimelapseDialog(true)}>
              <Film className="mr-1 size-3" /> Timelapse
            </Button>
          )}
          <Button size="sm" onClick={() => { resetAddForm(); setAddDialog(true); }}>
            <Plus className="mr-1 size-3" /> Add Photo
          </Button>
        </div>
      </div>

      {/* Timelapse Preview */}
      {hasTimelapse && !loading && (
        <Card className="mb-4 overflow-hidden">
          <CardContent className="p-3">
            <button
              type="button"
              className="flex w-full items-center gap-3 text-left"
              onClick={() => setTimelapseDialog(true)}
            >
              <div className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <Film className="size-5 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">Grow Timelapse</p>
                <p className="text-xs text-muted-foreground">
                  {snapshotCount} health-check snapshots — click to view animated timelapse
                </p>
              </div>
            </button>
          </CardContent>
        </Card>
      )}

      {loading ? (
        <Card className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Loading photos...</p>
        </Card>
      ) : photos.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <ImageIcon className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No photos yet</p>
          <p className="text-xs text-muted-foreground">Upload photos or run health checks with camera to build your gallery</p>
        </Card>
      ) : (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {photos.map((p) => (
            <Card key={p.id} className="overflow-hidden cursor-pointer group" onClick={() => { setViewPhoto(p); setEditCaption(p.caption || ""); }}>
              <div className="aspect-square bg-muted relative">
                <RetryImage url={getImageSrc(p)} alt={p.caption || "Photo"} className="size-full object-cover" />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
                {p.source === "health_check" && (
                  <Badge variant="secondary" className="absolute top-1.5 right-1.5 text-[10px] gap-1">
                    <Camera className="size-2.5" /> Health Check
                  </Badge>
                )}
              </div>
              <CardContent className="p-2">
                {p.bucket_id && <p className="text-xs text-muted-foreground truncate">{bucketLabelMap[p.bucket_id] || "Bucket"}</p>}
                {p.caption && <p className="text-xs truncate">{p.caption}</p>}
                <p className="text-xs text-muted-foreground">{formatDate(p.created_at)}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Photo Dialog */}
      <Dialog open={addDialog} onOpenChange={(open) => { if (!open) { setAddDialog(false); resetAddForm(); } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Photo</DialogTitle>
            <DialogDescription>Add a photo of your grow</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            {/* Drop zone / file picker */}
            <div
              className={`relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-6 transition-colors cursor-pointer ${
                dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"
              }`}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); }}
              />
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="max-h-48 w-full rounded object-contain" />
              ) : (
                <>
                  <Upload className="size-8 text-muted-foreground/50" />
                  <p className="mt-2 text-sm text-muted-foreground">Drop an image here or click to browse</p>
                  <p className="text-xs text-muted-foreground">JPEG, PNG, WebP — max 10 MB</p>
                </>
              )}
            </div>
            {selectedFile && (
              <p className="text-xs text-muted-foreground">{selectedFile.name} ({(selectedFile.size / 1024).toFixed(0)} KB)</p>
            )}
            {buckets.length > 0 && (
              <div className="space-y-1">
                <Label className="text-xs">Bucket (optional)</Label>
                <Select value={addForm.bucket_id} onValueChange={(v) => setAddForm((p) => ({ ...p, bucket_id: !v || v === "__none__" ? "" : v }))}>
                  <SelectTrigger><SelectValue placeholder="Whole grow" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="__none__">Whole grow</SelectItem>
                    {buckets.map((b) => <SelectItem key={b.id} value={b.id}>#{b.position} {b.label || "Unnamed"}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div className="space-y-1">
              <Label className="text-xs">Caption (optional)</Label>
              <Input placeholder="e.g. Day 14 - first pistils" value={addForm.caption} onChange={(e) => setAddForm((p) => ({ ...p, caption: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => { setAddDialog(false); resetAddForm(); }}>Cancel</Button>
            <Button type="button" onClick={handleAdd} disabled={saving || !selectedFile}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Upload
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View/Edit Photo Dialog */}
      <Dialog open={!!viewPhoto} onOpenChange={(open) => { if (!open) { setViewPhoto(null); setPhotoScanMode(false); } }}>
        <DialogContent className="max-w-2xl">
          {viewPhoto && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    {viewPhoto.source === "health_check" ? "Health Check Snapshot" : "Photo"}
                    {viewPhoto.source === "health_check" && (
                      <Badge variant="secondary" className="text-[10px] gap-1">
                        <Camera className="size-2.5" /> Auto
                      </Badge>
                    )}
                  </span>
                  <span className="text-xs text-muted-foreground font-normal">{formatDate(viewPhoto.created_at)}</span>
                </DialogTitle>
              </DialogHeader>
              <div className="rounded-lg overflow-hidden border">
                {photoScanMode ? (
                  <div className="p-3">
                    <VisionScanPanel source="photo" sourceId={viewPhoto.id} imageSrc={getImageSrc(viewPhoto)} />
                  </div>
                ) : (
                  <RetryImage url={getImageSrc(viewPhoto)} alt={viewPhoto.caption || "Photo"} className="w-full max-h-[60vh] object-contain bg-muted" />
                )}
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1 space-y-1">
                  <Label className="text-xs">Caption</Label>
                  <Input value={editCaption} onChange={(e) => setEditCaption(e.target.value)} placeholder="Add a caption..." />
                </div>
                <Button
                  size="sm"
                  variant={photoScanMode ? "secondary" : "outline"}
                  onClick={() => setPhotoScanMode((s) => !s)}
                  aria-label="Scan for issues"
                >
                  <ScanSearch className="size-4" />
                </Button>
                <Button size="sm" onClick={handleUpdateCaption} disabled={editSaving}>
                  {editSaving ? <Loader2 className="size-4 animate-spin" /> : <Pencil className="size-4" />}
                </Button>
                <Button size="sm" variant="destructive" onClick={() => handleDelete(viewPhoto.id)}>
                  <Trash2 className="size-4" />
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Timelapse Dialog */}
      <Dialog open={timelapseDialog} onOpenChange={(open) => !open && setTimelapseDialog(false)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Film className="size-4" /> Grow Timelapse
            </DialogTitle>
            <DialogDescription>
              Animated timelapse from {snapshotCount} health-check camera snapshots
            </DialogDescription>
          </DialogHeader>
          <div className="rounded-lg overflow-hidden border bg-black">
            <RetryImage
              url={getTimelapseSrc()}
              alt="Grow timelapse"
              className="w-full object-contain"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Snapshots are captured every 12 hours during scheduled health checks.
            The timelapse will grow as more snapshots are collected.
          </p>
        </DialogContent>
      </Dialog>

      {/* AI Analysis Dialog */}
      <PhotoAIDialog
        open={aiDialog}
        onOpenChange={setAiDialog}
        growId={growId}
        onPhotoSaved={loadPhotos}
      />
    </>
  );
}
