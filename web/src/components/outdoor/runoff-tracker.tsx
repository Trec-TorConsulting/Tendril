"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listRunoffReadings,
  createRunoffReading,
  getRunoffStats,
  deleteRunoffReading,
  listBuckets,
  type RunoffReadingResponse,
  type RunoffStatsResponse,
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

interface RunoffTrackerProps {
  growId: string;
  tentId: string;
}

function phBadge(ph: number | null, target: { min: number; max: number }) {
  if (ph === null) return null;
  const inRange = ph >= target.min && ph <= target.max;
  return (
    <Badge variant={inRange ? "secondary" : "destructive"} className="text-xs">
      {ph.toFixed(1)}
    </Badge>
  );
}

function ecBadge(ec: number | null) {
  if (ec === null) return null;
  return (
    <Badge variant="secondary" className="text-xs">
      {ec.toFixed(2)}
    </Badge>
  );
}

function deltaBadge(delta: number | null, label: string, warnThreshold: number) {
  if (delta === null) return null;
  const warn = Math.abs(delta) > warnThreshold;
  return (
    <span className={`text-xs ${warn ? "text-orange-600 font-medium" : "text-muted-foreground"}`}>
      {label}: {delta > 0 ? "+" : ""}{delta.toFixed(2)} {warn ? "⚠️" : ""}
    </span>
  );
}

