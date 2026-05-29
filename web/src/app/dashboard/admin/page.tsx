"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { formatDate } from "@/lib/utils";
import {
  adminGetStats,
  adminListTenants,
  adminListUsers,
  adminCreateTenant,
  adminUpdateTenantPlan,
  adminUpdateUserFlags,
  adminDeleteTenant,
  adminDeleteUser,
} from "@/lib/api";
import type { AdminTenantSummary, AdminUserSummary } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import {
  Building2,
  Users,
  BarChart3,
  Plus,
  Trash2,
  Search,
  Shield,
  ShieldAlert,
  X,
} from "lucide-react";

type Tab = "overview" | "tenants" | "users";
const PLANS = ["free", "hobby", "pro", "commercial", "enterprise", "dedicated"] as const;

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>("overview");
  const [stats, setStats] = useState<{
    total_tenants: number;
    total_users: number;
    plans: Record<string, number>;
  } | null>(null);
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Search / filter
  const [tenantSearch, setTenantSearch] = useState("");
  const [userSearch, setUserSearch] = useState("");

  // Create tenant form
  const [showCreateTenant, setShowCreateTenant] = useState(false);
  const [newTenantName, setNewTenantName] = useState("");
  const [newTenantSlug, setNewTenantSlug] = useState("");
  const [newTenantPlan, setNewTenantPlan] = useState("free");

  // Inline plan editing
  const [editingPlan, setEditingPlan] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setLoading(true);
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
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // ── Tenant Actions ──

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminCreateTenant(token, {
        name: newTenantName,
        slug: newTenantSlug,
        plan: newTenantPlan,
      });
      toast.success(`Organization "${newTenantName}" created`);
      setShowCreateTenant(false);
      setNewTenantName("");
      setNewTenantSlug("");
      setNewTenantPlan("free");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to create organization");
    }
  };

  const handleUpdatePlan = async (tenantId: string, plan: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminUpdateTenantPlan(token, tenantId, { plan });
      toast.success("Plan updated");
      setEditingPlan(null);
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to update plan");
    }
  };

  const handleDeleteTenant = async (tenantId: string, tenantName: string) => {
    if (!confirm(`Schedule deletion of "${tenantName}"?\n\nData will be permanently purged after 30 days.`)) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      const res = await adminDeleteTenant(token, tenantId);
      toast.success(res.message);
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to delete organization");
    }
  };

  // ── User Actions ──

  const handleChangeRole = async (userId: string, newRole: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminUpdateUserFlags(token, userId, { platform_role: newRole });
      toast.success("Role updated");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to update role");
    }
  };

  const handleDeleteUser = async (userId: string, email: string) => {
    if (!confirm(`Delete user "${email}"?\n\nThis removes the user and all their memberships. This cannot be undone.`)) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      const res = await adminDeleteUser(token, userId);
      toast.success(res.message);
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to delete user");
    }
  };

  // ── Filtered data ──

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(tenantSearch.toLowerCase()) ||
      t.slug.toLowerCase().includes(tenantSearch.toLowerCase()) ||
      t.plan.toLowerCase().includes(tenantSearch.toLowerCase()),
  );

  const filteredUsers = users.filter(
    (u) =>
      u.email.toLowerCase().includes(userSearch.toLowerCase()) ||
      (u.display_name || "").toLowerCase().includes(userSearch.toLowerCase()) ||
      (u.tenant_name || "").toLowerCase().includes(userSearch.toLowerCase()),
  );

  // ── Render ──

  if (error && !stats) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-white">Platform Admin</h1>
        <div className="rounded-md bg-red-900/50 p-4 text-red-300">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Platform Admin</h1>
        {error && <span className="text-sm text-red-400">{error}</span>}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-neutral-900 p-1 border border-neutral-800">
        {([
          { key: "overview" as Tab, icon: BarChart3, label: "Overview" },
          { key: "tenants" as Tab, icon: Building2, label: "Organizations" },
          { key: "users" as Tab, icon: Users, label: "Users" },
        ]).map(({ key, icon: Icon, label }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex-1 flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition ${
              tab === key
                ? "bg-green-900/40 text-green-400"
                : "text-neutral-400 hover:text-white"
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ═══════════════ Overview Tab ═══════════════ */}
      {tab === "overview" && stats && (
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-5">
              <div className="flex items-center gap-2 mb-2">
                <Building2 className="h-4 w-4 text-green-400" />
                <p className="text-sm text-neutral-400">Organizations</p>
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_tenants}</p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-5">
              <div className="flex items-center gap-2 mb-2">
                <Users className="h-4 w-4 text-blue-400" />
                <p className="text-sm text-neutral-400">Users</p>
              </div>
              <p className="text-3xl font-bold text-white">{stats.total_users}</p>
            </div>
            <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-5">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="h-4 w-4 text-purple-400" />
                <p className="text-sm text-neutral-400">Plan Distribution</p>
              </div>
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

          {/* Quick Links */}
          <div className="grid gap-3 sm:grid-cols-2">
            <a href="/dashboard/admin/config" className="rounded-lg border border-neutral-800 bg-neutral-900 p-4 hover:border-green-800 transition">
              <p className="font-medium text-white">Config Management</p>
              <p className="text-sm text-neutral-400 mt-1">Grow type configs, task templates, system settings</p>
            </a>
            <a href="/dashboard/admin/providers" className="rounded-lg border border-neutral-800 bg-neutral-900 p-4 hover:border-green-800 transition">
              <p className="font-medium text-white">Payment Providers</p>
              <p className="text-sm text-neutral-400 mt-1">Manage billing providers and webhooks</p>
            </a>
          </div>
        </div>
      )}

      {/* ═══════════════ Tenants Tab ═══════════════ */}
      {tab === "tenants" && (
        <div className="space-y-4">
          {/* Toolbar */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
              <Input
                placeholder="Search organizations..."
                value={tenantSearch}
                onChange={(e) => setTenantSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Button size="sm" onClick={() => setShowCreateTenant(!showCreateTenant)}>
              {showCreateTenant ? <X className="h-4 w-4 mr-1" /> : <Plus className="h-4 w-4 mr-1" />}
              {showCreateTenant ? "Cancel" : "Create Organization"}
            </Button>
          </div>

          {/* Create Tenant Form */}
          {showCreateTenant && (
            <form
              onSubmit={handleCreateTenant}
              className="rounded-lg border border-neutral-800 bg-neutral-900 p-4 space-y-3"
            >
              <h3 className="text-sm font-medium text-white">New Organization</h3>
              <div className="grid gap-3 sm:grid-cols-3">
                <Input
                  placeholder="Organization Name"
                  value={newTenantName}
                  onChange={(e) => {
                    setNewTenantName(e.target.value);
                    setNewTenantSlug(e.target.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));
                  }}
                  required
                />
                <Input
                  placeholder="slug (auto-generated)"
                  value={newTenantSlug}
                  onChange={(e) => setNewTenantSlug(e.target.value)}
                  required
                />
                <select
                  className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
                  value={newTenantPlan}
                  onChange={(e) => setNewTenantPlan(e.target.value)}
                >
                  {PLANS.map((p) => (
                    <option key={p} value={p}>
                      {p.charAt(0).toUpperCase() + p.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <Button type="submit" size="sm">
                Create
              </Button>
            </form>
          )}

          {/* Tenants Table */}
          {filteredTenants.length === 0 ? (
            <p className="text-neutral-500 text-sm py-4">
              {tenantSearch ? "No organizations match your search." : "No organizations found."}
            </p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-800">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-neutral-900/50 text-left text-neutral-400 border-b border-neutral-800">
                    <th className="px-4 py-3">Organization</th>
                    <th className="px-4 py-3">Slug</th>
                    <th className="px-4 py-3">Plan</th>
                    <th className="px-4 py-3">Users</th>
                    <th className="px-4 py-3">Created</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTenants.map((t) => (
                    <tr key={t.id} className="border-b border-neutral-800/50 hover:bg-neutral-900/30">
                      <td className="px-4 py-3">
                        <span className="text-white font-medium">{t.name}</span>
                      </td>
                      <td className="px-4 py-3 text-neutral-400 font-mono text-xs">{t.slug}</td>
                      <td className="px-4 py-3">
                        {editingPlan === t.id ? (
                          <select
                            className="rounded border border-neutral-700 bg-neutral-800 px-2 py-1 text-xs text-white"
                            defaultValue={t.plan}
                            onChange={(e) => handleUpdatePlan(t.id, e.target.value)}
                            onBlur={() => setEditingPlan(null)}
                            autoFocus
                          >
                            {PLANS.map((p) => (
                              <option key={p} value={p}>
                                {p}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <button
                            onClick={() => setEditingPlan(t.id)}
                            className="rounded bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300 capitalize hover:bg-neutral-700 hover:text-white transition"
                            title="Click to change plan"
                          >
                            {t.plan}
                          </button>
                        )}
                      </td>
                      <td className="px-4 py-3 text-white">{t.user_count}</td>
                      <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(t.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteTenant(t.id, t.name)}
                          className="h-7 px-2 text-xs"
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-xs text-neutral-500">
            {filteredTenants.length} of {tenants.length} organizations
          </p>
        </div>
      )}

      {/* ═══════════════ Users Tab ═══════════════ */}
      {tab === "users" && (
        <div className="space-y-4">
          {/* Toolbar */}
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
            <Input
              placeholder="Search users by email, name, or org..."
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Users Table */}
          {filteredUsers.length === 0 ? (
            <p className="text-neutral-500 text-sm py-4">
              {userSearch ? "No users match your search." : "No users found."}
            </p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-neutral-800">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-neutral-900/50 text-left text-neutral-400 border-b border-neutral-800">
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3">Organization</th>
                    <th className="px-4 py-3">Platform Role</th>
                    <th className="px-4 py-3">Verified</th>
                    <th className="px-4 py-3">Joined</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((u) => (
                    <tr key={u.id} className="border-b border-neutral-800/50 hover:bg-neutral-900/30">
                      <td className="px-4 py-3">
                        <div>
                          <p className="text-white font-medium text-xs">{u.email}</p>
                          {u.display_name && (
                            <p className="text-neutral-500 text-xs">{u.display_name}</p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-neutral-400 text-xs">
                        {u.tenant_name || "—"}
                        {u.role && (
                          <span className="ml-1 text-neutral-600">({u.role})</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <select
                          className="rounded border border-neutral-700 bg-neutral-800 px-2 py-1 text-xs text-white"
                          value={u.is_platform_admin ? "super_admin" : u.is_support ? "support" : "user"}
                          onChange={(e) => handleChangeRole(u.id, e.target.value)}
                        >
                          <option value="user">User</option>
                          <option value="support">Support</option>
                          <option value="super_admin">Super Admin</option>
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        {u.email_verified ? (
                          <span className="inline-flex items-center gap-1 rounded bg-green-900/30 px-2 py-0.5 text-xs text-green-400">
                            <Shield className="h-3 w-3" /> Yes
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 rounded bg-yellow-900/30 px-2 py-0.5 text-xs text-yellow-400">
                            <ShieldAlert className="h-3 w-3" /> No
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-neutral-500 text-xs">{formatDate(u.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteUser(u.id, u.email)}
                          className="h-7 px-2 text-xs"
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-xs text-neutral-500">
            {filteredUsers.length} of {users.length} users
          </p>
        </div>
      )}

      {/* Loading overlay */}
      {loading && !stats && (
        <div className="flex items-center justify-center py-12">
          <div className="text-neutral-500 text-sm">Loading platform data...</div>
        </div>
      )}
    </div>
  );
}
