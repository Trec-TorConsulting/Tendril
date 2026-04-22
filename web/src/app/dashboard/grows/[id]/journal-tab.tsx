"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { formatDate, formatTime } from "@/lib/utils";
import {
  createJournalEntry,
  updateJournalEntry,
  deleteJournalEntry,
  type JournalEntryResponse,
  type BucketResponse,
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

const EVENT_TYPES = ["note", "feeding", "water_change", "training", "transplant", "defoliation", "topping", "flushing", "other"];

interface JournalTabProps {
  buckets: BucketResponse[];
  journalEntries: JournalEntryResponse[];
  bucketLabelMap: Record<string, string>;
  onRefresh: () => void;
}

export function JournalTab({ buckets, journalEntries, bucketLabelMap, onRefresh }: JournalTabProps) {
  const [dialog, setDialog] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState({ bucket_id: "", event_type: "note", content: "" });
  const [saving, setSaving] = useState(false);

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
      } else {
        await createJournalEntry(token, {
          bucket_id: form.bucket_id,
          event_type: form.event_type,
          content: form.content.trim() || undefined,
        });
      }
      setDialog(false);
      setEditId(null);
      setForm({ bucket_id: "", event_type: "note", content: "" });
      onRefresh();
    } catch { /* empty */ } finally { setSaving(false); }
  };

  const handleDelete = async (entryId: string) => {
    if (!confirm("Delete this journal entry?")) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteJournalEntry(token, entryId);
    onRefresh();
  };

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Grow Journal</h3>
        <Button size="sm" onClick={() => {
          setEditId(null);
          setForm({ bucket_id: buckets[0]?.id || "", event_type: "note", content: "" });
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
                    setForm({ bucket_id: je.bucket_id, event_type: je.event_type, content: je.content || "" });
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
