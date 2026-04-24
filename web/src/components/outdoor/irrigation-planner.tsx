"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Droplets, Plus, Trash2, Clock, BarChart3 } from "lucide-react";

interface IrrigationZone {
  id: string;
  name: string;
  gridCells: string[]; // "row-col" format
  waterGallonsPerWeek: number;
  scheduleDescription: string;
}

interface WaterLog {
  id: string;
  zoneId: string;
  date: string;
  gallons: number;
  source: "manual" | "drip" | "sprinkler" | "rain";
}

interface Props {
  growId: string;
}

export function IrrigationPlanner({ growId }: Props) {
  // Local-only state (persisted via API in future iteration)
  const [zones, setZones] = useState<IrrigationZone[]>([]);
  const [logs, setLogs] = useState<WaterLog[]>([]);
  const [showZoneDialog, setShowZoneDialog] = useState(false);
  const [showLogDialog, setShowLogDialog] = useState(false);

  const [zoneForm, setZoneForm] = useState({ name: "", gallonsPerWeek: "", schedule: "" });
  const [logForm, setLogForm] = useState<{ zoneId: string; gallons: string; source: "manual" | "drip" | "sprinkler" | "rain" }>({ zoneId: "", gallons: "", source: "manual" });

  const handleAddZone = () => {
    const z: IrrigationZone = {
      id: crypto.randomUUID(),
      name: zoneForm.name,
      gridCells: [],
      waterGallonsPerWeek: +zoneForm.gallonsPerWeek || 0,
      scheduleDescription: zoneForm.schedule,
    };
    setZones([...zones, z]);
    setShowZoneDialog(false);
    setZoneForm({ name: "", gallonsPerWeek: "", schedule: "" });
  };

  const handleDeleteZone = (id: string) => {
    setZones(zones.filter((z) => z.id !== id));
    setLogs(logs.filter((l) => l.zoneId !== id));
  };

  const handleAddLog = () => {
    const l: WaterLog = {
      id: crypto.randomUUID(),
      zoneId: logForm.zoneId || zones[0]?.id || "",
      date: new Date().toISOString(),
      gallons: +logForm.gallons || 0,
      source: logForm.source,
    };
    setLogs([...logs, l]);
    setShowLogDialog(false);
    setLogForm({ zoneId: "", gallons: "", source: "manual" });
  };

  // Stats
  const thisWeekStart = new Date();
  thisWeekStart.setDate(thisWeekStart.getDate() - thisWeekStart.getDay());
  const weeklyGallons = logs
    .filter((l) => new Date(l.date) >= thisWeekStart)
    .reduce((s, l) => s + l.gallons, 0);
  const totalGallons = logs.reduce((s, l) => s + l.gallons, 0);

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="p-3 text-center">
          <Droplets className="mx-auto mb-1 size-5 text-cyan-500" />
          <p className="text-2xl font-bold">{zones.length}</p>
          <p className="text-xs text-muted-foreground">Zones</p>
        </Card>
        <Card className="p-3 text-center">
          <Clock className="mx-auto mb-1 size-5 text-blue-500" />
          <p className="text-2xl font-bold">{weeklyGallons.toFixed(1)}</p>
          <p className="text-xs text-muted-foreground">Gal This Week</p>
        </Card>
        <Card className="p-3 text-center">
          <BarChart3 className="mx-auto mb-1 size-5 text-green-500" />
          <p className="text-2xl font-bold">{totalGallons.toFixed(1)}</p>
          <p className="text-xs text-muted-foreground">Total Gallons</p>
        </Card>
      </div>

      {/* Zones */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Irrigation Zones ({zones.length})</h3>
        <Button size="sm" onClick={() => setShowZoneDialog(true)}><Plus className="mr-1 size-3" /> Add Zone</Button>
      </div>

      {zones.length === 0 ? (
        <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">
          <Droplets className="mx-auto mb-2 size-8 text-muted-foreground/50" />
          No irrigation zones defined. Create zones to plan and track watering.
        </CardContent></Card>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {zones.map((z) => {
            const zoneLogs = logs.filter((l) => l.zoneId === z.id);
            const weekGal = zoneLogs
              .filter((l) => new Date(l.date) >= thisWeekStart)
              .reduce((s, l) => s + l.gallons, 0);
            const pct = z.waterGallonsPerWeek > 0 ? Math.min(100, (weekGal / z.waterGallonsPerWeek) * 100) : 0;
            return (
              <Card key={z.id} className="p-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <p className="font-medium text-sm">{z.name}</p>
                    {z.scheduleDescription && (
                      <p className="text-xs text-muted-foreground">{z.scheduleDescription}</p>
                    )}
                    <div className="flex items-center gap-2 text-xs">
                      <span>{weekGal.toFixed(1)} / {z.waterGallonsPerWeek} gal</span>
                      <Badge variant={pct >= 100 ? "default" : "outline"} className="text-xs">
                        {pct.toFixed(0)}%
                      </Badge>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-muted">
                      <div
                        className="h-1.5 rounded-full bg-cyan-500 transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleDeleteZone(z.id)}>
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Log watering button */}
      {zones.length > 0 && (
        <div className="flex justify-end">
          <Button size="sm" variant="outline" onClick={() => setShowLogDialog(true)}>
            <Droplets className="mr-1 size-3" /> Log Watering
          </Button>
        </div>
      )}

      {/* Recent logs */}
      {logs.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Recent Watering ({logs.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            {logs.slice(-10).reverse().map((l) => {
              const zone = zones.find((z) => z.id === l.zoneId);
              return (
                <div key={l.id} className="flex items-center justify-between text-xs">
                  <span>{zone?.name ?? "Unknown"} — {l.gallons} gal ({l.source})</span>
                  <span className="text-muted-foreground">{new Date(l.date).toLocaleDateString()}</span>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* Zone dialog */}
      <Dialog open={showZoneDialog} onOpenChange={setShowZoneDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Irrigation Zone</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Zone Name</Label><Input value={zoneForm.name} onChange={(e) => setZoneForm({ ...zoneForm, name: e.target.value })} placeholder="e.g., Drip Line A, Raised Beds" /></div>
            <div><Label>Target Gallons/Week</Label><Input type="number" value={zoneForm.gallonsPerWeek} onChange={(e) => setZoneForm({ ...zoneForm, gallonsPerWeek: e.target.value })} /></div>
            <div><Label>Schedule Notes</Label><Input value={zoneForm.schedule} onChange={(e) => setZoneForm({ ...zoneForm, schedule: e.target.value })} placeholder="e.g., MWF mornings, 30 min" /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowZoneDialog(false)}>Cancel</Button>
            <Button onClick={handleAddZone} disabled={!zoneForm.name}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Log watering dialog */}
      <Dialog open={showLogDialog} onOpenChange={setShowLogDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Watering</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Zone</Label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={logForm.zoneId || zones[0]?.id || ""}
                onChange={(e) => setLogForm({ ...logForm, zoneId: e.target.value })}
              >
                {zones.map((z) => <option key={z.id} value={z.id}>{z.name}</option>)}
              </select>
            </div>
            <div><Label>Gallons</Label><Input type="number" step="0.1" value={logForm.gallons} onChange={(e) => setLogForm({ ...logForm, gallons: e.target.value })} /></div>
            <div><Label>Source</Label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={logForm.source}
                onChange={(e) => setLogForm({ ...logForm, source: e.target.value as "manual" | "drip" | "sprinkler" | "rain" })}
              >
                <option value="manual">Manual (hose/can)</option>
                <option value="drip">Drip System</option>
                <option value="sprinkler">Sprinkler</option>
                <option value="rain">Rain</option>
              </select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLogDialog(false)}>Cancel</Button>
            <Button onClick={handleAddLog} disabled={!logForm.gallons}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
