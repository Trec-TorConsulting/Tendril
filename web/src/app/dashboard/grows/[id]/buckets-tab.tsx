"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  createBucket,
  deleteBucket,
  updateBucket,
  type BucketResponse,
  type SensorReadingResponse,
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
import { Plus, Trash2, Droplets, Pencil, Loader2 } from "lucide-react";

interface BucketsTabProps {
  growId: string;
  buckets: BucketResponse[];
  latestReadings: Record<string, SensorReadingResponse | null>;
  onRefresh: () => void;
  onOpenSensorDialog: (bucketId: string, bucketLabel: string) => void;
}

export function BucketsTab({ growId, buckets, latestReadings, onRefresh, onOpenSensorDialog }: BucketsTabProps) {
  const [addLabel, setAddLabel] = useState("");
  const [addStrain, setAddStrain] = useState("");
  const [addVolume, setAddVolume] = useState("");

  const [editDialog, setEditDialog] = useState(false);
  const [editId, setEditId] = useState("");
  const [editForm, setEditForm] = useState({ label: "", strain_name: "", volume_gallons: "" });
  const [editSaving, setEditSaving] = useState(false);

  const handleAdd = async () => {
    const token = getAccessToken();
    if (!token) return;
    await createBucket(token, {
      grow_cycle_id: growId,
      label: addLabel || undefined,
      strain_name: addStrain || undefined,
      volume_gallons: addVolume ? parseFloat(addVolume) : undefined,
      position: buckets.length + 1,
    });
    setAddLabel("");
    setAddStrain("");
    setAddVolume("");
    onRefresh();
  };

  const handleDelete = async (bucketId: string) => {
    if (!confirm("Delete this bucket/plant?")) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteBucket(token, bucketId);
    onRefresh();
  };

  const handleEditSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setEditSaving(true);
    try {
      await updateBucket(token, editId, {
        label: editForm.label || undefined,
        strain_name: editForm.strain_name || undefined,
        volume_gallons: editForm.volume_gallons ? parseFloat(editForm.volume_gallons) : undefined,
      });
      setEditDialog(false);
      onRefresh();
    } catch { /* empty */ } finally { setEditSaving(false); }
  };

  return (
    <>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {buckets.map((b) => {
          const reading = latestReadings[b.id];
          return (
            <Card key={b.id}>
              <CardContent className="p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-medium">#{b.position} {b.label || "Unnamed"}</span>
                  <Badge variant="outline" className="text-xs">{b.growth_stage}</Badge>
                </div>
                {b.strain_name && (
                  <p className="text-sm text-muted-foreground">Strain: {b.strain_name}</p>
                )}
                <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{b.volume_gallons ? `${b.volume_gallons} gal` : "No size set"}</span>
                </div>
                {reading && (
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                    {reading.ph != null && <div><span className="text-muted-foreground">pH</span><p className="font-medium">{reading.ph.toFixed(1)}</p></div>}
                    {reading.ec != null && <div><span className="text-muted-foreground">EC</span><p className="font-medium">{reading.ec.toFixed(2)}</p></div>}
                    {reading.ppm != null && <div><span className="text-muted-foreground">PPM</span><p className="font-medium">{Math.round(reading.ppm)}</p></div>}
                    {reading.water_temp_f != null && <div><span className="text-muted-foreground">Water °F</span><p className="font-medium">{reading.water_temp_f.toFixed(1)}</p></div>}
                    {reading.ambient_temp_f != null && <div><span className="text-muted-foreground">Ambient °F</span><p className="font-medium">{reading.ambient_temp_f.toFixed(1)}</p></div>}
                    {reading.ambient_humidity != null && <div><span className="text-muted-foreground">Humidity</span><p className="font-medium">{reading.ambient_humidity.toFixed(0)}%</p></div>}
                  </div>
                )}
                {!reading && <p className="mt-2 text-xs text-muted-foreground">No readings yet</p>}
                <div className="mt-3 flex items-center gap-2">
                  <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => {
                    setEditId(b.id);
                    setEditForm({ label: b.label || "", strain_name: b.strain_name || "", volume_gallons: b.volume_gallons?.toString() || "" });
                    setEditDialog(true);
                  }}>
                    <Pencil className="mr-1 size-3" /> Edit
                  </Button>
                  <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => onOpenSensorDialog(b.id, `#${b.position} ${b.label || "Unnamed"}`)}>
                    <Droplets className="mr-1 size-3" /> Log Reading
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={() => handleDelete(b.id)}>
                    <Trash2 className="mr-1 size-3" /> Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}

        {/* Add bucket card */}
        <Card className="border-dashed">
          <CardContent className="p-4">
            <p className="mb-2 text-sm font-medium text-muted-foreground">Add bucket/plant</p>
            <Input className="mb-2" placeholder="Label (optional)" value={addLabel} onChange={(e) => setAddLabel(e.target.value)} />
            <Input className="mb-2" placeholder="Strain (optional)" value={addStrain} onChange={(e) => setAddStrain(e.target.value)} />
            <Input className="mb-2" type="number" step="0.5" placeholder="Bucket size (gallons)" value={addVolume} onChange={(e) => setAddVolume(e.target.value)} />
            <Button size="sm" onClick={handleAdd}>
              <Plus className="mr-1 size-3" /> Add
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Edit Bucket Dialog */}
      <Dialog open={editDialog} onOpenChange={(open) => !open && setEditDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Bucket</DialogTitle>
            <DialogDescription>Update label, strain, and bucket size</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Label</Label>
              <Input placeholder="e.g. Back Left" value={editForm.label} onChange={(e) => setEditForm((p) => ({ ...p, label: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Strain</Label>
              <Input placeholder="e.g. Blue Dream" value={editForm.strain_name} onChange={(e) => setEditForm((p) => ({ ...p, strain_name: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Bucket Size (gallons)</Label>
              <Input type="number" step="0.5" placeholder="e.g. 5" value={editForm.volume_gallons} onChange={(e) => setEditForm((p) => ({ ...p, volume_gallons: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setEditDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleEditSubmit} disabled={editSaving}>
              {editSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
