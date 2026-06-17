"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  adminListPlans,
  adminCreatePlan,
  adminUpdatePlan,
  adminArchivePlan,
  adminSyncPlan,
} from "@/lib/api";
import type { AdminBillingPlan } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
  CreditCard,
  Plus,
  Pencil,
  Archive,
  RefreshCw,
  Check,
  X,
  Loader2,
} from "lucide-react";
import { useApiSWR } from "@/lib/swr";

const LIMIT_FIELDS = [
  { key: "max_grows", label: "Grows" },
  { key: "max_devices", label: "Devices" },
  { key: "max_team_members", label: "Team Members" },
  { key: "max_ai_analyses_month", label: "AI Analyses/mo" },
  { key: "max_storage_gb", label: "Storage (GB)" },
  { key: "max_automations", label: "Automations" },
  { key: "max_integrations", label: "Integrations" },
  { key: "max_journal_entries_month", label: "Journal/mo" },
] as const;

function formatPrice(cents: number, currency: string = "usd") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency.toUpperCase(),
  }).format(cents / 100);
}

export default function PlatformBillingPage() {
  const [plans, setPlans] = useState<AdminBillingPlan[]>([]);
  const [error, setError] = useState("");
  const [syncing, setSyncing] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<AdminBillingPlan | null>(null);

  const { data, error: loadError, mutate } = useApiSWR(
    ["platform", "billing", "plans"],
    (token) => adminListPlans(token),
  );

  useEffect(() => {
    if (data) setPlans(data);
  }, [data]);

  useEffect(() => {
    if (loadError) setError(loadError instanceof Error ? loadError.message : "Failed to load plans");
  }, [loadError]);

  const refresh = mutate;

  const handleSync = async (planId: string) => {
    const token = getAccessToken();
    if (!token) return;
    setSyncing(planId);
    try {
      await adminSyncPlan(token, planId);
      setError("");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Sync failed");
    } finally {
      setSyncing(null);
    }
  };

  const handleArchive = async (planId: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminArchivePlan(token, planId);
      await refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Archive failed");
    }
  };

  const openEdit = (plan: AdminBillingPlan) => {
    setEditingPlan(plan);
    setDialogOpen(true);
  };

  const openCreate = () => {
    setEditingPlan(null);
    setDialogOpen(true);
  };

  return (
    <>
      <PageHeader
        title="Billing Plans"
        breadcrumbs={[
          { label: "Platform", href: "/platform" },
          { label: "Billing Plans" },
        ]}
        actions={
          <Button size="sm" onClick={openCreate}>
            <Plus className="mr-1 size-4" />
            New Plan
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {plans.length === 0 && !error ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <CreditCard className="size-12 text-amber-500/50" />
            <h3 className="mt-4 text-lg font-semibold">No plans configured</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Create billing plans to enable tier-based feature gating.
            </p>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                {plans.length} plan{plans.length !== 1 && "s"}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Plan</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Limits</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plans.map((plan) => (
                    <TableRow key={plan.id}>
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium">{plan.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {plan.slug}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col">
                          <span>{formatPrice(plan.base_price_cents, plan.currency)}/mo</span>
                          {plan.annual_price_cents != null && (
                            <span className="text-xs text-muted-foreground">
                              {formatPrice(plan.annual_price_cents, plan.currency)}/yr
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {plan.billing_model.replace("_", " ")}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {LIMIT_FIELDS.filter(
                            (f) => plan[f.key as keyof AdminBillingPlan] != null
                          ).map((f) => (
                            <Badge
                              key={f.key}
                              variant="secondary"
                              className="text-xs"
                            >
                              {f.label}: {plan[f.key as keyof AdminBillingPlan] as number}
                            </Badge>
                          ))}
                          {LIMIT_FIELDS.every(
                            (f) => plan[f.key as keyof AdminBillingPlan] == null
                          ) && (
                            <span className="text-xs text-muted-foreground">
                              Unlimited
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          {plan.is_active ? (
                            <Badge className="bg-green-900/50 text-green-300">
                              <Check className="mr-1 size-3" />
                              Active
                            </Badge>
                          ) : (
                            <Badge variant="secondary">
                              <X className="mr-1 size-3" />
                              Archived
                            </Badge>
                          )}
                          {plan.is_public && (
                            <Badge variant="outline" className="text-xs">
                              Public
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => openEdit(plan)}
                            title="Edit"
                          >
                            <Pencil className="size-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => handleSync(plan.id)}
                            disabled={syncing === plan.id}
                            title="Sync to Stripe"
                          >
                            {syncing === plan.id ? (
                              <Loader2 className="size-4 animate-spin" />
                            ) : (
                              <RefreshCw className="size-4" />
                            )}
                          </Button>
                          {plan.is_active && (
                            <Button
                              size="icon"
                              variant="ghost"
                              onClick={() => handleArchive(plan.id)}
                              title="Archive"
                              className="text-muted-foreground hover:text-destructive"
                            >
                              <Archive className="size-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>

      <PlanDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        plan={editingPlan}
        onSaved={refresh}
      />
    </>
  );
}

// ─── Create / Edit Dialog ────────────────────────────────────────────────────

interface PlanDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  plan: AdminBillingPlan | null;
  onSaved: () => void;
}

function PlanDialog({ open, onOpenChange, plan, onSaved }: PlanDialogProps) {
  const isEdit = !!plan;
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<Record<string, unknown>>({});

  useEffect(() => {
    if (plan) {
      setForm({ ...plan });
    } else {
      setForm({
        slug: "",
        name: "",
        description: "",
        is_active: true,
        is_public: true,
        sort_order: 0,
        billing_model: "flat",
        base_price_cents: 0,
        annual_price_cents: null,
        currency: "usd",
        included_support_tier: "community",
      });
    }
    setError("");
  }, [plan, open]);

  const update = (key: string, value: unknown) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    setSaving(true);
    setError("");

    try {
      if (isEdit) {
        await adminUpdatePlan(token, plan.id, form as Partial<AdminBillingPlan>);
      } else {
        await adminCreatePlan(token, form as Partial<AdminBillingPlan>);
      }
      onOpenChange(false);
      onSaved();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit Plan" : "Create Plan"}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? "Update plan configuration and limits."
              : "Define a new billing plan with feature limits."}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="slug">Slug</Label>
              <Input
                id="slug"
                value={(form.slug as string) || ""}
                onChange={(e) => update("slug", e.target.value)}
                disabled={isEdit}
                placeholder="pro"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="name">Display Name</Label>
              <Input
                id="name"
                value={(form.name as string) || ""}
                onChange={(e) => update("name", e.target.value)}
                placeholder="Pro"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="base_price_cents">Monthly Price (cents)</Label>
              <Input
                id="base_price_cents"
                type="number"
                value={(form.base_price_cents as number) ?? 0}
                onChange={(e) => update("base_price_cents", parseInt(e.target.value) || 0)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="annual_price_cents">Annual Price (cents)</Label>
              <Input
                id="annual_price_cents"
                type="number"
                value={(form.annual_price_cents as number) ?? ""}
                onChange={(e) =>
                  update(
                    "annual_price_cents",
                    e.target.value ? parseInt(e.target.value) : null
                  )
                }
                placeholder="Optional"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="billing_model">Billing Model</Label>
              <Select
                value={(form.billing_model as string) || "flat"}
                onValueChange={(v) => update("billing_model", v)}
              >
                <SelectTrigger id="billing_model">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="flat">Flat</SelectItem>
                  <SelectItem value="tiered_usage">Tiered + Usage</SelectItem>
                  <SelectItem value="pay_as_you_go">Pay As You Go</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-sm font-medium">Feature Limits</Label>
            <p className="text-xs text-muted-foreground">
              Leave blank for unlimited.
            </p>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {LIMIT_FIELDS.map((f) => (
                <div key={f.key} className="space-y-1">
                  <Label htmlFor={f.key} className="text-xs">
                    {f.label}
                  </Label>
                  <Input
                    id={f.key}
                    type="number"
                    value={(form[f.key] as number) ?? ""}
                    onChange={(e) =>
                      update(f.key, e.target.value ? parseInt(e.target.value) : null)
                    }
                    placeholder="∞"
                    className="h-8 text-sm"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="included_support_tier">Support Tier</Label>
              <Select
                value={(form.included_support_tier as string) || "community"}
                onValueChange={(v) => update("included_support_tier", v)}
              >
                <SelectTrigger id="included_support_tier">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="community">Community</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="priority">Priority</SelectItem>
                  <SelectItem value="dedicated">Dedicated</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="sort_order">Sort Order</Label>
              <Input
                id="sort_order"
                type="number"
                value={(form.sort_order as number) ?? 0}
                onChange={(e) => update("sort_order", parseInt(e.target.value) || 0)}
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {isEdit ? "Save Changes" : "Create Plan"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
