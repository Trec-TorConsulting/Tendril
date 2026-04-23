"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { getAccessToken } from "@/lib/auth";
import { listGrows, listDevices, listTents, getHarvestCountdown, getTent, listSensorReadings, listTentReadings, type GrowResponse, type DeviceResponse, type HarvestCountdownItem, type TentResponse, type SensorReadingResponse, type TentReadingResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { OnboardingChecklist } from "@/components/onboarding-checklist";
import { SensorSparkline } from "@/components/sparkline";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCalendarDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sprout, Cpu, Activity, Plus, ArrowRight, Timer, Camera, ChevronRight, Settings2, Thermometer, Droplets } from "lucide-react";
import { PullToRefresh } from "@/components/pull-to-refresh";
import { useWidgetLayout, type WidgetId } from "@/hooks/use-widget-layout";
import { CustomizeWidgetsDialog } from "@/components/customize-widgets-dialog";

export default function DashboardPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [countdown, setCountdown] = useState<HarvestCountdownItem[]>([]);
  const [heroTent, setHeroTent] = useState<TentResponse | null>(null);
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [customizeOpen, setCustomizeOpen] = useState(false);
  const [sensorTrends, setSensorTrends] = useState<{ ph: number[]; ec: number[]; temp: number[]; humidity: number[] }>({ ph: [], ec: [], temp: [], humidity: [] });
  const { widgets, toggle, moveUp, moveDown, reset, isVisible } = useWidgetLayout();

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [g, d, hc] = await Promise.all([
        listGrows(token),
        listDevices(token),
        getHarvestCountdown(token).catch(() => [] as HarvestCountdownItem[]),
      ]);
      const t = await listTents(token).catch(() => [] as TentResponse[]);
      setGrows(g);
      setDevices(d);
      setCountdown(hc);
      setTents(t);
      // Fetch tent for the primary active grow (hero card camera)
      const primaryGrow = g.find((gr) => gr.status === "active");
      if (primaryGrow) {
        try { setHeroTent(await getTent(token, primaryGrow.tent_id)); } catch { setHeroTent(null); }
      }
      // Fetch sensor trends for sparklines (last 50 readings)
      try {
        const [sensorReadings, tentReadings] = await Promise.all([
          listSensorReadings(token, undefined, 50).catch(() => [] as SensorReadingResponse[]),
          listTentReadings(token, undefined, 50).catch(() => [] as TentReadingResponse[]),
        ]);
        const phVals = sensorReadings.map((r) => r.ph).filter((v): v is number => v != null).reverse();
        const ecVals = sensorReadings.map((r) => r.ec).filter((v): v is number => v != null).reverse();
        const tempVals = tentReadings.map((r) => r.ambient_temp_f).filter((v): v is number => v != null).reverse();
        const humVals = tentReadings.map((r) => r.ambient_humidity).filter((v): v is number => v != null).reverse();
        setSensorTrends({ ph: phVals, ec: ecVals, temp: tempVals, humidity: humVals });
      } catch { /* non-critical */ }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const activeGrows = grows.filter((g) => g.status === "active").length;
  const devicesOnline = devices.filter((d) => d.status === "online").length;

  return (
    <>
      <PageHeader
        title="Dashboard"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setCustomizeOpen(true)}>
              <Settings2 className="mr-1 size-4" />
              Customize
            </Button>
            <Button render={<Link href="/dashboard/grows" />} size="sm">
              <Plus className="mr-1 size-4" />
              New Grow
            </Button>
          </div>
        }
      />
      <PullToRefresh onRefresh={refresh}>
      <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
        {widgets.map((w) => {
          if (!w.visible) return null;
          switch (w.id) {
            case "stats":
              return (
                <div key="stats" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <StatsCard
                    title="Active Grows"
                    value={loading ? undefined : activeGrows}
                    icon={<Sprout className="size-4 text-primary" />}
                    loading={loading}
                  />
                  <StatsCard
                    title="Devices Online"
                    value={loading ? undefined : `${devicesOnline} / ${devices.length}`}
                    icon={<Cpu className="size-4 text-primary" />}
                    loading={loading}
                  />
                  <StatsCard
                    title="Total Grows"
                    value={loading ? undefined : grows.length}
                    icon={<Activity className="size-4 text-primary" />}
                    loading={loading}
                  />
                  {sensorTrends.ph.length >= 2 && (
                    <StatsCard
                      title="pH Trend"
                      value={sensorTrends.ph[sensorTrends.ph.length - 1]?.toFixed(1)}
                      icon={<Droplets className="size-4 text-primary" />}
                      sparklineData={sensorTrends.ph}
                      sparklineRanges={{ min: 5.5, max: 6.5 }}
                    />
                  )}
                  {sensorTrends.ec.length >= 2 && (
                    <StatsCard
                      title="EC Trend"
                      value={sensorTrends.ec[sensorTrends.ec.length - 1]?.toFixed(2)}
                      icon={<Activity className="size-4 text-primary" />}
                      sparklineData={sensorTrends.ec}
                      sparklineRanges={{ min: 1.0, max: 2.5 }}
                    />
                  )}
                  {sensorTrends.temp.length >= 2 && (
                    <StatsCard
                      title="Temp Trend"
                      value={`${sensorTrends.temp[sensorTrends.temp.length - 1]?.toFixed(0)}°F`}
                      icon={<Thermometer className="size-4 text-primary" />}
                      sparklineData={sensorTrends.temp}
                      sparklineRanges={{ min: 68, max: 82 }}
                    />
                  )}
                </div>
              );

            case "hero":
              if (loading) return null;
              const primaryGrow = grows.find((g) => g.status === "active");
              if (!primaryGrow) return null;
              const hasCamera = heroTent?.camera_url;
              const daysSinceStart = Math.floor((Date.now() - new Date(primaryGrow.started_at).getTime()) / 86400000);
              const heroCountdown = countdown.find((c) => c.grow_id === primaryGrow.id);
              return (
                <Link key="hero" href={`/dashboard/grows/${primaryGrow.id}`}>
                  <motion.div whileTap={{ scale: 0.99 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
                    <Card className="overflow-hidden border-primary/20 hover:border-primary/40 transition-colors cursor-pointer">
                      <div className={hasCamera ? "grid md:grid-cols-[1fr_auto]" : ""}>
                        <CardContent className="p-5">
                          <div className="flex items-center gap-2 mb-3">
                            <Badge variant="default" className="text-xs capitalize">{primaryGrow.stage}</Badge>
                            <span className="text-xs text-muted-foreground">Day {daysSinceStart}</span>
                            {heroCountdown && heroCountdown.days_remaining > 0 && (
                              <Badge variant="outline" className="text-xs ml-auto">
                                <Timer className="mr-1 size-3" /> {heroCountdown.days_remaining}d to harvest
                              </Badge>
                            )}
                            {heroCountdown && heroCountdown.days_remaining <= 0 && (
                              <Badge variant="destructive" className="text-xs ml-auto">Ready to harvest!</Badge>
                            )}
                          </div>
                          <h2 className="text-xl font-bold">{primaryGrow.name}</h2>
                          <p className="mt-1 text-sm text-muted-foreground">
                            {heroTent?.name || "—"} · {primaryGrow.grow_type}
                          </p>
                          <div className="mt-4 flex items-center gap-1 text-sm text-primary font-medium">
                            View grow <ChevronRight className="size-4" />
                          </div>
                        </CardContent>
                        {hasCamera && (
                          <div className="relative h-48 md:h-auto md:w-64 bg-black overflow-hidden">
                            <img
                              src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1"}/tents/${primaryGrow.tent_id}/camera-snapshot?token=${encodeURIComponent(getAccessToken() || "")}&t=${Date.now()}`}
                              alt="Live camera"
                              className="size-full object-cover opacity-90"
                            />
                            <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-[10px] text-white">
                              <Camera className="size-3" /> Live
                            </div>
                          </div>
                        )}
                      </div>
                    </Card>
                  </motion.div>
                </Link>
              );

            case "countdown":
              if (loading || countdown.length === 0) return null;
              return (
                <div key="countdown">
                  <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
                    <Timer className="size-5" /> Harvest Countdown
                  </h2>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {countdown.map((item) => (
                      <motion.div key={item.bucket_id} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
                      <Link href={`/dashboard/grows/${item.grow_id}`}>
                      <Card className={`transition-colors hover:border-primary/50 cursor-pointer ${item.days_remaining <= 3 ? "border-orange-500/50" : item.days_remaining <= 0 ? "border-red-500/50" : ""}`}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{item.strain_name}</p>
                              <p className="text-xs text-muted-foreground">
                                {item.grow_name} — {item.bucket_label || "Bucket"}
                              </p>
                            </div>
                            <Badge variant={item.days_remaining <= 0 ? "destructive" : item.days_remaining <= 3 ? "secondary" : "outline"}>
                              {item.days_remaining <= 0 ? "Ready!" : `${item.days_remaining}d`}
                            </Badge>
                          </div>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {item.flowering_days}d flower cycle — est. {formatCalendarDate(item.estimated_harvest)}
                          </p>
                        </CardContent>
                      </Card>
                      </Link>
                      </motion.div>
                    ))}
                  </div>
                </div>
              );

            case "active-grows":
              if (loading || activeGrows === 0) return null;
              return (
                <div key="active-grows">
                  <div className="mb-3 flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Active Grows</h2>
                    <Button variant="ghost" size="sm" render={<Link href="/dashboard/grows" />}>
                      View all <ArrowRight className="ml-1 size-4" />
                    </Button>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {grows
                      .filter((g) => g.status === "active")
                      .slice(0, 6)
                      .map((g) => (
                        <motion.div key={g.id} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
                        <Card className="transition-colors hover:border-primary/50">
                          <Link href={`/dashboard/grows/${g.id}`} className="block p-4">
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="font-medium">{g.name}</h3>
                                <p className="mt-1 text-sm text-muted-foreground">{g.grow_type}</p>
                              </div>
                              <Badge variant="secondary">{g.stage}</Badge>
                            </div>
                          </Link>
                        </Card>
                        </motion.div>
                      ))}
                  </div>
                </div>
              );

            default:
              return null;
          }
        })}

        {/* Onboarding / Empty State */}
        {!loading && (grows.length === 0 || tents.length === 0 || devices.length === 0) && (
          <OnboardingChecklist
            hasTents={tents.length > 0}
            hasGrows={grows.length > 0}
            hasDevices={devices.length > 0}
          />
        )}
      </div>
      </PullToRefresh>

      <CustomizeWidgetsDialog
        open={customizeOpen}
        onOpenChange={setCustomizeOpen}
        widgets={widgets}
        toggle={toggle}
        moveUp={moveUp}
        moveDown={moveDown}
        reset={reset}
      />
    </>
  );
}

function StatsCard({
  title,
  value,
  icon,
  loading,
  sparklineData,
  sparklineRanges,
}: {
  title: string;
  value?: string | number;
  icon: React.ReactNode;
  loading?: boolean;
  sparklineData?: number[];
  sparklineRanges?: { min: number; max: number };
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="flex items-end justify-between gap-3">
            <div className="text-2xl font-bold">{value}</div>
            {sparklineData && sparklineData.length >= 2 && (
              <SensorSparkline data={sparklineData} ranges={sparklineRanges} height={28} className="w-24 shrink-0" />
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
