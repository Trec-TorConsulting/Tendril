"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import {
  adminGetStats,
  adminListTenants,
  adminListUsers,
  adminUpdateUserFlags,
} from "@/lib/api";
import type { AdminTenantSummary, AdminUserSummary } from "@/lib/api";
import { Button } from "@/components/ui/button";

type Tab = "overview" | "tenants" | "users";

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [stats, setStats] = useState<{
    total_tenants: number;
    total_users: number;
    plans: Record<string, number>;
  } | null>(null);
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
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
      setTenants(t);
      setUsers(u);
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Access denied");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const toggleFlag = async (
    userId: string,
    flag: "is_platform_admin" | "is_support",
    current: boolean,
  ) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      let newRole: string;
      if (flag === "is_platform_admin") {
        newRole = current ? "user" : "super_admin";
      } else {
        newRole = current ? "user" : "support";
      }
      await adminUpdateUserFlags(token, userId, { platform_role: newRole });
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to update");
    }
  };

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white">Platform Admin</h1>
        <div className="rounded-md bg-red-900/50 p-4 text-red-300">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Platform Admin</h1>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-neutral-900 p-1 border border-neutral-800">
        {(["overview", "tenants", "users"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium capitalize transition ${
              tab === t
                ? "bg-green-900/40 text-green-400"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === "overview" && stats && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
              <p className="text-sm text-neutral-400">Total Organizations</p>
              <p className="text-3xl font-bold text-white">{stats.total_tenants}</p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
              <p className="text-sm text-neutral-400">Total Users</p>
              <p className="text-3xl font-bold text-white">{stats.total_users}</p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
              <p className="text-sm text-neutral-400">Plans</p>
              <div className="mt-2 space-y-1">
                {Object.entries(stats.plans).map(([plan, count]) => (
                  <div key={plan} className="flex justify-between text-sm">
                    <span className="text-neutral-300 capitalize">{plan}</span>
                    <span className="text-white font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tenants */}
      {tab === "tenants" && (
        <div className="space-y-3">
          {tenants.length === 0 ? (
            <p className="text-neutral-500">No tenants found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-800 text-left text-neutral-400">
                    <th className="pb-2 pr-4">Organization</th>
                    <th className="pb-2 pr-4">Slug</th>
                    <th className="pb-2 pr-4">Plan</th>
                    <th className="pb-2 pr-4">Users</th>
                    <th className="pb-2">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {tenants.map((t) => (
                    <tr key={t.id} className="border-b border-neutral-800/50">
                      <td className="py-2 pr-4 text-white">{t.name}</td>
                      <td className="py-2 pr-4 text-neutral-400">{t.slug}</td>
                      <td className="py-2 pr-4">
                        <span className="rounded bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300 capitalize">
                          {t.plan}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-white">{t.user_count}</td>
                      <td className="py-2 text-neutral-500">
                        {formatDate(t.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
