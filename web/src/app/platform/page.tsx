"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { adminGetStats, adminListTenants, adminListUsers } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Building2, Users, CreditCard } from "lucide-react";
import { formatDate } from "@/lib/utils";

export default function PlatformOverviewPage() {
  const [stats, setStats] = useState<{
    total_tenants: number;
    total_users: number;
    plans: Record<string, number>;
  } | null>(null);
  const [recentTenants, setRecentTenants] = useState<
    Array<{ name: string; plan: string; user_count: number; created_at: string }>
  >([]);
  const [recentUsers, setRecentUsers] = useState<
    Array<{ email: string; display_name: string | null; tenant_name: string; created_at: string }>
  >([]);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [s, t, u] = await Promise.all([
        adminGetStats(token),
        adminListTenants(token),
        adminListUsers(token),
      ]);
      setStats(s);
      setRecentTenants(t.slice(0, 5));
      setRecentUsers(u.slice(0, 10));
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (error) {
    return (
      <div className="p-4 lg:p-6">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
      <h1 className="text-2xl font-bold">Platform Overview</h1>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Organizations</CardTitle>
            <Building2 className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="text-3xl font-bold">{stats.total_tenants}</div>
            ) : (
              <Skeleton className="h-9 w-16" />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Users</CardTitle>
            <Users className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="text-3xl font-bold">{stats.total_users}</div>
            ) : (
              <Skeleton className="h-9 w-16" />
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Plans</CardTitle>
            <CreditCard className="size-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="space-y-1">
                {Object.entries(stats.plans).map(([plan, count]) => (
                  <div key={plan} className="flex justify-between text-sm">
                    <span className="capitalize text-muted-foreground">{plan}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <Skeleton className="h-9 w-full" />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent Organizations</CardTitle>
          </CardHeader>
          <CardContent>
            {recentTenants.length === 0 ? (
              <p className="text-sm text-muted-foreground">No organizations yet.</p>
            ) : (
              <div className="space-y-3">
                {recentTenants.map((t, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{t.name}</span>
                      <Badge variant="outline" className="capitalize text-xs">{t.plan}</Badge>
                    </div>
                    <span className="text-muted-foreground">
                      {formatDate(t.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent Users</CardTitle>
          </CardHeader>
          <CardContent>
            {recentUsers.length === 0 ? (
              <p className="text-sm text-muted-foreground">No users yet.</p>
            ) : (
              <div className="space-y-3">
                {recentUsers.map((u, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="font-medium">{u.display_name || u.email}</span>
                      <span className="ml-2 text-muted-foreground">{u.tenant_name}</span>
                    </div>
                    <span className="text-muted-foreground">
                      {formatDate(u.created_at)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