export default function RunoffTracker({ growId }: RunoffTrackerProps) {
  const [readings, setReadings] = useState<RunoffReadingResponse[]>([]);
  const [stats, setStats] = useState<RunoffStatsResponse[]>([]);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [filterBucket, setFilterBucket] = useState<string>("all");
  const [form, setForm] = useState({
    bucket_id: "",
    input_ph: "",
    input_ec: "",
    runoff_ph: "",
    runoff_ec: "",
    runoff_pct: "",
    notes: "",
  });

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [r, s, b] = await Promise.all([
        listRunoffReadings(token, growId),
        getRunoffStats(token, growId),
        listBuckets(token, growId),
      ]);
      setReadings(r);
      setStats(s);
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

  const bucketName = (id: string) => { const b = buckets.find((x) => x.id === id); return b ? (b.label || `Pot ${b.position}`) : "Unknown"; };

  const handleSubmit = async () => {
    if (!form.bucket_id) return;
    const token = getAccessToken();
    if (!token) return;
    setSubmitting(true);
    try {
      await createRunoffReading(token, growId, {
        bucket_id: form.bucket_id,
        input_ph: form.input_ph ? parseFloat(form.input_ph) : null,
        input_ec: form.input_ec ? parseFloat(form.input_ec) : null,
        runoff_ph: form.runoff_ph ? parseFloat(form.runoff_ph) : null,
        runoff_ec: form.runoff_ec ? parseFloat(form.runoff_ec) : null,
        runoff_pct: form.runoff_pct ? parseFloat(form.runoff_pct) : null,
        notes: form.notes || null,
      });
      setForm({ bucket_id: "", input_ph: "", input_ec: "", runoff_ph: "", runoff_ec: "", runoff_pct: "", notes: "" });
      setShowForm(false);
      await refresh();
    } catch {
      /* ignore */
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteRunoffReading(token, growId, id);
    await refresh();
  };

  const filteredReadings = filterBucket === "all"
    ? readings
    : readings.filter((r) => r.bucket_id === filterBucket);

  // Overall stats
  const totalReadings = readings.length;
  const bucketsWithData = new Set(readings.map((r) => r.bucket_id)).size;
  const saltBuildup = stats.filter((s) => s.avg_ec_delta !== null && s.avg_ec_delta > 0.5);

  if (loading) {
    return <div className="text-sm text-muted-foreground p-4">Loading runoff data...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold">{totalReadings}</div>
            <div className="text-xs text-muted-foreground">Readings</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold">{bucketsWithData}/{buckets.length}</div>
            <div className="text-xs text-muted-foreground">Pots Tracked</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className={`text-2xl font-bold ${saltBuildup.length > 0 ? "text-orange-500" : "text-green-600"}`}>
              {saltBuildup.length}
            </div>
            <div className="text-xs text-muted-foreground">Salt Buildup ⚠️</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <Button size="sm" onClick={() => setShowForm(!showForm)}>
              {showForm ? "Cancel" : "+ Log Reading"}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Entry form */}
      {showForm && (
        <Card>
          <CardHeader><CardTitle className="text-sm">New Runoff Reading</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Pot</Label>
              <Select value={form.bucket_id || "none"} onValueChange={(v) => setForm({ ...form, bucket_id: v === "none" ? "" : v ?? "" })}>
                <SelectTrigger><SelectValue placeholder="Select pot..." /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Select pot...</SelectItem>
                  {buckets.map((b) => (
                    <SelectItem key={b.id} value={b.id}>{b.label || `Pot ${b.position}`}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-blue-600">Input pH</Label>
                <Input type="number" step="0.1" min="0" max="14" value={form.input_ph} onChange={(e) => setForm({ ...form, input_ph: e.target.value })} placeholder="6.0" />
              </div>
              <div>
                <Label className="text-orange-600">Runoff pH</Label>
                <Input type="number" step="0.1" min="0" max="14" value={form.runoff_ph} onChange={(e) => setForm({ ...form, runoff_ph: e.target.value })} placeholder="6.2" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-blue-600">Input EC</Label>
                <Input type="number" step="0.01" min="0" max="20" value={form.input_ec} onChange={(e) => setForm({ ...form, input_ec: e.target.value })} placeholder="1.2" />
              </div>
              <div>
                <Label className="text-orange-600">Runoff EC</Label>
                <Input type="number" step="0.01" min="0" max="20" value={form.runoff_ec} onChange={(e) => setForm({ ...form, runoff_ec: e.target.value })} placeholder="1.8" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Runoff % (volume)</Label>
                <Input type="number" step="1" min="0" max="100" value={form.runoff_pct} onChange={(e) => setForm({ ...form, runoff_pct: e.target.value })} placeholder="15" />
              </div>
              <div>
                <Label>Notes</Label>
                <Input value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Optional notes" />
              </div>
            </div>
            {/* Live delta preview */}
            {(form.input_ph && form.runoff_ph) && (
              <div className="text-sm">
                pH Δ: <span className={Math.abs(parseFloat(form.runoff_ph) - parseFloat(form.input_ph)) > 0.5 ? "text-orange-600 font-medium" : "text-green-600"}>
                  {(parseFloat(form.runoff_ph) - parseFloat(form.input_ph)).toFixed(1)}
                </span>
                {form.input_ec && form.runoff_ec && (
                  <span className="ml-4">
                    EC Δ: <span className={Math.abs(parseFloat(form.runoff_ec) - parseFloat(form.input_ec)) > 0.5 ? "text-orange-600 font-medium" : "text-green-600"}>
                      {(parseFloat(form.runoff_ec) - parseFloat(form.input_ec)).toFixed(2)}
                    </span>
                  </span>
                )}
              </div>
            )}
            <Button onClick={handleSubmit} disabled={!form.bucket_id || submitting}>
              {submitting ? "Saving..." : "Log Reading"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Per-pot stats */}
      {stats.length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-sm">Per-Pot Summary</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.map((s) => (
                <div key={s.bucket_id} className="flex items-center justify-between border-b pb-2 last:border-0">
                  <div>
                    <div className="font-medium text-sm">{bucketName(s.bucket_id)}</div>
                    <div className="text-xs text-muted-foreground">{s.reading_count} readings</div>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <div className="flex gap-2">
                      <span className="text-xs text-muted-foreground">pH in:</span>
                      {phBadge(s.latest_input_ph, { min: 6.0, max: 7.0 })}
                      <span className="text-xs text-muted-foreground">out:</span>
                      {phBadge(s.latest_runoff_ph, { min: 6.0, max: 7.0 })}
                    </div>
                    <div className="flex gap-2">
                      <span className="text-xs text-muted-foreground">EC in:</span>
                      {ecBadge(s.latest_input_ec)}
                      <span className="text-xs text-muted-foreground">out:</span>
                      {ecBadge(s.latest_runoff_ec)}
                    </div>
                    <div className="flex gap-3">
                      {deltaBadge(s.avg_ph_delta, "Avg pH Δ", 0.5)}
                      {deltaBadge(s.avg_ec_delta, "Avg EC Δ", 0.5)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reading history */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">Reading History</CardTitle>
            <Select value={filterBucket} onValueChange={(v) => setFilterBucket(v ?? "all")}>
              <SelectTrigger className="w-[180px]"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Pots</SelectItem>
                {buckets.map((b) => (
                  <SelectItem key={b.id} value={b.id}>{b.label || `Pot ${b.position}`}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {filteredReadings.length === 0 ? (
            <div className="text-center text-sm text-muted-foreground py-4">
              No runoff readings yet. Log your first reading above.
            </div>
          ) : (
            <div className="space-y-2">
              {filteredReadings.map((r) => {
                const phDelta = r.input_ph !== null && r.runoff_ph !== null ? r.runoff_ph - r.input_ph : null;
                const ecDelta = r.input_ec !== null && r.runoff_ec !== null ? r.runoff_ec - r.input_ec : null;
                return (
                  <div key={r.id} className="border rounded-lg p-3 text-sm">
                    <div className="flex items-center justify-between mb-1">
                      <div className="font-medium">{bucketName(r.bucket_id)}</div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">
                          {new Date(r.recorded_at).toLocaleDateString()}
                        </span>
                        <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-muted-foreground" onClick={() => handleDelete(r.id)}>×</Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                      <div>
                        <span className="text-blue-600">In pH:</span> {r.input_ph?.toFixed(1) ?? "—"}
                      </div>
                      <div>
                        <span className="text-orange-600">Out pH:</span> {r.runoff_ph?.toFixed(1) ?? "—"}
                        {phDelta !== null && (
                          <span className={Math.abs(phDelta) > 0.5 ? " text-orange-600" : " text-green-600"}>
                            {" "}(Δ {phDelta > 0 ? "+" : ""}{phDelta.toFixed(1)})
                          </span>
                        )}
                      </div>
                      <div>
                        <span className="text-blue-600">In EC:</span> {r.input_ec?.toFixed(2) ?? "—"}
                      </div>
                      <div>
                        <span className="text-orange-600">Out EC:</span> {r.runoff_ec?.toFixed(2) ?? "—"}
                        {ecDelta !== null && (
                          <span className={Math.abs(ecDelta) > 0.5 ? " text-orange-600" : " text-green-600"}>
                            {" "}(Δ {ecDelta > 0 ? "+" : ""}{ecDelta.toFixed(2)})
                          </span>
                        )}
                      </div>
                    </div>
                    {r.runoff_pct !== null && (
                      <div className="text-xs text-muted-foreground mt-1">Runoff: {r.runoff_pct}%</div>
                    )}
                    {r.notes && (
                      <div className="text-xs text-muted-foreground mt-1">{r.notes}</div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
