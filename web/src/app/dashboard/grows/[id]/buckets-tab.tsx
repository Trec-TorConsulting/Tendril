"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import {
  createBucket,
  deleteBucket,
  updateBucket,
  listStrains,
  type BucketResponse,
  type SensorReadingResponse,
  type StrainResponse,
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
import { Plus, Trash2, Droplets, Pencil, Loader2, Dna, FlaskConical, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { ReferenceStrainSearch } from "@/components/reference-search";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp } from "@/lib/units";
import { createQuickJournalEntry } from "@/lib/api";

interface BucketsTabProps {
  growId: string;
  growType: string;
  buckets: BucketResponse[];
  latestReadings: Record<string, SensorReadingResponse | null>;
  onRefresh: () => void;
  onOpenSensorDialog: (bucketId: string, bucketLabel: string) => void;
}

export function BucketsTab({ growId, growType, buckets, latestReadings, onRefresh, onOpenSensorDialog }: BucketsTabProps) {
  const { prefs } = usePreferences();
  const [addLabel, setAddLabel] = useState("");
  const [addStrainId, setAddStrainId] = useState("");
  const [addVolume, setAddVolume] = useState("");
  const [addRole, setAddRole] = useState("site");
  const [addDialog, setAddDialog] = useState(false);
  const [strains, setStrains] = useState<StrainResponse[]>([]);

  const [editDialog, setEditDialog] = useState(false);
  const [editId, setEditId] = useState("");
  const [editForm, setEditForm] = useState({ label: "", strain_id: "", volume_gallons: "", role: "site" });
  const [editSaving, setEditSaving] = useState(false);

  // Water change / Feed quick action dialog
  const [quickActionDialog, setQuickActionDialog] = useState<{ type: "water_change" | "feeding"; bucketId: string; bucketLabel: string } | null>(null);
  const [quickForm, setQuickForm] = useState({ ph: "", ec: "", ppm: "", water_temp_f: "", notes: "" });
  const [quickSaving, setQuickSaving] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    listStrains(token).then(setStrains).catch(() => {});
  }, []);

  const strainMap = Object.fromEntries(strains.map((s) => [s.id, s]));

  const handleAdd = async () => {
    const token = getAccessToken();
    if (!token) return;
    await createBucket(token, {
      grow_cycle_id: growId,
      label: addLabel || undefined,
      strain_id: addStrainId || undefined,
      volume_gallons: addVolume ? parseFloat(addVolume) : undefined,
      position: buckets.length + 1,
      role: addRole !== "site" ? addRole : undefined,
    });
    setAddLabel("");
    setAddStrainId("");
    setAddVolume("");
    setAddRole("site");
    setAddDialog(false);
    onRefresh();
  };

  const confirm = useConfirm();

  const handleDelete = async (bucketId: string) => {
    if (!await confirm({ title: "Delete Bucket", description: "Delete this bucket/plant?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteBucket(token, bucketId);
      onRefresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete bucket"); }
  };

  const handleEditSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setEditSaving(true);
    try {
      await updateBucket(token, editId, {
        label: editForm.label || undefined,
        strain_id: editForm.strain_id || undefined,
        volume_gallons: editForm.volume_gallons ? parseFloat(editForm.volume_gallons) : undefined,
        role: editForm.role,
      });
      setEditDialog(false);
      onRefresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to update bucket"); } finally { setEditSaving(false); }
  };

  const handleQuickAction = async () => {
    if (!quickActionDialog) return;
    const token = getAccessToken();
    if (!token) return;
    setQuickSaving(true);
    try {
      await createQuickJournalEntry(token, {
        bucket_id: quickActionDialog.bucketId,
        event_type: quickActionDialog.type,
        content: quickForm.notes || undefined,
        ph: quickForm.ph ? parseFloat(quickForm.ph) : undefined,
        ec: quickForm.ec ? parseFloat(quickForm.ec) : undefined,
        ppm: quickForm.ppm ? parseFloat(quickForm.ppm) : undefined,
        water_temp_f: quickForm.water_temp_f ? parseFloat(quickForm.water_temp_f) : undefined,
      });
      toast.success(quickActionDialog.type === "water_change" ? "Water change logged" : "Feeding logged");
      setQuickActionDialog(null);
      setQuickForm({ ph: "", ec: "", ppm: "", water_temp_f: "", notes: "" });
      onRefresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to log action");
    } finally {
      setQuickSaving(false);
    }
  };

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{buckets.length} bucket{buckets.length !== 1 ? "s" : ""}</p>
        <Button size="sm" onClick={() => {
          setAddLabel("");
          setAddStrainId("");
          setAddVolume("");
          setAddRole("site");
          setAddDialog(true);
        }}>
          <Plus className="mr-1 size-3" /> Add Bucket
        </Button>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {buckets.map((b) => {
          const reading = latestReadings[b.id];
          const strain = b.strain_id ? strainMap[b.strain_id] : null;
          const daysSinceWater = b.last_water_change_at
            ? Math.floor((Date.now() - new Date(b.last_water_change_at).getTime()) / 86400000)
            : null;
          const waterBadgeVariant = daysSinceWater === null ? "outline" : daysSinceWater > 10 ? "destructive" : daysSinceWater > 7 ? "secondary" : "default";
          return (
            <Card key={b.id}>
              <CardContent className="p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-medium">#{b.position} {b.label || "Unnamed"}</span>
                  <div className="flex items-center gap-1.5">
                    {b.role === "header" && (
                      <Badge variant="default" className="text-[10px] bg-blue-600">Header</Badge>
                    )}
                    <Badge variant={waterBadgeVariant} className="text-[10px]">
                      {daysSinceWater === null ? "No water change" : `${daysSinceWater}d since change`}
                    </Badge>
                    <Badge variant="outline" className="text-xs">{b.growth_stage}</Badge>
                  </div>
                </div>
                {(b.strain_name || strain) && (
                  <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                    <Dna className="size-3" />
                    <span>{strain?.name || b.strain_name}</span>
                    {strain?.genetics && <span className="text-xs opacity-70">({strain.genetics})</span>}
                  </div>
                )}
                {strain?.flowering_days && (
                  <p className="text-xs text-muted-foreground">{strain.flowering_days}d flower</p>
                )}
                <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{b.volume_gallons ? `${b.volume_gallons} gal` : "No size set"}</span>
                </div>
                {reading && (
                  <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                    {reading.ph != null && <div><span className="text-muted-foreground">pH</span><p className="font-medium">{reading.ph.toFixed(1)}</p></div>}
                    {reading.ec != null && <div><span className="text-muted-foreground">EC</span><p className="font-medium">{reading.ec.toFixed(2)}</p></div>}
                    {reading.ppm != null && <div><span className="text-muted-foreground">PPM</span><p className="font-medium">{Math.round(reading.ppm)}</p></div>}
                    {reading.water_temp_f != null && <div><span className="text-muted-foreground">Water {prefs.temp_unit === "celsius" ? "°C" : "°F"}</span><p className="font-medium">{formatTemp(reading.water_temp_f, "f", prefs.temp_unit)}</p></div>}
                  </div>
                )}
                {!reading && <p className="mt-2 text-xs text-muted-foreground">No readings yet</p>}
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Button variant="default" size="sm" className="h-7 text-xs" onClick={() => {
                    setQuickForm({ ph: "", ec: "", ppm: "", water_temp_f: "", notes: "" });
                    setQuickActionDialog({ type: "water_change", bucketId: b.id, bucketLabel: `#${b.position} ${b.label || "Unnamed"}` });
                  }}>
                    <RefreshCw className="mr-1 size-3" /> Water Change
                  </Button>
                  <Button variant="secondary" size="sm" className="h-7 text-xs" onClick={() => {
                    setQuickForm({ ph: "", ec: "", ppm: "", water_temp_f: "", notes: "" });
                    setQuickActionDialog({ type: "feeding", bucketId: b.id, bucketLabel: `#${b.position} ${b.label || "Unnamed"}` });
                  }}>
                    <FlaskConical className="mr-1 size-3" /> Feed
                  </Button>
                  <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => onOpenSensorDialog(b.id, `#${b.position} ${b.label || "Unnamed"}`)}>
                    <Droplets className="mr-1 size-3" /> Log Reading
                  </Button>
                  <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => {
                    setEditId(b.id);
                    setEditForm({ label: b.label || "", strain_id: b.strain_id || "", volume_gallons: b.volume_gallons?.toString() || "", role: b.role || "site" });
                    setEditDialog(true);
                  }}>
                    <Pencil className="mr-1 size-3" /> Edit
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={() => handleDelete(b.id)}>
                    <Trash2 className="mr-1 size-3" /> Remove
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}

      </div>

      {/* Add Bucket Dialog */}
      <Dialog open={addDialog} onOpenChange={(open) => !open && setAddDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Bucket / Plant</DialogTitle>
            <DialogDescription>Add a new bucket or plant to this grow cycle.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Label (optional)</Label>
              <Input placeholder="e.g. Bucket A" value={addLabel} onChange={(e) => setAddLabel(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Strain (optional)</Label>
              <Select value={addStrainId} onValueChange={(v) => setAddStrainId(v ?? "")}>
                <SelectTrigger>
                  <SelectValue>{addStrainId ? strainMap[addStrainId]?.name ?? "Select strain" : "Select strain"}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {strains.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}{s.genetics ? ` (${s.genetics})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <ReferenceStrainSearch
                placeholder="Or search global strain database..."
                onSelect={(s) => setAddStrainId(s.id)}
                className="mt-1"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Bucket Size (gallons)</Label>
              <Input type="number" step="0.5" placeholder="e.g. 5" value={addVolume} onChange={(e) => setAddVolume(e.target.value)} />
            </div>
            {growType === "rdwc" && (
              <div className="space-y-1">
                <Label className="text-xs">Role</Label>
                <Select value={addRole} onValueChange={(v) => setAddRole(v || "site")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="site">Site Bucket</SelectItem>
                    <SelectItem value="header">Header / Control Bucket</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">The header bucket&apos;s readings propagate to all site buckets in the system.</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setAddDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleAdd}>
              <Plus className="mr-1 size-3" /> Add Bucket
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
              <Select value={editForm.strain_id} onValueChange={(v) => setEditForm((p) => ({ ...p, strain_id: v ?? "" }))}>
                <SelectTrigger>
                  <SelectValue>{editForm.strain_id ? strainMap[editForm.strain_id]?.name ?? "Select strain" : "Select strain"}</SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {strains.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}{s.genetics ? ` (${s.genetics})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Bucket Size (gallons)</Label>
              <Input type="number" step="0.5" placeholder="e.g. 5" value={editForm.volume_gallons} onChange={(e) => setEditForm((p) => ({ ...p, volume_gallons: e.target.value }))} />
            </div>
            {growType === "rdwc" && (
              <div className="space-y-1">
                <Label className="text-xs">Role</Label>
                <Select value={editForm.role} onValueChange={(v) => setEditForm((p) => ({ ...p, role: v || "site" }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="site">Site Bucket</SelectItem>
                    <SelectItem value="header">Header / Control Bucket</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
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

      {/* Quick Action Dialog (Water Change / Feed) */}
      <Dialog open={!!quickActionDialog} onOpenChange={(open) => !open && setQuickActionDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {quickActionDialog?.type === "water_change" ? "Log Water Change" : "Log Feeding"}
            </DialogTitle>
            <DialogDescription>
              {quickActionDialog?.bucketLabel} — record readings and create a journal entry
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">pH</Label>
                <Input type="number" step="0.1" placeholder="e.g. 5.8" value={quickForm.ph} onChange={(e) => setQuickForm((p) => ({ ...p, ph: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">EC (mS/cm)</Label>
                <Input type="number" step="0.01" placeholder="e.g. 1.2" value={quickForm.ec} onChange={(e) => setQuickForm((p) => ({ ...p, ec: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">PPM</Label>
                <Input type="number" step="1" placeholder="e.g. 800" value={quickForm.ppm} onChange={(e) => setQuickForm((p) => ({ ...p, ppm: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Water Temp ({prefs.temp_unit === "celsius" ? "°C" : "°F"})</Label>
                <Input type="number" step="0.1" placeholder="e.g. 68" value={quickForm.water_temp_f} onChange={(e) => setQuickForm((p) => ({ ...p, water_temp_f: e.target.value }))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes (optional)</Label>
              <Input placeholder="e.g. Added CalMag, full flush" value={quickForm.notes} onChange={(e) => setQuickForm((p) => ({ ...p, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setQuickActionDialog(null)}>Cancel</Button>
            <Button type="button" onClick={handleQuickAction} disabled={quickSaving}>
              {quickSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {quickActionDialog?.type === "water_change" ? "Log Water Change" : "Log Feeding"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
