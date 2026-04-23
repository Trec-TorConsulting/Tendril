"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getAccessToken } from "@/lib/auth";
import { getTent, listGrows, listSchedules, listDevices, type TentResponse, type GrowResponse, type ScheduleResponse, type DeviceResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCalendarDate } from "@/lib/utils";
import { Warehouse, MapPin, Camera, Sprout, Calendar, Cpu, Lightbulb, Fan, Snowflake, Droplets, Settings, ArrowRight } from "lucide-react";

const EQUIPMENT_LABELS: Record<string, string> = {
  grow_light: "Grow Light",
  exhaust_fan: "Exhaust Fan",
  inline_fan: "Inline Fan",
  oscillating_fan: "Oscillating Fan",
  air_pump: "Air Pump",
  water_pump: "Water / Circulation Pump",
  water_chiller: "Water Chiller",
  carbon_filter: "Carbon Filter",
  humidifier: "Humidifier",
  dehumidifier: "Dehumidifier",
  heater: "Heater",
  ac_unit: "AC Unit",
  co2_system: "CO₂ System",
  controller: "Controller / Automation",
  custom: "Other",
};

const scheduleTypeIcon: Record<string, React.ReactNode> = {
  light: <Lightbulb className="size-4" />,
  fan: <Fan className="size-4" />,
  hvac: <Snowflake className="size-4" />,
  pump: <Droplets className="size-4" />,
};

export default function TentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [tent, setTent] = useState<TentResponse | null>(null);
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [schedules, setSchedules] = useState<ScheduleResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [t, g, s, d] = await Promise.all([
        getTent(token, id),
        listGrows(token, { tent_id: id }),
        listSchedules(token, id).catch(() => [] as ScheduleResponse[]),
        listDevices(token).catch(() => [] as DeviceResponse[]),
      ]);
      setTent(t);
      setGrows(g);
      setSchedules(s);
      setDevices(d.filter((dev) => dev.tent_id === id));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (loading) return <PageSkeleton rows={4} cards />;
  if (!tent) return <p className="p-6 text-muted-foreground">Grow space not found.</p>;

  const activeGrows = grows.filter((g) => g.status === "active");
  const pastGrows = grows.filter((g) => g.status !== "active");
  const hasCamera = !!tent.camera_url;

  return (
    <>
      <PageHeader
        title={tent.name}
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Grow Spaces", href: "/dashboard/tents" },
          { label: tent.name },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Info + Camera */}
        <div className={`grid gap-4 ${hasCamera ? "lg:grid-cols-[1fr_auto]" : ""}`}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Warehouse className="size-4" /> Space Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary" className="capitalize">{tent.environment_type}</Badge>
                {tent.size && <Badge variant="outline">{tent.size}</Badge>}
              </div>
              {(tent.latitude || tent.longitude) && (
                <p className="flex items-center gap-1 text-sm text-muted-foreground">
                  <MapPin className="size-3" />
                  {tent.latitude?.toFixed(4)}, {tent.longitude?.toFixed(4)}
                </p>
              )}
              {tent.notes && (
                <p className="text-sm text-muted-foreground whitespace-pre-line">{tent.notes}</p>
              )}
            </CardContent>
          </Card>

          {hasCamera && (
            <Card className="overflow-hidden lg:w-72">
              <div className="relative aspect-video bg-black">
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1"}/tents/${tent.id}/camera-snapshot?token=${encodeURIComponent(getAccessToken() || "")}&t=${Date.now()}`}
                  alt="Camera snapshot"
                  className="size-full object-cover"
                />
                <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] text-white">
                  <Camera className="size-3" /> Live
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Equipment */}
        {tent.equipment && tent.equipment.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Settings className="size-4" /> Equipment
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {tent.equipment.map((e, i) => (
                  <div key={i} className="flex items-center gap-3 rounded-lg border p-3">
                    <Fan className="size-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium">
                        {e.quantity > 1 ? `${e.quantity}× ` : ""}{EQUIPMENT_LABELS[e.type] || e.type}
                      </p>
                      {(e.brand || e.model) && (
                        <p className="text-xs text-muted-foreground truncate">
                          {[e.brand, e.model].filter(Boolean).join(" · ")}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Active Grows */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-base">
              <Sprout className="size-4" /> Grows in this Space
            </CardTitle>
            {grows.length > 0 && (
              <Button variant="ghost" size="sm" render={<Link href="/dashboard/grows" />}>
                All Grows <ArrowRight className="ml-1 size-3" />
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {grows.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Sprout className="size-8 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">No grows in this space yet.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {activeGrows.map((g) => (
                  <Link key={g.id} href={`/dashboard/grows/${g.id}`} className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50">
                    <div>
                      <p className="font-medium">{g.name}</p>
                      <p className="text-xs text-muted-foreground">{g.grow_type} · Stage: {g.stage} · Started {formatCalendarDate(g.started_at)}</p>
                    </div>
                    <Badge variant="default">{g.status}</Badge>
                  </Link>
                ))}
                {pastGrows.length > 0 && (
                  <>
                    <p className="pt-2 text-xs font-medium text-muted-foreground">Past ({pastGrows.length})</p>
                    {pastGrows.slice(0, 5).map((g) => (
                      <Link key={g.id} href={`/dashboard/grows/${g.id}`} className="flex items-center justify-between rounded-lg border p-3 opacity-60 transition-colors hover:bg-muted/50">
                        <div>
                          <p className="font-medium">{g.name}</p>
                          <p className="text-xs text-muted-foreground">{g.grow_type}</p>
                        </div>
                        <Badge variant="secondary">{g.status}</Badge>
                      </Link>
                    ))}
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Schedules */}
        {schedules.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Calendar className="size-4" /> Schedules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {schedules.map((s) => (
                  <div key={s.id} className="flex items-center gap-3 rounded-lg border p-3">
                    {scheduleTypeIcon[s.schedule_type] || <Settings className="size-4" />}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{s.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {s.on_time} → {s.off_time}
                        {s.stage && ` · ${s.stage}`}
                      </p>
                    </div>
                    <Badge variant={s.enabled ? "default" : "outline"} className="text-xs">
                      {s.enabled ? "On" : "Off"}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Devices */}
        {devices.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="size-4" /> Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2 sm:grid-cols-2">
                {devices.map((d) => (
                  <div key={d.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="text-sm font-medium">{d.label || d.device_id}</p>
                      {d.firmware_version && (
                        <p className="text-xs text-muted-foreground">FW {d.firmware_version}</p>
                      )}
                    </div>
                    <Badge variant={d.status === "online" ? "default" : "outline"} className="text-xs">
                      {d.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
