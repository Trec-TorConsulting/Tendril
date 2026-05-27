"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { adminListTenants, adminListTenantUsers, adminUpdateTenantPlan, adminListPlans, adminCreateTenant, adminDeleteTenant } from "@/lib/api";
import type { AdminTenantSummary, AdminUserSummary, AdminBillingPlan } from "@/lib/api";
import { cn, formatDate } from "@/lib/utils";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Building2, ChevronDown, CheckCircle, XCircle, Plus, Trash2 } from "lucide-react";

export default function PlatformTenantsPage() {
  const [tenants, setTenants] = useState<AdminTenantSummary[]>([]);
  const [plans, setPlans] = useState<AdminBillingPlan[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedUsers, setExpandedUsers] = useState<AdminUserSummary[]>([]);
  const [error, setError] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [createName, setCreateName] = useState("");
  const [createSlug, setCreateSlug] = useState("");
  const [createPlan, setCreatePlan] = useState("free");
  const [creating, setCreating] = useState(false);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [t, p] = await Promise.all([
        adminListTenants(token),
        adminListPlans(token),
      ]);
      setTenants(t);
      setPlans(p.filter((pl) => pl.is_active));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const toggleExpand = async (tenantId: string) => {
    if (expandedId === tenantId) {
      setExpandedId(null);
      setExpandedUsers([]);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    try {
      const users = await adminListTenantUsers(token, tenantId);
      setExpandedUsers(users);
      setExpandedId(tenantId);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load users");
    }
  };

  const changePlan = async (tenantId: string, newPlan: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminUpdateTenantPlan(token, tenantId, { plan: newPlan });
      setTenants((prev) =>
        prev.map((t) => (t.id === tenantId ? { ...t, plan: newPlan } : t)),
      );
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to update plan");
    }
  };

  const handleCreate = async () => {
    const token = getAccessToken();
    if (!token) return;
    setCreating(true);
    try {
      await adminCreateTenant(token, { name: createName, slug: createSlug, plan: createPlan });
      setCreateOpen(false);
      setCreateName("");
      setCreateSlug("");
      setCreatePlan("free");
      setError("");
      await refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create organization");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (tenantId: string, tenantName: string) => {
    if (!confirm(`Permanently delete "${tenantName}"?\n\nThis will remove the organization and all its data. This cannot be undone.`)) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminDeleteTenant(token, tenantId);
      setError("");
      await refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to delete organization");
    }
  };

  const slugify = (value: string) =>
    value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  return (
    <>
      <PageHeader
        title="Organizations"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Organizations" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{tenants.length} total</Badge>
            <Dialog open={createOpen} onOpenChange={setCreateOpen}>
              <DialogTrigger render={<Button size="sm"><Plus className="mr-1 size-4" />Add Organization</Button>} />
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Organization</DialogTitle>
                  <DialogDescription>
                    Add a new organization (tenant) to the platform.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="org-name">Name</Label>
                    <Input
                      id="org-name"
                      placeholder="Acme Corp"
                      value={createName}
                      onChange={(e) => {
                        setCreateName(e.target.value);
                        setCreateSlug(slugify(e.target.value));
                      }}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="org-slug">Slug</Label>
                    <Input
                      id="org-slug"
                      placeholder="acme-corp"
                      value={createSlug}
                      onChange={(e) => setCreateSlug(e.target.value)}
                    />
                    <p className="text-xs text-muted-foreground">URL-friendly identifier. Must be unique.</p>
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="org-plan">Plan</Label>
                    <Select value={createPlan} onValueChange={(v) => setCreatePlan(v ?? "")}>
                      <SelectTrigger id="org-plan">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {plans.map((p) => (
                          <SelectItem key={p.slug} value={p.slug}>{p.name}</SelectItem>
                        ))}
                        {plans.length === 0 && <SelectItem value="free">Free</SelectItem>}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancel</Button>
                  <Button onClick={handleCreate} disabled={creating || !createName || !createSlug}>
                    {creating ? "Creating…" : "Create"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-2">
          {tenants.length === 0 && !error && (
            <Card className="flex flex-col items-center justify-center py-16">
              <Building2 className="size-12 text-amber-500/50" />
              <h3 className="mt-4 text-lg font-semibold">No organizations</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Organizations will appear here once tenants are created.
              </p>
            </Card>
          )}

          {tenants.map((t) => (
            <Collapsible
              key={t.id}
              open={expandedId === t.id}
              onOpenChange={() => toggleExpand(t.id)}
            >
              <CollapsibleTrigger
                render={
                  <Card
                    className={cn(
                      "cursor-pointer transition hover:border-border/80",
                      expandedId === t.id && "border-amber-500/50",
                    )}
                  />
                }
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Building2 className="size-4 text-amber-500" />
                      <span className="font-medium">{t.name}</span>
                      <span className="text-sm text-muted-foreground">{t.slug}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Select
                        value={t.plan}
                        onValueChange={(value) => { if (value) changePlan(t.id, value); }}
                      >
                        <SelectTrigger className="h-7 w-[130px] text-xs" onClick={(e) => e.stopPropagation()}>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {plans.map((p) => (
                            <SelectItem key={p.slug} value={p.slug}>
                              {p.name}
                            </SelectItem>
                          ))}
                          {/* Always show current plan even if not in active plans */}
                          {!plans.some((p) => p.slug === t.plan) && (
                            <SelectItem value={t.plan}>
                              {t.plan} (current)
                            </SelectItem>
                          )}
                        </SelectContent>
                      </Select>
                      <span className="text-sm text-muted-foreground">{t.user_count} users</span>
                      <span className="text-sm text-muted-foreground">
                        {formatDate(t.created_at)}
                      </span>
                      <Button
                        size="sm"
                        variant="destructive"
                        className="h-7 px-2 text-xs"
                        onClick={(e) => { e.stopPropagation(); handleDelete(t.id, t.name); }}
                      >
                        <Trash2 className="size-3 mr-1" />
                        Delete
                      </Button>
                      <ChevronDown
                        className={cn(
                          "size-4 text-muted-foreground transition-transform",
                          expandedId === t.id && "rotate-180",
                        )}
                      />
                    </div>
                  </div>
                </CardContent>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <Card className="mx-4 rounded-t-none border-t-0">
                  <CardContent className="p-4">
                    <h3 className="mb-2 text-xs font-semibold text-muted-foreground">Members</h3>
                    {expandedUsers.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No users.</p>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Email</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Verified</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {expandedUsers.map((u) => (
                            <TableRow key={u.id}>
                              <TableCell>{u.email}</TableCell>
                              <TableCell className="text-muted-foreground">
                                {u.display_name || "—"}
                              </TableCell>
                              <TableCell>
                                <Badge variant="secondary">{u.role}</Badge>
                              </TableCell>
                              <TableCell>
                                {u.email_verified ? (
                                  <CheckCircle className="size-4 text-green-500" />
                                ) : (
                                  <XCircle className="size-4 text-muted-foreground" />
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </CardContent>
                </Card>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </div>
    </>
  );
}
