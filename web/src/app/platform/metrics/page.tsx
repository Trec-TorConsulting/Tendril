"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { apiFetch } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { DollarSign, TrendingUp, TrendingDown, Users, AlertTriangle } from "lucide-react";

interface RevenueMetrics {
  mrr_cents: number;
  arr_cents: number;
  total_subscribers: number;
  total_accounts: number;
  arpu_cents: number;
  plan_distribution: Record<string, number>;
  churn_rate_30d: number;
  new_subscribers_30d: number;
  cancelled_30d: number;
  dunning_accounts: number;
  conversion_rate: number;
}

function formatCurrency(cents: number): string {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

const PLAN_COLORS: Record<string, string> = {
  free: "bg-neutral-700",
  hobby: "bg-blue-600",
  pro: "bg-green-600",
  commercial: "bg-purple-600",
  enterprise: "bg-amber-600",
  dedicated: "bg-red-600",
};

export default function PlatformMetricsPage() {
  const [metrics, setMetrics] = useState<RevenueMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const token = getAccessToken();
      if (!token) return;
      try {
        const data = await apiFetch<RevenueMetrics>("/billing/metrics", { token });
        setMetrics(data);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Access denied — platform admin required");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading || !metrics) {
    return (
      <>
        <PageHeader
          title="Business Metrics"
          breadcrumbs={[
            { label: "Platform", href: "/platform" },
            { label: "Metrics" },
          ]}
        />
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-32" />)}
            </div>
          )}
        </div>
      </>
    );
  }

  const totalTenants = Object.values(metrics.plan_distribution).reduce((a, b) => a + b, 0);

  return (
    <>
      <PageHeader
        title="Business Metrics"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Metrics" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">MRR</CardTitle>
              <DollarSign className="size-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics.mrr_cents)}</div>
              <p className="text-xs text-muted-foreground">ARR: {formatCurrency(metrics.arr_cents)}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Subscribers</CardTitle>
              <Users className="size-4 text-blue-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_subscribers}</div>
              <p className="text-xs text-muted-foreground">+{metrics.new_subscribers_30d} this month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">ARPU</CardTitle>
              <TrendingUp className="size-4 text-purple-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics.arpu_cents)}</div>
              <p className="text-xs text-muted-foreground">per subscriber/month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Churn Rate</CardTitle>
              <TrendingDown className="size-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.churn_rate_30d > 5 ? "text-red-500" : ""}`}>
                {metrics.churn_rate_30d}%
              </div>
              <p className="text-xs text-muted-foreground">30-day rolling</p>
            </CardContent>
          </Card>
        </div>

        {/* Second Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Conversion Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.conversion_rate}%</div>
              <p className="text-xs text-muted-foreground">free → paid</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Accounts at Risk</CardTitle>
              <AlertTriangle className="size-4 text-amber-500" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.dunning_accounts > 0 ? "text-amber-500" : ""}`}>
                {metrics.dunning_accounts}
              </div>
              <p className="text-xs text-muted-foreground">in dunning / grace period</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Accounts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.total_accounts}</div>
              <p className="text-xs text-muted-foreground">{totalTenants} tenants</p>
            </CardContent>
          </Card>
        </div>

        {/* Plan Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Plan Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(metrics.plan_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([plan, count]) => {
                  const pct = totalTenants > 0 ? (count / totalTenants) * 100 : 0;
                  return (
                    <div key={plan} className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <span className="capitalize font-medium">{plan}</span>
                          <Badge variant="secondary" className="text-xs">{count}</Badge>
                        </div>
                        <span className="text-muted-foreground">{pct.toFixed(1)}%</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-muted">
                        <div
                          className={`h-full rounded-full ${PLAN_COLORS[plan] || "bg-neutral-600"}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
