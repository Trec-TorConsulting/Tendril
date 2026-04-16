"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { getAccessToken } from "@/lib/auth";
import { listGrows, listDevices, type GrowResponse, type DeviceResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Sprout, Cpu, Activity, Plus, ArrowRight } from "lucide-react";

export default function DashboardPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [g, d] = await Promise.all([listGrows(token), listDevices(token)]);
      setGrows(g);
      setDevices(d);
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
