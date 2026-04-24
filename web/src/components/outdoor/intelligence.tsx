"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  getGDD,
  getFrostDates,
  getMoonPhase,
  logManualWeather,
  type GDDResponse,
  type FrostDatesResponse,
  type MoonPhaseResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Thermometer,
  Snowflake,
  Moon,
  CloudRain,
  TrendingUp,
  MapPin,
  Droplets,
} from "lucide-react";

interface Props {
  growId: string;
  tentId: string;
}

export function OutdoorIntelligence({ growId, tentId }: Props) {
  const [gdd, setGdd] = useState<GDDResponse | null>(null);
  const [frost, setFrost] = useState<FrostDatesResponse | null>(null);
  const [moon, setMoon] = useState<MoonPhaseResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [rainDialog, setRainDialog] = useState(false);
  const [rainIn, setRainIn] = useState("");

  const refresh = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) return;
    try {
      const [g, f, m] = await Promise.all([
        getGDD(token, growId).catch(() => null),
        getFrostDates(token, tentId).catch(() => null),
        getMoonPhase(token, tentId).catch(() => null),
      ]);
      setGdd(g);
      setFrost(f);
      setMoon(m);
    } finally {
      setLoading(false);
    }
  }, [growId, tentId]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleLogRain = async () => {
    const token = await getAccessToken();
    if (!token || !rainIn) return;
    await logManualWeather(token, tentId, { rainfall_in: +rainIn });
    setRainDialog(false);
    setRainIn("");
    refresh();
  };

  if (loading) return <div className="flex justify-center py-8"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>;

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {/* GDD Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Thermometer className="size-4 text-orange-500" />
              Growing Degree Days
            </CardTitle>
          </CardHeader>
          <CardContent>
            {gdd ? (
              <div className="space-y-2">
                <p className="text-3xl font-bold">{gdd.accumulated_gdd}</p>
                {gdd.target_gdd && (
                  <>
                    <div className="h-2 w-full rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full bg-orange-500 transition-all"
                        style={{ width: `${Math.min(100, gdd.progress_pct ?? 0)}%` }}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {gdd.progress_pct?.toFixed(0)}% of {gdd.target_gdd} GDD target
                    </p>
                  </>
                )}
                {!gdd.target_gdd && (
                  <p className="text-xs text-muted-foreground">
                    Set a target GDD in grow settings for progress tracking
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No weather data yet. GDD accumulates from daily temperatures.</p>
            )}
          </CardContent>
        </Card>

        {/* Frost Calendar Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Snowflake className="size-4 text-blue-500" />
              Frost Calendar
            </CardTitle>
          </CardHeader>
          <CardContent>
            {frost ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Spring Frost</span>
                  <span className="font-medium">{frost.last_spring_frost}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">First Fall Frost</span>
                  <span className="font-medium">{frost.first_fall_frost}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Frost-Free Days</span>
                  <span className="font-medium">{frost.frost_free_days}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Hardiness Zone</span>
                  <Badge variant="outline">{frost.hardiness_zone}</Badge>
                </div>
              </div>
            ) : (
              <div className="space-y-2 text-sm text-muted-foreground">
                <MapPin className="size-8 text-muted-foreground/50" />
                <p>Set latitude/longitude on your garden to see frost dates.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Moon Phase Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              <Moon className="size-4 text-purple-500" />
              Moon Phase
            </CardTitle>
          </CardHeader>
          <CardContent>
            {moon ? (
              <div className="space-y-2 text-sm">
                <p className="text-xl font-bold">{moon.phase}</p>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Illumination</span>
                  <span className="font-medium">{moon.illumination_pct}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Next New Moon</span>
                  <span className="font-medium">{moon.days_until_new}d</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Next Full Moon</span>
                  <span className="font-medium">{moon.days_until_full}d</span>
                </div>
                <p className="rounded bg-muted p-2 text-xs">{moon.planting_recommendation}</p>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Unable to load moon phase data.</p>
            )}
          </CardContent>
        </Card>

        {/* Rain Tracker Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm">
              <CloudRain className="size-4 text-cyan-500" />
              Rain Tracker
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-muted-foreground">
              Track rainfall to optimize irrigation. Weather API data combined with manual gauge readings.
            </p>
            <Button size="sm" variant="outline" onClick={() => setRainDialog(true)}>
              <Droplets className="mr-1 size-3" /> Log Rain Gauge
            </Button>
          </CardContent>
        </Card>

        {/* GDD Daily Log (mini chart) */}
        {gdd && gdd.daily_log.length > 0 && (
          <Card className="sm:col-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm">
                <TrendingUp className="size-4 text-green-500" />
                GDD Accumulation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex h-24 items-end gap-0.5">
                {gdd.daily_log.slice(-30).map((d, i) => {
                  const maxGdd = Math.max(...gdd.daily_log.slice(-30).map((x) => x.gdd), 1);
                  const height = Math.max(2, (d.gdd / maxGdd) * 100);
                  return (
                    <div
                      key={i}
                      className="flex-1 rounded-t bg-orange-400 transition-all hover:bg-orange-500"
                      style={{ height: `${height}%` }}
                      title={`${d.date}: ${d.gdd} GDD (total: ${d.cumulative_gdd})`}
                    />
                  );
                })}
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                Last {Math.min(30, gdd.daily_log.length)} days · Total: {gdd.accumulated_gdd} GDD
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Rain gauge dialog */}
      <Dialog open={rainDialog} onOpenChange={setRainDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Rain Gauge Reading</DialogTitle></DialogHeader>
          <div>
            <Label>Rainfall (inches)</Label>
            <Input type="number" step="0.01" value={rainIn} onChange={(e) => setRainIn(e.target.value)} placeholder="e.g., 0.5" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRainDialog(false)}>Cancel</Button>
            <Button onClick={handleLogRain} disabled={!rainIn}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
