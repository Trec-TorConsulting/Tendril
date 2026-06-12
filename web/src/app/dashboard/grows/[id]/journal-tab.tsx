"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import { formatDate, formatTime } from "@/lib/utils";
import {
  createJournalEntry,
  createQuickJournalEntry,
  updateJournalEntry,
  deleteJournalEntry,
  listFeedingSchedules,
  type JournalEntryResponse,
  type BucketResponse,
  type FeedingScheduleResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
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
import { NotebookPen, Plus, Trash2, Pencil, Loader2 } from "lucide-react";
import { toast } from "sonner";

const EVENT_TYPES = ["note", "feeding", "water_change", "training", "transplant", "defoliation", "topping", "flushing", "other"];

interface JournalTabProps {
  growId: string;
  growType: string;
  buckets: BucketResponse[];
  journalEntries: JournalEntryResponse[];
  bucketLabelMap: Record<string, string>;
  onRefresh: () => void;
}

export function JournalTab({ growId, growType, buckets, journalEntries, bucketLabelMap, onRefresh }: JournalTabProps) {
  const [dialog, setDialog] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState({ bucket_id: "", event_type: "note", content: "", ph: "", ec: "", water_temp_f: "", volume_gal: "" });
  const [saving, setSaving] = useState(false);

  // Feeding schedule nutrients for the nutrient checklist
  const [scheduleNutrients, setScheduleNutrients] = useState<{ name: string; brand?: string; ml_per_gallon?: number }[]>([]);
  const [selectedNutrients, setSelectedNutrients] = useState<Set<string>>(new Set());

  // Load feeding schedule nutrients when dialog opens for water_change/feeding
  useEffect(() => {
    if (!dialog || editId) return;
    const token = getAccessToken();
    if (!token || !growId) return;
    listFeedingSchedules(token, growId).then((schedules) => {
      // Find the active schedule (matching current grow stage) or just use the first
      const allNutrients = schedules.flatMap((s) => s.nutrients || []);
      // Deduplicate by name
      const unique = Array.from(new Map(allNutrients.map((n) => [n.name, n])).values());
      setScheduleNutrients(unique);
      // Pre-select all by default
      setSelectedNutrients(new Set(unique.map((n) => n.name)));
    }).catch(() => {});
  }, [dialog, growId, editId]);

  const showMeasurements = !editId && (form.event_type === "water_change" || form.event_type === "feeding" || form.event_type === "flushing");

  const handleSubmit = async () => {
    const token = getAccessToken();
    if (!token || !form.bucket_id || !form.event_type) return;
    setSaving(true);
    try {
      if (editId) {
        await updateJournalEntry(token, editId, {
          event_type: form.event_type,
          content: form.content.trim() || undefined,
        });
      } else if (showMeasurements) {
        // Use the quick endpoint to save journal + sensor reading atomically
        const nutrientPayload = scheduleNutrients
          .filter((n) => selectedNutrients.has(n.name))
          .map((n) => ({ name: n.name, ml_per_gallon: n.ml_per_gallon }));
        await createQuickJournalEntry(token, {
          bucket_id: form.bucket_id,
          event_type: form.event_type,
          content: form.content.trim() || undefined,
          ph: form.ph ? parseFloat(form.ph) : undefined,
          ec: form.ec ? parseFloat(form.ec) : undefined,
          water_temp_f: form.water_temp_f ? parseFloat(form.water_temp_f) : undefined,
          volume_gallons: form.volume_gal ? parseFloat(form.volume_gal) : undefined,
          payload: nutrientPayload.length > 0 ? { nutrients: nutrientPayload, volume_gal: form.volume_gal ? parseFloat(form.volume_gal) : undefined } : undefined,
        });
      } else {
        await createJournalEntry(token, {
          bucket_id: form.bucket_id,
          event_type: form.event_type,
          content: form.content.trim() || undefined,
        });
      }
      setDialog(false);
      setEditId(null);
      setForm({ bucket_id: "", event_type: "note", content: "", ph: "", ec: "", water_temp_f: "", volume_gal: "" });
      onRefresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save journal entry"); } finally { setSaving(false); }
  };

  const confirm = useConfirm();

  const handleDelete = async (entryId: string) => {
    if (!await confirm({ title: "Delete Entry", description: "Delete this journal entry?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteJournalEntry(token, entryId);
      onRefresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete entry"); }
  };

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Grow Journal</h3>
        <Button size="sm" onClick={() => {
          setEditId(null);
          setForm({ bucket_id: buckets[0]?.id || "", event_type: "note", content: "", ph: "", ec: "", water_temp_f: "", volume_gal: "" });
          setDialog(true);
        }} disabled={buckets.length === 0}>
          <Plus className="mr-1 size-3" /> Add Entry
        </Button>
      </div>
      {journalEntries.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <NotebookPen className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No journal entries yet</p>
          <p className="text-xs text-muted-foreground">Track feedings, water changes, training, and notes</p>
        </Card>
      ) : (
        <div className="space-y-2">
          {journalEntries.map((je) => (
            <Card key={je.id}>
              <CardContent className="flex items-start justify-between p-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-xs capitalize">{je.event_type.replace("_", " ")}</Badge>
                    <span className="text-xs text-muted-foreground">{bucketLabelMap[je.bucket_id] || "Unknown"}</span>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(je.created_at)} {formatTime(je.created_at)}
                    </span>
                  </div>
                  {je.content && <p className="mt-1 text-sm">{je.content}</p>}
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => {
                    setEditId(je.id);
                    setForm({ bucket_id: je.bucket_id, event_type: je.event_type, content: je.content || "", ph: "", ec: "", water_temp_f: "", volume_gal: "" });
                    setDialog(true);
                  }}>
                    <Pencil className="size-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-6 text-xs text-destructive hover:text-destructive" onClick={() => handleDelete(je.id)}>
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Journal Entry Dialog (Add/Edit) */}
      <Dialog open={dialog} onOpenChange={(open) => !open && setDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editId ? "Edit" : "New"} Journal Entry</DialogTitle>
            <DialogDescription>{editId ? "Update this entry" : "Log an event for a specific bucket"}</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Bucket</Label>
                <Select value={form.bucket_id} onValueChange={(v) => setForm((p) => ({ ...p, bucket_id: v ?? "" }))} disabled={!!editId}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {buckets.map((b) => <SelectItem key={b.id} value={b.id}>#{b.position} {b.label || "Unnamed"}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Event Type</Label>
                <Select value={form.event_type} onValueChange={(v) => setForm((p) => ({ ...p, event_type: v ?? "note" }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {EVENT_TYPES.map((t) => <SelectItem key={t} value={t}>{t.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Input placeholder="What happened?" value={form.content} onChange={(e) => setForm((p) => ({ ...p, content: e.target.value }))} />
            </div>
            {showMeasurements && (
              <div className="space-y-2 rounded-md border p-3">
                <p className="text-xs font-medium text-muted-foreground">Measurements (recommended)</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">pH</Label>
                    <Input type="number" step="0.1" placeholder="5.8" value={form.ph} onChange={(e) => setForm((p) => ({ ...p, ph: e.target.value }))} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">EC</Label>
                    <Input type="number" step="0.1" placeholder="1.2" value={form.ec} onChange={(e) => setForm((p) => ({ ...p, ec: e.target.value }))} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Water Temp (°F)</Label>
                    <Input type="number" step="0.1" placeholder="68" value={form.water_temp_f} onChange={(e) => setForm((p) => ({ ...p, water_temp_f: e.target.value }))} />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Volume (gal)</Label>
                    <Input type="number" step="0.5" placeholder="5" value={form.volume_gal} onChange={(e) => setForm((p) => ({ ...p, volume_gal: e.target.value }))} />
                  </div>
                </div>
              </div>
            )}
            {showMeasurements && scheduleNutrients.length > 0 && (
              <div className="space-y-2 rounded-md border p-3">
                <p className="text-xs font-medium text-muted-foreground">Nutrients Used (from feeding schedule)</p>
                <div className="flex flex-wrap gap-1.5">
                  {scheduleNutrients.map((n) => {
                    const isSelected = selectedNutrients.has(n.name);
                    return (
                      <button
                        key={n.name}
                        type="button"
                        onClick={() => setSelectedNutrients((prev) => {
                          const next = new Set(prev);
                          if (isSelected) next.delete(n.name);
                          else next.add(n.name);
                          return next;
                        })}
                        className={`rounded-md border px-2 py-1 text-xs transition-colors ${
                          isSelected
                            ? "border-primary bg-primary/10 text-primary"
                            : "border-border text-muted-foreground hover:border-primary/50"
                        }`}
                      >
                        {n.name}{n.ml_per_gallon ? ` (${n.ml_per_gallon} ml/gal)` : ""}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleSubmit} disabled={saving || !form.bucket_id}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editId ? "Update" : "Save"} Entry
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
