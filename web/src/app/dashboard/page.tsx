"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { getAccessToken } from "@/lib/auth";
import { listGrows, listDevices, getHarvestCountdown, type GrowResponse, type DeviceResponse, type HarvestCountdownItem } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCalendarDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sprout, Cpu, Activity, Plus, ArrowRight, Timer } from "lucide-react";

export default function DashboardPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [countdown, setCountdown] = useState<HarvestCountdownItem[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [g, d, hc] = await Promise.all([
        listGrows(token),
        listDevices(token),
        getHarvestCountdown(token).catch(() => [] as HarvestCountdownItem[]),
      ]);
      setGrows(g);
      setDevices(d);
      setCountdown(hc);
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
          <Button render={<Link href="/dashboard/grows" />} size="sm">
            <Plus className="mr-1 size-4" />
            New Grow
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">
        {/* Stats Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
        </div>

        {/* Harvest Countdown */}
        {!loading && countdown.length > 0 && (
          <div>
            <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
              <Timer className="size-5" /> Harvest Countdown
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {countdown.map((item) => (
                <Card key={item.bucket_id} className={item.days_remaining <= 3 ? "border-orange-500/50" : item.days_remaining <= 0 ? "border-red-500/50" : ""}>
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
              ))}
            </div>
          </div>
        )}

        {/* Active Grows */}
        {!loading && activeGrows > 0 && (
          <div>
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
                  <Card key={g.id} className="transition-colors hover:border-primary/50">
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
                ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && grows.length === 0 && (
          <Card className="flex flex-col items-center justify-center py-16">
            <Sprout className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No grows yet</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Start tracking your first grow to see data here.
            </p>
            <Button className="mt-4" render={<Link href="/dashboard/grows" />}>
              <Plus className="mr-1 size-4" />
              Create Grow
            </Button>
          </Card>
        )}
      </div>
    </>
  );
}

function StatsCard({
  title,
  value,
  icon,
  loading,
}: {
  title: string;
  value?: string | number;
  icon: React.ReactNode;
  loading?: boolean;
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
          <div className="text-2xl font-bold">{value}</div>
        )}
      </CardContent>
    </Card>
  );
}
