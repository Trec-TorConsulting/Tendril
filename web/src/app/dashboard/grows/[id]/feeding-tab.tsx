"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  createFeedingSchedule,
  updateFeedingSchedule,
  deleteFeedingSchedule,
  listDoseProfiles,
  createDoseProfile,
  updateDoseProfile,
  deleteDoseProfile,
  type FeedingScheduleResponse,
  type BucketResponse,
  type DoseProfileResponse,
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
import { FlaskConical, Plus, Trash2, Pencil, Loader2, ToggleLeft, ToggleRight } from "lucide-react";
import { useEffect, useCallback } from "react";

const STAGES = ["seedling", "vegetative", "flowering", "ripening", "drying", "curing"];

interface FeedingTabProps {
  growId: string;
  growStage: string;
  buckets: BucketResponse[];
  feedingSchedules: FeedingScheduleResponse[];
  onRefresh: () => void;
  onOpenBrandDialog: () => void;
}

export function FeedingTab({ growId, growStage, buckets, feedingSchedules, onRefresh, onOpenBrandDialog }: FeedingTabProps) {
  // Feeding schedule dialog (add/edit)
  const [feedingDialog, setFeedingDialog] = useState(false);
  const [editFeedingId, setEditFeedingId] = useState<string | null>(null);
  const [feedingForm, setFeedingForm] = useState({ name: "", stage: "vegetative", notes: "", nutrients: [{ name: "", brand: "", ml_per_gallon: "" }] });
  const [feedingSaving, setFeedingSaving] = useState(false);

  // Dose profiles
  const [doseProfiles, setDoseProfiles] = useState<DoseProfileResponse[]>([]);
  const [doseDialog, setDoseDialog] = useState(false);
  const [editDoseId, setEditDoseId] = useState<string | null>(null);
  const [doseForm, setDoseForm] = useState({ name: "", dose_type: "nutrient", dose_ml: "" });
  const [doseSaving, setDoseSaving] = useState(false);

  const loadDoses = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try { setDoseProfiles(await listDoseProfiles(token, growId)); } catch { /* empty */ }
  }, [growId]);

  useEffect(() => { loadDoses(); }, [loadDoses]);

  const handleFeedingSubmit = async () => {
    const token = getAccessToken();
    if (!token || !feedingForm.name.trim()) return;
    setFeedingSaving(true);
    try {
      const nutrients = feedingForm.nutrients
        .filter((n) => n.name.trim())
        .map((n) => ({ name: n.name.trim(), brand: n.brand.trim() || undefined, ml_per_gallon: n.ml_per_gallon ? parseFloat(n.ml_per_gallon) : undefined }));
      if (editFeedingId) {
        await updateFeedingSchedule(token, editFeedingId, {
          name: feedingForm.name.trim(),
          stage: feedingForm.stage,
          nutrients,
          notes: feedingForm.notes.trim() || undefined,
        });
      } else {
        await createFeedingSchedule(token, {
          grow_cycle_id: growId,
          name: feedingForm.name.trim(),
          stage: feedingForm.stage,
          nutrients,
          notes: feedingForm.notes.trim() || undefined,
        });
      }
      setFeedingDialog(false);
      setEditFeedingId(null);
      setFeedingForm({ name: "", stage: "vegetative", notes: "", nutrients: [{ name: "", brand: "", ml_per_gallon: "" }] });
      onRefresh();
    } catch { /* empty */ } finally { setFeedingSaving(false); }
  };

  const handleDeleteFeeding = async (schedId: string) => {
    if (!confirm("Delete this feeding schedule?")) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteFeedingSchedule(token, schedId);
    onRefresh();
  };

  const handleDoseSubmit = async () => {
    const token = getAccessToken();
    if (!token || !doseForm.name.trim() || !doseForm.dose_ml) return;
    setDoseSaving(true);
    try {
      if (editDoseId) {
        await updateDoseProfile(token, editDoseId, {
          name: doseForm.name.trim(),
          dose_ml: parseFloat(doseForm.dose_ml),
        });
      } else {
        await createDoseProfile(token, {
          grow_cycle_id: growId,
          name: doseForm.name.trim(),
          dose_type: doseForm.dose_type,
          dose_ml: parseFloat(doseForm.dose_ml),
        });
      }
      setDoseDialog(false);
      setEditDoseId(null);
      setDoseForm({ name: "", dose_type: "nutrient", dose_ml: "" });
      loadDoses();
    } catch { /* empty */ } finally { setDoseSaving(false); }
  };

  const handleToggleDose = async (dose: DoseProfileResponse) => {
    const token = getAccessToken();
    if (!token) return;
    await updateDoseProfile(token, dose.id, { enabled: !dose.enabled });
    loadDoses();
  };

  const handleDeleteDose = async (doseId: string) => {
    if (!confirm("Delete this dose profile?")) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteDoseProfile(token, doseId);
    loadDoses();
  };

  return (
    <>
      {/* Feeding Schedules */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Feeding Schedules</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={onOpenBrandDialog}>
            <FlaskConical className="mr-1 size-3" /> Use Brand Template
          </Button>
          <Button size="sm" onClick={() => {
            setEditFeedingId(null);
            setFeedingForm({ name: "", stage: growStage || "vegetative", notes: "", nutrients: [{ name: "", brand: "", ml_per_gallon: "" }] });
            setFeedingDialog(true);
          }}>
            <Plus className="mr-1 size-3" /> Add Custom
          </Button>
        </div>
      </div>
      {feedingSchedules.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-12">
          <FlaskConical className="size-10 text-muted-foreground/50" />
          <p className="mt-3 text-sm text-muted-foreground">No feeding schedules yet</p>
          <p className="text-xs text-muted-foreground">Add your nutrient mix for each growth stage</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {feedingSchedules.map((fs) => (
            <Card key={fs.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{fs.name}</span>
                      <Badge variant="secondary" className="capitalize text-xs">{fs.stage}</Badge>
                    </div>
                    {fs.nutrients.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {fs.nutrients.map((n, i) => (
                          <p key={i} className="text-sm text-muted-foreground">
                            {n.name}{n.brand ? ` (${n.brand})` : ""}{n.ml_per_gallon ? ` — ${n.ml_per_gallon} ml/gal` : ""}
                          </p>
                        ))}
                      </div>
                    )}
                    {/* Per-bucket breakdown */}
                    {fs.nutrients.some((n) => n.ml_per_gallon) && buckets.filter((b) => b.volume_gallons && b.status === "active").length > 0 && (
                      <div className="mt-3 rounded-md border bg-muted/30 p-2">
                        <p className="mb-1 text-xs font-medium text-muted-foreground">Per Bucket</p>
                        <div className="space-y-1">
                          {buckets.filter((b) => b.volume_gallons && b.status === "active").map((b) => (
                            <div key={b.id} className="flex flex-wrap items-baseline gap-x-3 text-xs">
                              <span className="font-medium min-w-[5rem]">#{b.position} {b.label || "Unnamed"} ({b.volume_gallons}g)</span>
                              {fs.nutrients.filter((n) => n.ml_per_gallon).map((n, i) => (
                                <span key={i} className="text-muted-foreground">
                                  {n.name}: <span className="text-foreground font-medium">{(n.ml_per_gallon! * b.volume_gallons!).toFixed(1)} ml</span>
                                </span>
                              ))}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {fs.notes && <p className="mt-1 text-xs text-muted-foreground italic">{fs.notes}</p>}
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => {
                      setEditFeedingId(fs.id);
                      setFeedingForm({
                        name: fs.name,
                        stage: fs.stage,
                        notes: fs.notes || "",
                        nutrients: fs.nutrients.map((n) => ({ name: n.name, brand: n.brand || "", ml_per_gallon: n.ml_per_gallon?.toString() || "" })),
                      });
                      setFeedingDialog(true);
                    }}>
                      <Pencil className="size-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={() => handleDeleteFeeding(fs.id)}>
                      <Trash2 className="size-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Dose Profiles Section */}
      <div className="mt-8 mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium">Dose Profiles</h3>
        <Button size="sm" onClick={() => {
          setEditDoseId(null);
          setDoseForm({ name: "", dose_type: "nutrient", dose_ml: "" });
          setDoseDialog(true);
        }}>
          <Plus className="mr-1 size-3" /> Add Dose
        </Button>
      </div>
      {doseProfiles.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-8">
          <p className="text-sm text-muted-foreground">No dose profiles yet</p>
          <p className="text-xs text-muted-foreground">Configure dosing pumps for automated feeding</p>
        </Card>
      ) : (
        <div className="space-y-2">
          {doseProfiles.map((dp) => (
            <Card key={dp.id}>
              <CardContent className="flex items-center justify-between p-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{dp.name}</span>
                    <Badge variant="outline" className="text-xs">{dp.dose_type}</Badge>
                    <Badge variant={dp.enabled ? "default" : "secondary"} className="text-xs">{dp.enabled ? "Active" : "Disabled"}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">{dp.dose_ml} ml per dose</p>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="sm" className="h-7" onClick={() => handleToggleDose(dp)}>
                    {dp.enabled ? <ToggleRight className="size-4" /> : <ToggleLeft className="size-4" />}
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => {
                    setEditDoseId(dp.id);
                    setDoseForm({ name: dp.name, dose_type: dp.dose_type, dose_ml: dp.dose_ml.toString() });
                    setDoseDialog(true);
                  }}>
                    <Pencil className="size-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={() => handleDeleteDose(dp.id)}>
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Feeding Schedule Dialog (Add/Edit) */}
      <Dialog open={feedingDialog} onOpenChange={(open) => !open && setFeedingDialog(false)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editFeedingId ? "Edit" : "New"} Feeding Schedule</DialogTitle>
            <DialogDescription>Define a nutrient mix for a specific growth stage</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Name</Label>
                <Input placeholder="e.g. Early Veg Mix" value={feedingForm.name} onChange={(e) => setFeedingForm((p) => ({ ...p, name: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Stage</Label>
                <Select value={feedingForm.stage} onValueChange={(v) => setFeedingForm((p) => ({ ...p, stage: v ?? "vegetative" }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {STAGES.map((s) => <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label className="text-xs">Nutrients</Label>
              {feedingForm.nutrients.map((n, i) => (
                <div key={i} className="flex gap-2">
                  <Input className="flex-1" placeholder="Nutrient name" value={n.name} onChange={(e) => {
                    const updated = [...feedingForm.nutrients];
                    updated[i] = { ...updated[i], name: e.target.value };
                    setFeedingForm((p) => ({ ...p, nutrients: updated }));
                  }} />
                  <Input className="w-28" placeholder="Brand" value={n.brand} onChange={(e) => {
                    const updated = [...feedingForm.nutrients];
                    updated[i] = { ...updated[i], brand: e.target.value };
                    setFeedingForm((p) => ({ ...p, nutrients: updated }));
                  }} />
                  <Input className="w-24" type="number" step="0.1" placeholder="ml/gal" value={n.ml_per_gallon} onChange={(e) => {
                    const updated = [...feedingForm.nutrients];
                    updated[i] = { ...updated[i], ml_per_gallon: e.target.value };
                    setFeedingForm((p) => ({ ...p, nutrients: updated }));
                  }} />
                  {feedingForm.nutrients.length > 1 && (
                    <Button type="button" variant="ghost" size="sm" className="h-8 px-2 text-destructive" onClick={() => {
                      setFeedingForm((p) => ({ ...p, nutrients: p.nutrients.filter((_, j) => j !== i) }));
                    }}>
                      <Trash2 className="size-3" />
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => setFeedingForm((p) => ({ ...p, nutrients: [...p.nutrients, { name: "", brand: "", ml_per_gallon: "" }] }))}>
                <Plus className="mr-1 size-3" /> Add Nutrient
              </Button>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes (optional)</Label>
              <Input placeholder="e.g. Mix A first, then B after 30 min" value={feedingForm.notes} onChange={(e) => setFeedingForm((p) => ({ ...p, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setFeedingDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleFeedingSubmit} disabled={feedingSaving || !feedingForm.name.trim()}>
              {feedingSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editFeedingId ? "Update" : "Save"} Schedule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dose Profile Dialog (Add/Edit) */}
      <Dialog open={doseDialog} onOpenChange={(open) => !open && setDoseDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editDoseId ? "Edit" : "New"} Dose Profile</DialogTitle>
            <DialogDescription>Configure an automated dosing profile</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Name</Label>
              <Input placeholder="e.g. pH Down" value={doseForm.name} onChange={(e) => setDoseForm((p) => ({ ...p, name: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Type</Label>
              <Select value={doseForm.dose_type} onValueChange={(v) => setDoseForm((p) => ({ ...p, dose_type: v ?? "nutrient" }))} disabled={!!editDoseId}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="nutrient">Nutrient</SelectItem>
                  <SelectItem value="ph_up">pH Up</SelectItem>
                  <SelectItem value="ph_down">pH Down</SelectItem>
                  <SelectItem value="additive">Additive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Dose Amount (ml)</Label>
              <Input type="number" step="0.1" placeholder="e.g. 2.5" value={doseForm.dose_ml} onChange={(e) => setDoseForm((p) => ({ ...p, dose_ml: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setDoseDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleDoseSubmit} disabled={doseSaving || !doseForm.name.trim() || !doseForm.dose_ml}>
              {doseSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editDoseId ? "Update" : "Save"} Profile
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
