"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listGrows, listBuckets, type GrowResponse, type BucketResponse } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { BarChart3, Sprout, CheckCircle2, Activity } from "lucide-react";

export default function AnalyticsPage() {
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const g = await listGrows(token);
      setGrows(g);
      if (g.length > 0) {
        const bkts = await listBuckets(token, g[0].id);
        setBuckets(bkts);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const activeGrows = grows.filter((g) => g.status === "active").length;
  const completedGrows = grows.filter((g) => g.status === "completed").length;

  const stats = [
    { label: "Active Grows", value: activeGrows, icon: Sprout },
    { label: "Completed", value: completedGrows, icon: CheckCircle2 },
    { label: "Total Grows", value: grows.length, icon: BarChart3 },
    { label: "Active Buckets", value: buckets.length, icon: Activity },
  ];

  return (
    <>
      <PageHeader
        title="Analytics"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Analytics" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <Card key={s.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{s.label}</CardTitle>
                <s.icon className="size-4 text-primary" />
              </CardHeader>
              <CardContent>
                {loading ? <Skeleton className="h-8 w-16" /> : <div className="text-2xl font-bold">{s.value}</div>}
              </CardContent>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Charts & Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Detailed sensor charts, yield trends, and strain comparisons will be available here.
              Connect sensors and complete harvests to populate analytics.
            </p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
