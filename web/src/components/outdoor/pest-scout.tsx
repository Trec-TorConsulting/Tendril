"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listPestScouts,
  createPestScout,
  deletePestScout,
  type PestScoutResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
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
import { Bug, Plus, Trash2, Shield, AlertTriangle } from "lucide-react";

const PEST_TYPES = ["insect", "disease", "animal", "beneficial", "unknown"];
const SEVERITIES = ["low", "medium", "high", "critical"];
const TREATMENT_TYPES = ["organic", "synthetic", "biological", "physical", "none"];

const SEVERITY_COLORS: Record<string, string> = {
  low: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400",
};

interface Props {
  growId: string;
}

export function PestScout({ growId }: Props) {
  const [entries, setEntries] = useState<PestScoutResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [filter, setFilter] = useState<string>("all");

  const [form, setForm] = useState({
    pest_type: "insect",
    species: "",
    severity: "low",
    grid_row: "",
    grid_col: "",
    treatment_applied: "",
    treatment_type: "",
    notes: "",
  });

  const refresh = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) return;
    try {
      const filters = filter !== "all" ? { pest_type: filter } : undefined;
      const data = await listPestScouts(token, growId, filters);
      setEntries(data);
    } finally {
      setLoading(false);
    }
  }, [growId, filter]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleCreate = async () => {
    const token = await getAccessToken();
    if (!token || !form.species) return;
    const data: Record<string, unknown> = {
      pest_type: form.pest_type,
      species: form.species,
      severity: form.severity,
    };
    if (form.grid_row) data.grid_row = +form.grid_row;
    if (form.grid_col) data.grid_col = +form.grid_col;
    if (form.treatment_applied) data.treatment_applied = form.treatment_applied;
    if (form.treatment_type) data.treatment_type = form.treatment_type;
    if (form.notes) data.notes = form.notes;

    await createPestScout(token, growId, data);
    setShowDialog(false);
    setForm({ pest_type: "insect", species: "", severity: "low", grid_row: "", grid_col: "", treatment_applied: "", treatment_type: "", notes: "" });
    refresh();
  };

  const handleDelete = async (id: string) => {
    const token = await getAccessToken();
    if (!token) return;
    await deletePestScout(token, growId, id);
    refresh();
  };

  const beneficialCount = entries.filter((e) => e.pest_type === "beneficial").length;
  const threatCount = entries.filter((e) => e.pest_type !== "beneficial").length;
  const criticalCount = entries.filter((e) => e.severity === "critical" || e.severity === "high").length;

  if (loading) return <div className="flex justify-center py-8"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>;

  return (
    <div className="space-y-4">
      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="p-3 text-center">
          <p className="text-2xl font-bold">{threatCount}</p>
          <p className="text-xs text-muted-foreground">Threats</p>
        </Card>
        <Card className="p-3 text-center">
          <p className="text-2xl font-bold text-green-600">{beneficialCount}</p>
          <p className="text-xs text-muted-foreground">Beneficials</p>
        </Card>
        <Card className="p-3 text-center">
          <p className={`text-2xl font-bold ${criticalCount > 0 ? "text-red-600" : ""}`}>{criticalCount}</p>
          <p className="text-xs text-muted-foreground">High/Critical</p>
        </Card>
      </div>

      {/* Filter & add */}
      <div className="flex items-center justify-between">
        <Select value={filter} onValueChange={(v) => setFilter(v ?? "all")}>
          <SelectTrigger className="w-[140px]"><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {PEST_TYPES.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
          </SelectContent>
        </Select>
        <Button size="sm" onClick={() => setShowDialog(true)}><Plus className="mr-1 size-3" /> Log Observation</Button>
      </div>

      {/* Entries list */}
      {entries.length === 0 ? (
        <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">
          <Shield className="mx-auto mb-2 size-8 text-muted-foreground/50" />
          No scouting entries yet. Regular field scouting is key to early pest detection.
        </CardContent></Card>
      ) : (
        <div className="space-y-2">
          {entries.map((e) => (
            <Card key={e.id} className="p-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {e.pest_type === "beneficial" ? (
                      <Shield className="size-4 text-green-500" />
                    ) : e.severity === "critical" || e.severity === "high" ? (
                      <AlertTriangle className="size-4 text-red-500" />
                    ) : (
                      <Bug className="size-4 text-muted-foreground" />
                    )}
                    <span className="font-medium text-sm">{e.species}</span>
                    <Badge variant="outline" className="text-xs">{e.pest_type}</Badge>
                    <Badge className={`text-xs ${SEVERITY_COLORS[e.severity] ?? ""}`}>{e.severity}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {new Date(e.scouted_at).toLocaleDateString()}
                    {e.grid_row !== null && e.grid_col !== null && ` · Plot (${e.grid_row},${e.grid_col})`}
                  </p>
                  {e.treatment_applied && (
                    <p className="text-xs">Treatment: {e.treatment_applied} ({e.treatment_type})</p>
                  )}
                  {e.notes && <p className="text-xs text-muted-foreground">{e.notes}</p>}
                </div>
                <Button variant="ghost" size="icon" onClick={() => handleDelete(e.id)}><Trash2 className="size-3" /></Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Field Observation</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Type</Label>
                <Select value={form.pest_type} onValueChange={(v) => setForm({ ...form, pest_type: v ?? "insect" })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {PEST_TYPES.map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div><Label>Severity</Label>
                <Select value={form.severity} onValueChange={(v) => setForm({ ...form, severity: v ?? "low" })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {SEVERITIES.map((s) => <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div><Label>Species/Name</Label><Input value={form.species} onChange={(e) => setForm({ ...form, species: e.target.value })} placeholder="e.g., Aphid, Powdery Mildew, Ladybug" /></div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label>Grid Row</Label><Input type="number" value={form.grid_row} onChange={(e) => setForm({ ...form, grid_row: e.target.value })} placeholder="Optional" /></div>
              <div><Label>Grid Col</Label><Input type="number" value={form.grid_col} onChange={(e) => setForm({ ...form, grid_col: e.target.value })} placeholder="Optional" /></div>
            </div>
            <div><Label>Treatment Applied</Label><Input value={form.treatment_applied} onChange={(e) => setForm({ ...form, treatment_applied: e.target.value })} placeholder="e.g., Neem oil spray" /></div>
            <div><Label>Treatment Type</Label>
              <Select value={form.treatment_type || "none"} onValueChange={(v) => setForm({ ...form, treatment_type: v === "none" ? "" : v ?? "" })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {TREATMENT_TYPES.filter((t) => t !== "none").map((t) => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div><Label>Notes</Label><Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDialog(false)}>Cancel</Button>
            <Button onClick={handleCreate} disabled={!form.species}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
