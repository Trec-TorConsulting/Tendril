"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listSensorReadings,
  listJournalEntries,
  listDoseProfiles,
  listPhotos,
  getSensorDrift,
  getGrow,
  type BucketResponse,
  type SensorReadingResponse,
  type JournalEntryResponse,
  type DoseProfileResponse,
  type PhotoResponse,
} from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, tempUnitLabel } from "@/lib/units";
import { formatShortDateTime } from "@/lib/utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Activity, BookOpen, Pipette, Camera, Loader2 } from "lucide-react";

interface BucketDetailModalProps {
  bucket: BucketResponse | null;
  growId: string;
  open: boolean;
  onClose: () => void;
}

export function BucketDetailModal({ bucket, growId, open, onClose }: BucketDetailModalProps) {
  const { prefs } = usePreferences();
  const [readings, setReadings] = useState<SensorReadingResponse[]>([]);
  const [journal, setJournal] = useState<JournalEntryResponse[]>([]);
  const [doses, setDoses] = useState<DoseProfileResponse[]>([]);
  const [photos, setPhotos] = useState<PhotoResponse[]>([]);
  const [drift, setDrift] = useState<{
    ph: { min: number; max: number; first: number; last: number; delta: number; count: number } | null;
    ec: { min: number; max: number; first: number; last: number; delta: number; count: number } | null;
  } | null>(null);
  const [milestones, setMilestones] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    if (!bucket) return;
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
    try {
      const [readingsData, journalData, dosesData, photosData, driftData, growData] = await Promise.all([
        listSensorReadings(token, bucket.id, 200),
        listJournalEntries(token, bucket.id),
        listDoseProfiles(token, growId),
        listPhotos(token, bucket.id),
        getSensorDrift(token, bucket.id, 168).catch(() => null),
        getGrow(token, growId).catch(() => null),
      ]);
      setReadings(readingsData);
      setJournal(journalData);
      setDoses(dosesData);
      setPhotos(photosData);
      setDrift(driftData ? { ph: driftData.ph, ec: driftData.ec } : null);
      setMilestones(growData?.milestones || {});
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, [bucket, growId]);

  useEffect(() => {
    if (open && bucket) loadData();
  }, [open, bucket, loadData]);

  if (!bucket) return null;

  const latestReading = readings[0] ?? null;

  const chartData = [...readings].reverse().map((r) => ({
    time: new Date(r.recorded_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }),
    ph: r.ph,
    ec: r.ec,
    water_temp_f: r.water_temp_f != null
      ? Number(formatTemp(r.water_temp_f, "f", prefs.temp_unit))
      : null,
  }));

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span>#{bucket.position} {bucket.label || "Unnamed"}</span>
            <Badge variant="outline">{bucket.growth_stage}</Badge>
            {bucket.role === "header" && <Badge className="bg-blue-600">Header</Badge>}
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="size-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Tabs defaultValue="overview" className="mt-2">
            <TabsList>
              <TabsTrigger value="overview"><Activity className="mr-1 size-3" /> Overview</TabsTrigger>
              <TabsTrigger value="journal"><BookOpen className="mr-1 size-3" /> Journal ({journal.length})</TabsTrigger>
              <TabsTrigger value="doses"><Pipette className="mr-1 size-3" /> Doses ({doses.length})</TabsTrigger>
              <TabsTrigger value="photos"><Camera className="mr-1 size-3" /> Photos ({photos.length})</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4 mt-4">
              {/* Current Readings */}
              <Card>
                <CardContent className="p-4">
                  <h3 className="text-sm font-medium mb-3">Current Readings</h3>
                  {latestReading ? (
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
                      {latestReading.ph != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">pH</span>
                          <p className="font-semibold text-lg">{latestReading.ph.toFixed(1)}</p>
                        </div>
                      )}
                      {latestReading.ec != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">EC</span>
                          <p className="font-semibold text-lg">{latestReading.ec.toFixed(2)} mS</p>
                        </div>
                      )}
                      {latestReading.ppm != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">PPM</span>
                          <p className="font-semibold text-lg">{Math.round(latestReading.ppm)}</p>
                        </div>
                      )}
                      {latestReading.water_temp_f != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">Water Temp</span>
                          <p className="font-semibold text-lg">{formatTemp(latestReading.water_temp_f, "f", prefs.temp_unit)} {tempUnitLabel(prefs.temp_unit)}</p>
                        </div>
                      )}
                      {latestReading.dissolved_oxygen != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">D.O.</span>
                          <p className="font-semibold text-lg">{latestReading.dissolved_oxygen.toFixed(1)} mg/L</p>
                        </div>
                      )}
                      {latestReading.water_level_pct != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">Water Level</span>
                          <p className="font-semibold text-lg">{Math.round(latestReading.water_level_pct)}%</p>
                        </div>
                      )}
                      {latestReading.soil_moisture != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">Soil Moisture</span>
                          <p className="font-semibold text-lg">{Math.round(latestReading.soil_moisture)}%</p>
                        </div>
                      )}
                      {latestReading.orp != null && (
                        <div>
                          <span className="text-muted-foreground text-xs">ORP</span>
                          <p className="font-semibold text-lg">{Math.round(latestReading.orp)} mV</p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No readings yet</p>
                  )}
                  {latestReading && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Last reading: {formatShortDateTime(latestReading.recorded_at)}
                    </p>
                  )}
                </CardContent>
              </Card>

              {/* Drift Summary */}
              {drift && (drift.ph || drift.ec) && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="text-sm font-medium mb-2">7-Day Drift</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {drift.ph && (
                        <div>
                          <span className="text-muted-foreground text-xs">pH</span>
                          <p className="font-medium">
                            {drift.ph.first.toFixed(1)} → {drift.ph.last.toFixed(1)}
                            <span className={`ml-2 text-xs ${drift.ph.delta > 0 ? "text-green-500" : drift.ph.delta < 0 ? "text-red-500" : ""}`}>
                              ({drift.ph.delta > 0 ? "+" : ""}{drift.ph.delta.toFixed(2)})
                            </span>
                          </p>
                          <p className="text-xs text-muted-foreground">Range: {drift.ph.min.toFixed(1)} – {drift.ph.max.toFixed(1)} ({drift.ph.count} readings)</p>
                        </div>
                      )}
                      {drift.ec && (
                        <div>
                          <span className="text-muted-foreground text-xs">EC</span>
                          <p className="font-medium">
                            {drift.ec.first.toFixed(2)} → {drift.ec.last.toFixed(2)}
                            <span className={`ml-2 text-xs ${drift.ec.delta > 0 ? "text-green-500" : drift.ec.delta < 0 ? "text-red-500" : ""}`}>
                              ({drift.ec.delta > 0 ? "+" : ""}{drift.ec.delta.toFixed(2)})
                            </span>
                          </p>
                          <p className="text-xs text-muted-foreground">Range: {drift.ec.min.toFixed(2)} – {drift.ec.max.toFixed(2)} ({drift.ec.count} readings)</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Milestones */}
              {Object.keys(milestones).length > 0 && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="text-sm font-medium mb-2">Milestones</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
                      {Object.entries(milestones).map(([stage, dateStr]) => (
                        <div key={stage}>
                          <span className="text-muted-foreground text-xs capitalize">{stage.replace(/_/g, " ")}</span>
                          <p className="font-medium">{formatShortDateTime(dateStr)}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Sensor Trend Chart */}
              {chartData.length >= 2 && (
                <Card>
                  <CardContent className="p-4">
                    <h3 className="text-sm font-medium mb-3">Sensor Trends</h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                          <XAxis dataKey="time" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                          <YAxis yAxisId="ph" domain={[4, 8]} tick={{ fontSize: 10 }} />
                          <YAxis yAxisId="ec" orientation="right" tick={{ fontSize: 10 }} />
                          <Tooltip contentStyle={{ fontSize: 12 }} />
                          <Legend wrapperStyle={{ fontSize: 12 }} />
                          <Line yAxisId="ph" type="monotone" dataKey="ph" stroke="#22c55e" name="pH" dot={false} strokeWidth={2} connectNulls />
                          <Line yAxisId="ec" type="monotone" dataKey="ec" stroke="#3b82f6" name="EC" dot={false} strokeWidth={2} connectNulls />
                          <Line yAxisId="ec" type="monotone" dataKey="water_temp_f" stroke="#ef4444" name={`Temp (${tempUnitLabel(prefs.temp_unit)})`} dot={false} strokeWidth={1.5} connectNulls />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Bucket Info */}
              <Card>
                <CardContent className="p-4">
                  <h3 className="text-sm font-medium mb-2">Details</h3>
                  <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                    <dt className="text-muted-foreground">Volume</dt>
                    <dd>{bucket.volume_gallons ? `${bucket.volume_gallons} gal` : "—"}</dd>
                    <dt className="text-muted-foreground">Strain</dt>
                    <dd>{bucket.strain_name || bucket.strain?.name || "—"}</dd>
                    <dt className="text-muted-foreground">Growth Stage</dt>
                    <dd>{bucket.growth_stage}</dd>
                    <dt className="text-muted-foreground">Status</dt>
                    <dd>{bucket.status}</dd>
                    <dt className="text-muted-foreground">Last Water Change</dt>
                    <dd>{bucket.last_water_change_at ? formatShortDateTime(bucket.last_water_change_at) : "—"}</dd>
                  </dl>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Journal Tab */}
            <TabsContent value="journal" className="mt-4">
              {journal.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">No journal entries yet.</p>
              ) : (
                <div className="space-y-2 max-h-[60vh] overflow-y-auto">
                  {journal.map((entry) => (
                    <Card key={entry.id}>
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className="text-xs">{entry.event_type}</Badge>
                          <span className="text-xs text-muted-foreground">{formatShortDateTime(entry.created_at)}</span>
                        </div>
                        {entry.content && <p className="mt-1 text-sm">{entry.content}</p>}
                        {entry.payload && Object.keys(entry.payload).length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                            {Object.entries(entry.payload).map(([k, v]) => (
                              <span key={k} className="bg-muted px-1.5 py-0.5 rounded">{k}: {String(v)}</span>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Doses Tab */}
            <TabsContent value="doses" className="mt-4">
              {doses.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">No dose profiles configured.</p>
              ) : (
                <div className="space-y-2">
                  {doses.map((dose) => (
                    <Card key={dose.id}>
                      <CardContent className="p-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-medium text-sm">{dose.name}</span>
                            <Badge variant="outline" className="ml-2 text-xs">{dose.dose_type}</Badge>
                          </div>
                          <Badge variant={dose.enabled ? "default" : "secondary"}>
                            {dose.enabled ? "Active" : "Disabled"}
                          </Badge>
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">{dose.dose_ml} mL</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Photos Tab */}
            <TabsContent value="photos" className="mt-4">
              {photos.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4">No photos yet.</p>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {photos.map((photo) => (
                    <div key={photo.id} className="relative group">
                      <img
                        src={photo.url}
                        alt={photo.caption || "Bucket photo"}
                        className="w-full h-32 object-cover rounded-md border"
                      />
                      {photo.caption && (
                        <p className="text-xs text-muted-foreground mt-1 truncate">{photo.caption}</p>
                      )}
                      <p className="text-[10px] text-muted-foreground">{formatShortDateTime(photo.created_at)}</p>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
