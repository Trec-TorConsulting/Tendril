"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import { fireCannons } from "@/lib/confetti";
import { formatCalendarDate } from "@/lib/utils";
import {
  listYields,
  createYield,
  updateYield,
  deleteYield,
  type YieldResponse,
  type BucketResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
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
import { Wheat, Plus, Trash2, Pencil, Loader2, Star } from "lucide-react";

interface HarvestTabProps {
  growId: string;
  buckets: BucketResponse[];
}

export function HarvestTab({ growId, buckets }: HarvestTabProps) {
  const [yields, setYields] = useState<YieldResponse[]>([]);
  const [dialog, setDialog] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState({
    bucket_id: "",
    wet_weight_g: "",
    dry_weight_g: "",
    trim_weight_g: "",
    quality_rating: "",
    terpene_notes: "",
    harvest_date: "",
    dry_start: "",
    dry_end: "",
    cure_start: "",
    cure_end: "",
    notes: "",
  });
  const [saving, setSaving] = useState(false);

  const bucketLabelMap: Record<string, string> = {};
  buckets.forEach((b) => { bucketLabelMap[b.id] = `#${b.position} ${b.label || "Unnamed"}`; });

  const loadYields = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const allYields: YieldResponse[] = [];
    await Promise.all(buckets.map(async (b) => {
      try {
        const y = await listYields(token, b.id);
        allYields.push(...y);
      } catch { /* empty */ }
    }));
    allYields.sort((a, b) => new Date(b.harvest_date || "").getTime() - new Date(a.harvest_date || "").getTime());
    setYields(allYields);
  }, [buckets]);

  useEffect(() => { loadYields(); }, [loadYields]);

  const handleSubmit = async () => {
    const token = getAccessToken();
    if (!token || (!editId && !form.bucket_id)) return;
    setSaving(true);
    try {
      const data: Record<string, unknown> = {};
      if (form.wet_weight_g) data.wet_weight_g = parseFloat(form.wet_weight_g);
      if (form.dry_weight_g) data.dry_weight_g = parseFloat(form.dry_weight_g);
      if (form.trim_weight_g) data.trim_weight_g = parseFloat(form.trim_weight_g);
      if (form.quality_rating) data.quality_rating = parseInt(form.quality_rating);
      if (form.terpene_notes) data.terpene_notes = form.terpene_notes.trim();
      if (form.harvest_date) data.harvest_date = new Date(form.harvest_date).toISOString();
      if (form.dry_start) data.dry_start = new Date(form.dry_start).toISOString();
      if (form.dry_end) data.dry_end = new Date(form.dry_end).toISOString();
      if (form.cure_start) data.cure_start = new Date(form.cure_start).toISOString();
      if (form.cure_end) data.cure_end = new Date(form.cure_end).toISOString();
      if (form.notes) data.notes = form.notes.trim();

      if (editId) {
        await updateYield(token, editId, data as Parameters<typeof updateYield>[2]);
      } else {
        await createYield(token, { bucket_id: form.bucket_id, ...data } as Parameters<typeof createYield>[1]);
        fireCannons();
      }
      setDialog(false);
      setEditId(null);
      resetForm();
      loadYields();
    } catch { /* empty */ } finally { setSaving(false); }
  };

  const confirm = useConfirm();

  const handleDelete = async (yieldId: string) => {
    if (!await confirm({ title: "Delete Harvest", description: "Delete this harvest record?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteYield(token, yieldId);
    loadYields();
  };

  const resetForm = () => setForm({
    bucket_id: "", wet_weight_g: "", dry_weight_g: "", trim_weight_g: "",
    quality_rating: "", terpene_notes: "", harvest_date: "", dry_start: "",
    dry_end: "", cure_start: "", cure_end: "", notes: "",
  });

  // Totals
  const totalWet = yields.reduce((s, y) => s + (y.wet_weight_g || 0), 0);
  const totalDry = yields.reduce((s, y) => s + (y.dry_weight_g || 0), 0);
  const totalTrim = yields.reduce((s, y) => s + (y.trim_weight_g || 0), 0);
  const avgQuality = yields.filter((y) => y.quality_rating).length > 0
    ? (yields.reduce((s, y) => s + (y.quality_rating || 0), 0) / yields.filter((y) => y.quality_rating).length)
    : null;

  return (
    <>
      {/* Summary */}
      {yields.length > 0 && (
        <div className="mb-4 grid gap-3 sm:grid-cols-4">
          <Card><CardContent className="p-3 text-center"><p className="text-xs text-muted-foreground">Total Wet</p><p className="text-lg font-bold">{totalWet.toFixed(0)}g</p></CardContent></Card>
          <Card><CardContent className="p-3 text-center"><p className="text-xs text-muted-foreground">Total Dry</p><p className="text-lg font-bold">{totalDry.toFixed(0)}g</p></CardContent></Card>
          <Card><CardContent className="p-3 text-center"><p className="text-xs text-muted-foreground">Total Trim</p><p className="text-lg font-bold">{totalTrim.toFixed(0)}g</p></CardContent></Card>
          <Card><CardContent className="p-3 text-center"><p className="text-xs text-muted-foreground">Avg Quality</p><p className="text-lg font-bold">{avgQuality ? `${avgQuality.toFixed(1)}/10` : "—"}</p></CardContent></Card>
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Harvest Records</h3>
        <Button size="sm" onClick={() => { resetForm(); setEditId(null); setForm((p) => ({ ...p, bucket_id: buckets[0]?.id || "" })); setDialog(true); }} disabled={buckets.length === 0}>
          <Plus className="mr-1 size-3" /> Log Harvest
        </Button>
      </div>

      {yields.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <Wheat className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No harvests logged yet</p>
          <p className="text-xs text-muted-foreground">Record yields when you harvest each bucket</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {yields.map((y) => (
            <Card key={y.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{bucketLabelMap[y.bucket_id] || "Unknown"}</span>
                      {y.harvest_date && <span className="text-xs text-muted-foreground">{formatCalendarDate(y.harvest_date)}</span>}
                      {y.quality_rating && (
                        <Badge variant="outline" className="text-xs">
                          <Star className="mr-0.5 size-3" />{y.quality_rating}/10
                        </Badge>
                      )}
                    </div>
                    <div className="mt-2 grid grid-cols-3 gap-3 text-sm">
                      {y.wet_weight_g != null && <div><span className="text-xs text-muted-foreground">Wet</span><p className="font-medium">{y.wet_weight_g}g</p></div>}
                      {y.dry_weight_g != null && <div><span className="text-xs text-muted-foreground">Dry</span><p className="font-medium">{y.dry_weight_g}g</p></div>}
                      {y.trim_weight_g != null && <div><span className="text-xs text-muted-foreground">Trim</span><p className="font-medium">{y.trim_weight_g}g</p></div>}
                    </div>
                    {/* Drying/curing dates */}
                    {(y.dry_start || y.cure_start) && (
                      <div className="mt-2 flex flex-wrap gap-x-4 text-xs text-muted-foreground">
                        {y.dry_start && <span>Dry: {formatCalendarDate(y.dry_start)}{y.dry_end ? ` – ${formatCalendarDate(y.dry_end)}` : " (ongoing)"}</span>}
                        {y.cure_start && <span>Cure: {formatCalendarDate(y.cure_start)}{y.cure_end ? ` – ${formatCalendarDate(y.cure_end)}` : " (ongoing)"}</span>}
                      </div>
                    )}
                    {y.terpene_notes && <p className="mt-1 text-xs text-muted-foreground">Terpenes: {y.terpene_notes}</p>}
                    {y.notes && <p className="mt-1 text-xs italic text-muted-foreground">{y.notes}</p>}
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => {
                      setEditId(y.id);
                      setForm({
                        bucket_id: y.bucket_id,
                        wet_weight_g: y.wet_weight_g?.toString() || "",
                        dry_weight_g: y.dry_weight_g?.toString() || "",
                        trim_weight_g: y.trim_weight_g?.toString() || "",
                        quality_rating: y.quality_rating?.toString() || "",
                        terpene_notes: y.terpene_notes || "",
                        harvest_date: y.harvest_date ? new Date(y.harvest_date).toISOString().slice(0, 10) : "",
                        dry_start: y.dry_start ? new Date(y.dry_start).toISOString().slice(0, 10) : "",
                        dry_end: y.dry_end ? new Date(y.dry_end).toISOString().slice(0, 10) : "",
                        cure_start: y.cure_start ? new Date(y.cure_start).toISOString().slice(0, 10) : "",
                        cure_end: y.cure_end ? new Date(y.cure_end).toISOString().slice(0, 10) : "",
                        notes: y.notes || "",
                      });
                      setDialog(true);
                    }}>
                      <Pencil className="size-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={() => handleDelete(y.id)}>
                      <Trash2 className="size-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Harvest Dialog (Add/Edit) */}
      <Dialog open={dialog} onOpenChange={(open) => !open && setDialog(false)}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editId ? "Edit" : "Log"} Harvest</DialogTitle>
            <DialogDescription>Record harvest weights, quality, and drying/curing dates</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {!editId && (
              <div className="space-y-1">
                <Label className="text-xs">Bucket</Label>
                <Select value={form.bucket_id} onValueChange={(v) => setForm((p) => ({ ...p, bucket_id: v ?? "" }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {buckets.map((b) => <SelectItem key={b.id} value={b.id}>#{b.position} {b.label || "Unnamed"}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Harvest Date</Label>
                <Input type="date" value={form.harvest_date} onChange={(e) => setForm((p) => ({ ...p, harvest_date: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Quality (1-10)</Label>
                <Input type="number" min="1" max="10" value={form.quality_rating} onChange={(e) => setForm((p) => ({ ...p, quality_rating: e.target.value }))} />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Wet Weight (g)</Label>
                <Input type="number" step="0.1" value={form.wet_weight_g} onChange={(e) => setForm((p) => ({ ...p, wet_weight_g: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Dry Weight (g)</Label>
                <Input type="number" step="0.1" value={form.dry_weight_g} onChange={(e) => setForm((p) => ({ ...p, dry_weight_g: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Trim Weight (g)</Label>
                <Input type="number" step="0.1" value={form.trim_weight_g} onChange={(e) => setForm((p) => ({ ...p, trim_weight_g: e.target.value }))} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Dry Start</Label>
                <Input type="date" value={form.dry_start} onChange={(e) => setForm((p) => ({ ...p, dry_start: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Dry End</Label>
                <Input type="date" value={form.dry_end} onChange={(e) => setForm((p) => ({ ...p, dry_end: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Cure Start</Label>
                <Input type="date" value={form.cure_start} onChange={(e) => setForm((p) => ({ ...p, cure_start: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Cure End</Label>
                <Input type="date" value={form.cure_end} onChange={(e) => setForm((p) => ({ ...p, cure_end: e.target.value }))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Terpene Notes</Label>
              <Input placeholder="e.g. Citrus, earthy, pine" value={form.terpene_notes} onChange={(e) => setForm((p) => ({ ...p, terpene_notes: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Textarea rows={2} placeholder="Additional notes..." value={form.notes} onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleSubmit} disabled={saving || (!editId && !form.bucket_id)}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editId ? "Update" : "Save"} Harvest
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
