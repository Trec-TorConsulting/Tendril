"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listPhotos,
  createPhoto,
  updatePhoto,
  deletePhoto,
  type PhotoResponse,
  type BucketResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
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
import { ImageIcon, Plus, Trash2, Pencil, Loader2, X } from "lucide-react";

interface PhotosTabProps {
  buckets: BucketResponse[];
}

export function PhotosTab({ buckets }: PhotosTabProps) {
  const [photos, setPhotos] = useState<PhotoResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [addDialog, setAddDialog] = useState(false);
  const [addForm, setAddForm] = useState({ bucket_id: "", url: "", caption: "" });
  const [saving, setSaving] = useState(false);
  const [viewPhoto, setViewPhoto] = useState<PhotoResponse | null>(null);
  const [editCaption, setEditCaption] = useState("");
  const [editSaving, setEditSaving] = useState(false);

  const bucketLabelMap: Record<string, string> = {};
  buckets.forEach((b) => { bucketLabelMap[b.id] = `#${b.position} ${b.label || "Unnamed"}`; });

  const loadPhotos = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    const allPhotos: PhotoResponse[] = [];
    await Promise.all(buckets.map(async (b) => {
      try {
        const p = await listPhotos(token, b.id);
        allPhotos.push(...p);
      } catch { /* empty */ }
    }));
    allPhotos.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    setPhotos(allPhotos);
    setLoading(false);
  }, [buckets]);

  useEffect(() => { loadPhotos(); }, [loadPhotos]);

  const handleAdd = async () => {
    const token = getAccessToken();
    if (!token || !addForm.bucket_id || !addForm.url.trim()) return;
    setSaving(true);
    try {
      await createPhoto(token, {
        bucket_id: addForm.bucket_id,
        url: addForm.url.trim(),
        caption: addForm.caption.trim() || undefined,
      });
      setAddDialog(false);
      setAddForm({ bucket_id: "", url: "", caption: "" });
      loadPhotos();
    } catch { /* empty */ } finally { setSaving(false); }
  };

  const handleUpdateCaption = async () => {
    if (!viewPhoto) return;
    const token = getAccessToken();
    if (!token) return;
    setEditSaving(true);
    try {
      await updatePhoto(token, viewPhoto.id, { caption: editCaption.trim() });
      setViewPhoto(null);
      loadPhotos();
    } catch { /* empty */ } finally { setEditSaving(false); }
  };

  const handleDelete = async (photoId: string) => {
    if (!confirm("Delete this photo?")) return;
    const token = getAccessToken();
    if (!token) return;
    await deletePhoto(token, photoId);
    if (viewPhoto?.id === photoId) setViewPhoto(null);
    loadPhotos();
  };

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Photo Gallery ({photos.length})</h3>
        <Button size="sm" onClick={() => {
          setAddForm({ bucket_id: buckets[0]?.id || "", url: "", caption: "" });
          setAddDialog(true);
        }} disabled={buckets.length === 0}>
          <Plus className="mr-1 size-3" /> Add Photo
        </Button>
      </div>

      {loading ? (
        <Card className="flex items-center justify-center py-12">
          <p className="text-sm text-muted-foreground">Loading photos...</p>
        </Card>
      ) : photos.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <ImageIcon className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No photos yet</p>
          <p className="text-xs text-muted-foreground">Add photo URLs to track your grow visually</p>
        </Card>
      ) : (
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {photos.map((p) => (
            <Card key={p.id} className="overflow-hidden cursor-pointer group" onClick={() => { setViewPhoto(p); setEditCaption(p.caption || ""); }}>
              <div className="aspect-square bg-muted relative">
                <img src={p.url} alt={p.caption || "Photo"} className="size-full object-cover" loading="lazy" />
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
              </div>
              <CardContent className="p-2">
                <p className="text-xs text-muted-foreground truncate">{bucketLabelMap[p.bucket_id] || "Unknown"}</p>
                {p.caption && <p className="text-xs truncate">{p.caption}</p>}
                <p className="text-xs text-muted-foreground">{new Date(p.created_at).toLocaleDateString()}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Photo Dialog */}
      <Dialog open={addDialog} onOpenChange={(open) => !open && setAddDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Photo</DialogTitle>
            <DialogDescription>Provide a URL to an image of your grow</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Bucket</Label>
              <Select value={addForm.bucket_id} onValueChange={(v) => setAddForm((p) => ({ ...p, bucket_id: v ?? "" }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {buckets.map((b) => <SelectItem key={b.id} value={b.id}>#{b.position} {b.label || "Unnamed"}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Image URL</Label>
              <Input placeholder="https://..." value={addForm.url} onChange={(e) => setAddForm((p) => ({ ...p, url: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Caption (optional)</Label>
              <Input placeholder="e.g. Day 14 - first pistils" value={addForm.caption} onChange={(e) => setAddForm((p) => ({ ...p, caption: e.target.value }))} />
            </div>
            {addForm.url && (
              <div className="rounded-lg border overflow-hidden">
                <img src={addForm.url} alt="Preview" className="max-h-48 w-full object-contain bg-muted" />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setAddDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleAdd} disabled={saving || !addForm.bucket_id || !addForm.url.trim()}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save Photo
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View/Edit Photo Dialog */}
      <Dialog open={!!viewPhoto} onOpenChange={(open) => !open && setViewPhoto(null)}>
        <DialogContent className="max-w-2xl">
          {viewPhoto && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>{bucketLabelMap[viewPhoto.bucket_id] || "Photo"}</span>
                  <span className="text-xs text-muted-foreground font-normal">{new Date(viewPhoto.created_at).toLocaleDateString()}</span>
                </DialogTitle>
              </DialogHeader>
              <div className="rounded-lg overflow-hidden border">
                <img src={viewPhoto.url} alt={viewPhoto.caption || "Photo"} className="w-full max-h-[60vh] object-contain bg-muted" />
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1 space-y-1">
                  <Label className="text-xs">Caption</Label>
                  <Input value={editCaption} onChange={(e) => setEditCaption(e.target.value)} placeholder="Add a caption..." />
                </div>
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
    </>
  );
}
