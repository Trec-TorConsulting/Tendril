"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listContainerProfiles,
  upsertContainerProfile,
  listBuckets,
  type ContainerProfileResponse,
  type BucketResponse,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface ContainerManagerProps {
  growId: string;
  tentId: string;
}

const MATERIALS = [
  { value: "plastic", label: "Plastic" },
  { value: "fabric", label: "Fabric (Smart Pot)" },
  { value: "ceramic", label: "Ceramic" },
  { value: "terracotta", label: "Terracotta" },
  { value: "metal", label: "Metal" },
  { value: "wood", label: "Wood" },
  { value: "concrete", label: "Concrete" },
  { value: "other", label: "Other" },
];

const SUN_OPTIONS = [
  { value: "full_sun", label: "Full Sun (6+ hrs)" },
  { value: "partial_sun", label: "Partial Sun (4-6 hrs)" },
  { value: "partial_shade", label: "Partial Shade (2-4 hrs)" },
  { value: "full_shade", label: "Full Shade (<2 hrs)" },
];

const MEDIA_TYPES = [
  "Soil", "Coco Coir", "Coco-Perlite Mix", "Peat Mix",
  "Super Soil", "Living Soil", "Pro-Mix", "Other",
];

export default function ContainerManager({ growId }: ContainerManagerProps) {
  const [profiles, setProfiles] = useState<ContainerProfileResponse[]>([]);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [editBucketId, setEditBucketId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    pot_size_gallons: "",
    media_type: "",
    pot_color: "",
    pot_material: "",
    has_saucer: false,
    is_mobile: true,
    sun_exposure: "",
    location_notes: "",
  });

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [p, b] = await Promise.all([
        listContainerProfiles(token, growId),
        listBuckets(token, growId),
      ]);
      setProfiles(p);
      setBuckets(b);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }, [growId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const profileMap = new Map(profiles.map((p) => [p.bucket_id, p]));

  const openEdit = (bucketId: string) => {
    const existing = profileMap.get(bucketId);
    if (existing) {
      setForm({
        pot_size_gallons: existing.pot_size_gallons?.toString() ?? "",
        media_type: existing.media_type ?? "",
        pot_color: existing.pot_color ?? "",
        pot_material: existing.pot_material ?? "",
        has_saucer: existing.has_saucer,
        is_mobile: existing.is_mobile,
        sun_exposure: existing.sun_exposure ?? "",
        location_notes: existing.location_notes ?? "",
      });
    } else {
      setForm({
        pot_size_gallons: "",
        media_type: "",
        pot_color: "",
        pot_material: "",
        has_saucer: false,
        is_mobile: true,
        sun_exposure: "",
        location_notes: "",
      });
    }
    setEditBucketId(bucketId);
  };

  const handleSave = async () => {
    if (!editBucketId) return;
    const token = getAccessToken();
    if (!token) return;
    setSaving(true);
    try {
      await upsertContainerProfile(token, growId, editBucketId, {
        pot_size_gallons: form.pot_size_gallons ? parseFloat(form.pot_size_gallons) : null,
        media_type: form.media_type || null,
        pot_color: form.pot_color || null,
        pot_material: form.pot_material || null,
        has_saucer: form.has_saucer,
        is_mobile: form.is_mobile,
        sun_exposure: form.sun_exposure || null,
        location_notes: form.location_notes || null,
      });
      setEditBucketId(null);
      await refresh();
    } catch {
      /* ignore */
    } finally {
      setSaving(false);
    }
  };

  const materialLabel = (val: string | null) => MATERIALS.find((m) => m.value === val)?.label ?? val ?? "—";
  const sunLabel = (val: string | null) => SUN_OPTIONS.find((s) => s.value === val)?.label ?? val ?? "—";

  // Summary cards
  const totalPots = profiles.length;
  const mobilePots = profiles.filter((p) => p.is_mobile).length;
  const darkPots = profiles.filter((p) =>
    p.pot_color && ["black", "dark", "navy", "brown"].some((c) => p.pot_color!.toLowerCase().includes(c))
  ).length;
  const avgSize = totalPots > 0
    ? (profiles.reduce((s, p) => s + (p.pot_size_gallons ?? 0), 0) / totalPots).toFixed(1)
    : "—";

  if (loading) {
    return <div className="text-sm text-muted-foreground p-4">Loading containers...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold">{totalPots}/{buckets.length}</div>
            <div className="text-xs text-muted-foreground">Profiled</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold">{avgSize}</div>
            <div className="text-xs text-muted-foreground">Avg Gallons</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold">{mobilePots}</div>
            <div className="text-xs text-muted-foreground">Mobile</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-orange-500">{darkPots}</div>
            <div className="text-xs text-muted-foreground">Dark Pots ⚠️</div>
          </CardContent>
        </Card>
      </div>

      {/* Pot cards */}
      {buckets.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            No pots added yet. Add pots from the Pots tab first.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {buckets.map((b) => {
            const profile = profileMap.get(b.id);
            return (
              <Card key={b.id} className="relative">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center justify-between">
                    <span>{b.label || `Pot ${b.position}`}</span>
                    {profile ? (
                      <Badge variant="outline" className="text-green-600">Profiled</Badge>
                    ) : (
                      <Badge variant="outline" className="text-yellow-600">No Profile</Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-1">
                  {profile ? (
                    <>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Size</span>
                        <span>{profile.pot_size_gallons ? `${profile.pot_size_gallons} gal` : "—"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Material</span>
                        <span>{materialLabel(profile.pot_material)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Media</span>
                        <span>{profile.media_type ?? "—"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Sun</span>
                        <span>{sunLabel(profile.sun_exposure)}</span>
                      </div>
                      <div className="flex gap-2 mt-2">
                        {profile.is_mobile && <Badge variant="secondary">Mobile</Badge>}
                        {profile.has_saucer && <Badge variant="secondary">Saucer</Badge>}
                        {profile.pot_color && (
                          <Badge
                            variant="secondary"
                            className={
                              ["black", "dark", "navy", "brown"].some((c) =>
                                profile.pot_color!.toLowerCase().includes(c)
                              )
                                ? "bg-orange-100 text-orange-700"
                                : ""
                            }
                          >
                            {profile.pot_color}
                          </Badge>
                        )}
                      </div>
                      {profile.location_notes && (
                        <div className="text-xs text-muted-foreground mt-1">📍 {profile.location_notes}</div>
                      )}
                    </>
                  ) : (
                    <div className="text-muted-foreground text-center py-2">
                      No container info yet
                    </div>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full mt-2"
                    onClick={() => openEdit(b.id)}
                  >
                    {profile ? "Edit" : "Set Up Container"}
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Edit dialog */}
      <Dialog open={editBucketId !== null} onOpenChange={(open) => !open && setEditBucketId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Container Profile</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Pot Size (gallons)</Label>
                <Input
                  type="number"
                  step="0.5"
                  min="0.1"
                  value={form.pot_size_gallons}
                  onChange={(e) => setForm({ ...form, pot_size_gallons: e.target.value })}
                  placeholder="e.g. 5"
                />
              </div>
              <div>
                <Label>Material</Label>
                <Select value={form.pot_material || "none"} onValueChange={(v) => setForm({ ...form, pot_material: v === "none" ? "" : v ?? "" })}>
                  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Not set</SelectItem>
                    {MATERIALS.map((m) => (
                      <SelectItem key={m.value} value={m.value}>{m.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Media Type</Label>
                <Select value={form.media_type || "none"} onValueChange={(v) => setForm({ ...form, media_type: v === "none" ? "" : v ?? "" })}>
                  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Not set</SelectItem>
                    {MEDIA_TYPES.map((m) => (
                      <SelectItem key={m} value={m}>{m}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Sun Exposure</Label>
                <Select value={form.sun_exposure || "none"} onValueChange={(v) => setForm({ ...form, sun_exposure: v === "none" ? "" : v ?? "" })}>
                  <SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Not set</SelectItem>
                    {SUN_OPTIONS.map((s) => (
                      <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Pot Color</Label>
              <Input
                value={form.pot_color}
                onChange={(e) => setForm({ ...form, pot_color: e.target.value })}
                placeholder="e.g. Black, White, Terracotta"
              />
              {form.pot_color && ["black", "dark", "navy", "brown"].some((c) => form.pot_color.toLowerCase().includes(c)) && (
                <p className="text-xs text-orange-600 mt-1">
                  ⚠️ Dark pots absorb more heat — roots can overheat in direct sun. Consider wrapping or moving to shade during peak hours.
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.has_saucer}
                  onChange={(e) => setForm({ ...form, has_saucer: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Has Saucer</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.is_mobile}
                  onChange={(e) => setForm({ ...form, is_mobile: e.target.checked })}
                  className="rounded"
                />
                <span className="text-sm">Can Move Indoors</span>
              </label>
            </div>
            <div>
              <Label>Location Notes</Label>
              <Input
                value={form.location_notes}
                onChange={(e) => setForm({ ...form, location_notes: e.target.value })}
                placeholder="e.g. South-facing patio, near fence"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditBucketId(null)}>Cancel</Button>
            <Button onClick={handleSave} disabled={saving}>{saving ? "Saving..." : "Save"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
