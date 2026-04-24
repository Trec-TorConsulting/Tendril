"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listHarvestYields,
  createHarvestYield,
  getYieldSummary,
  deleteHarvestYield,
  type HarvestYieldResponse,
  type YieldSummaryResponse,
  type BucketResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
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
import { Scissors, Plus, Trash2, Scale, Award, BarChart3 } from "lucide-react";

interface Props {
  growId: string;
  buckets: BucketResponse[];
}

export function HarvestTracker({ growId, buckets }: Props) {
  const [yields, setYields] = useState<HarvestYieldResponse[]>([]);
  const [summary, setSummary] = useState<YieldSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);

  const [form, setForm] = useState({
    bucket_id: "",
    wet_weight_oz: "",
    dry_weight_oz: "",
    trim_weight_oz: "",
    quality_rating: "",
    trichome_stage: "",
    notes: "",
  });

  const refresh = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) return;
    try {
      const [y, s] = await Promise.all([
        listHarvestYields(token, growId),
        getYieldSummary(token, growId),
      ]);
      setYields(y);
      setSummary(s);
    } finally {
      setLoading(false);
    }
  }, [growId]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleCreate = async () => {
    const token = await getAccessToken();
    if (!token || !form.bucket_id) return;
    const data: Record<string, unknown> = { bucket_id: form.bucket_id };
    if (form.wet_weight_oz) data.wet_weight_oz = +form.wet_weight_oz;
    if (form.dry_weight_oz) data.dry_weight_oz = +form.dry_weight_oz;
    if (form.trim_weight_oz) data.trim_weight_oz = +form.trim_weight_oz;
    if (form.quality_rating) data.quality_rating = +form.quality_rating;
    if (form.trichome_stage) data.trichome_stage = form.trichome_stage;
    if (form.notes) data.notes = form.notes;

    await createHarvestYield(token, growId, data);
    setShowDialog(false);
    setForm({ bucket_id: "", wet_weight_oz: "", dry_weight_oz: "", trim_weight_oz: "", quality_rating: "", trichome_stage: "", notes: "" });
    refresh();
  };

  const handleDelete = async (id: string) => {
    const token = await getAccessToken();
    if (!token) return;
    await deleteHarvestYield(token, growId, id);
    refresh();
  };

  const bucketName = (id: string) => {
    const b = buckets.find((b) => b.id === id);
    return b?.strain_name || b?.label || `Plant ${b?.position ?? "?"}`;
  };

  if (loading) return <div className="flex justify-center py-8"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>;

  return (
    <div className="space-y-4">
      {/* Summary cards */}
      {summary && summary.plants_harvested > 0 && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="p-3 text-center">
            <Scale className="mx-auto mb-1 size-5 text-green-500" />
            <p className="text-2xl font-bold">{summary.total_dry_oz} oz</p>
            <p className="text-xs text-muted-foreground">Total Dry Weight</p>
          </Card>
          <Card className="p-3 text-center">
            <BarChart3 className="mx-auto mb-1 size-5 text-blue-500" />
            <p className="text-2xl font-bold">{summary.avg_dry_per_plant_oz} oz</p>
            <p className="text-xs text-muted-foreground">Avg Per Plant</p>
          </Card>
          <Card className="p-3 text-center">
            <Scissors className="mx-auto mb-1 size-5 text-purple-500" />
            <p className="text-2xl font-bold">{summary.plants_harvested}/{summary.total_plants}</p>
            <p className="text-xs text-muted-foreground">Plants Harvested</p>
          </Card>
          {summary.yield_per_sqft_oz !== null && (
            <Card className="p-3 text-center">
              <Award className="mx-auto mb-1 size-5 text-amber-500" />
              <p className="text-2xl font-bold">{summary.yield_per_sqft_oz} oz</p>
              <p className="text-xs text-muted-foreground">Per Sq Ft</p>
            </Card>
          )}
          {summary.avg_quality !== null && (
            <Card className="p-3 text-center">
              <Award className="mx-auto mb-1 size-5 text-amber-500" />
              <p className="text-2xl font-bold">{summary.avg_quality}/10</p>
              <p className="text-xs text-muted-foreground">Avg Quality</p>
            </Card>
          )}
        </div>
      )}

      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Harvest Log ({yields.length})</h3>
        <Button size="sm" onClick={() => setShowDialog(true)}><Plus className="mr-1 size-3" /> Log Harvest</Button>
      </div>

      {yields.length === 0 ? (
        <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">
          <Scissors className="mx-auto mb-2 size-8 text-muted-foreground/50" />
          No harvests logged yet. Log yields per plant for detailed analytics.
        </CardContent></Card>
      ) : (
        <div className="space-y-2">
          {yields.map((y) => (
            <Card key={y.id} className="p-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <p className="text-sm font-medium">{bucketName(y.bucket_id)}</p>
                  <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                    <span>{new Date(y.harvested_at).toLocaleDateString()}</span>
                    {y.wet_weight_oz !== null && <span>Wet: {y.wet_weight_oz} oz</span>}
                    {y.dry_weight_oz !== null && <Badge variant="outline">Dry: {y.dry_weight_oz} oz</Badge>}
                    {y.trim_weight_oz !== null && <span>Trim: {y.trim_weight_oz} oz</span>}
                    {y.quality_rating !== null && <Badge>{y.quality_rating}/10</Badge>}
                    {y.trichome_stage && <Badge variant="outline">{y.trichome_stage}</Badge>}
                  </div>
                  {y.notes && <p className="text-xs text-muted-foreground">{y.notes}</p>}
                </div>
                <Button variant="ghost" size="icon" onClick={() => handleDelete(y.id)}><Trash2 className="size-3" /></Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Plant Harvest</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Plant</Label>
              <Select value={form.bucket_id} onValueChange={(v) => setForm({ ...form, bucket_id: v ?? "" })}>
                <SelectTrigger><SelectValue placeholder="Select plant..." /></SelectTrigger>
                <SelectContent>
                  {buckets.map((b) => (
                    <SelectItem key={b.id} value={b.id}>
                      {b.strain_name || b.label || `Position ${b.position}`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div><Label>Wet (oz)</Label><Input type="number" step="0.1" value={form.wet_weight_oz} onChange={(e) => setForm({ ...form, wet_weight_oz: e.target.value })} /></div>
              <div><Label>Dry (oz)</Label><Input type="number" step="0.1" value={form.dry_weight_oz} onChange={(e) => setForm({ ...form, dry_weight_oz: e.target.value })} /></div>
              <div><Label>Trim (oz)</Label><Input type="number" step="0.1" value={form.trim_weight_oz} onChange={(e) => setForm({ ...form, trim_weight_oz: e.target.value })} /></div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Quality (1-10)</Label><Input type="number" min={1} max={10} value={form.quality_rating} onChange={(e) => setForm({ ...form, quality_rating: e.target.value })} /></div>
              <div><Label>Trichome Stage</Label>
                <Select value={form.trichome_stage || "none"} onValueChange={(v) => setForm({ ...form, trichome_stage: v === "none" ? "" : v ?? "" })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Not set</SelectItem>
                    <SelectItem value="clear">Clear</SelectItem>
                    <SelectItem value="cloudy">Cloudy</SelectItem>
                    <SelectItem value="amber">Amber</SelectItem>
                    <SelectItem value="mixed">Mixed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div><Label>Notes</Label><Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={!form.bucket_id}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
