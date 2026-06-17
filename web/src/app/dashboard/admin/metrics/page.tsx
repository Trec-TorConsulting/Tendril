"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
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

export default function BusinessMetricsPage() {
  const [metrics, setMetrics] = useState<RevenueMetrics | null>(null);
  const [error, setError] = useState("");
  const { data, isLoading: loading, error: loadError } = useApiSWR(
    ["dashboard", "admin", "metrics"],
    (token) => apiFetch<RevenueMetrics>("/billing/metrics", { token }),
  );

  useEffect(() => {
    if (data) setMetrics(data);
  }, [data]);

  useEffect(() => {
    if (loadError) setError(loadError instanceof Error ? loadError.message : "Access denied — platform admin required");
  }, [loadError]);

  if (error) {
    return (
      <div className="space-y-4">
        <PageHeader title="Business Metrics" description="Revenue and growth analytics" />
        <div className="rounded-md bg-red-900/50 p-4 text-red-300">{error}</div>
      </div>
    );
  }

  if (loading || !metrics) {
    return (
      <div className="space-y-6">
        <PageHeader title="Business Metrics" description="Revenue and growth analytics" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  const totalTenants = Object.values(metrics.plan_distribution).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-6">
      <PageHeader title="Business Metrics" description="Revenue, growth, and subscription health" />

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">MRR</CardTitle>
            <DollarSign className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatCurrency(metrics.mrr_cents)}</p>
            <p className="text-xs text-neutral-500">ARR: {formatCurrency(metrics.arr_cents)}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Subscribers</CardTitle>
            <Users className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{metrics.total_subscribers}</p>
            <p className="text-xs text-neutral-500">+{metrics.new_subscribers_30d} this month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">ARPU</CardTitle>
            <TrendingUp className="h-4 w-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatCurrency(metrics.arpu_cents)}</p>
            <p className="text-xs text-neutral-500">per subscriber/month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Churn Rate</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${metrics.churn_rate_30d > 5 ? "text-red-400" : "text-white"}`}>
              {metrics.churn_rate_30d}%
            </p>
            <p className="text-xs text-neutral-500">30-day rolling</p>
          </CardContent>
        </Card>
      </div>

      {/* Second Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Conversion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{metrics.conversion_rate}%</p>
            <p className="text-xs text-neutral-500">free → paid</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Accounts at Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-400" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${metrics.dunning_accounts > 0 ? "text-amber-400" : "text-white"}`}>
              {metrics.dunning_accounts}
            </p>
            <p className="text-xs text-neutral-500">in dunning / grace period</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Total Accounts</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{metrics.total_accounts}</p>
            <p className="text-xs text-neutral-500">{totalTenants} tenants</p>
          </CardContent>
        </Card>
      </div>

      {/* Plan Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Plan Distribution</CardTitle>
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
                      <span className="capitalize text-white">{plan}</span>
                      <span className="text-neutral-400">{count} ({pct.toFixed(1)}%)</span>
                    </div>
                    <div className="h-2 rounded-full bg-neutral-800 overflow-hidden">
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
  );
}
