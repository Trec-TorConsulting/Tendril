"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  listAutomationRules,
  createAutomationRule,
  updateAutomationRule,
  deleteAutomationRule,
  getRuleStageThresholds,
  setRuleStageThresholds,
  clearRuleStageThresholds,
  listAlerts,
  acknowledgeAlert,
  getTenantCoachingSettings,
  updateTenantCoachingSettings,
  type AutomationRuleResponse,
  type AlertResponse,
  type TenantCoachingSettingsResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { cn, formatDateTime } from "@/lib/utils";
import { toast } from "sonner";
import { useConfirm } from "@/components/confirm-dialog";
import {
  Plus,
  MoreHorizontal,
  Trash2,
  ToggleLeft,
  ToggleRight,
  CheckCircle2,
  Zap,
  AlertTriangle,
  Loader2,
  SlidersHorizontal,
} from "lucide-react";

const STAGES = ["seedling", "vegetative", "flowering", "ripening", "harvesting"] as const;

export default function AutomationPage() {
  const confirm = useConfirm();
  const [showCreate, setShowCreate] = useState(false);
  const [editingRule, setEditingRule] = useState<AutomationRuleResponse | null>(null);
  const [coachingDraft, setCoachingDraft] = useState<TenantCoachingSettingsResponse | null>(null);
  const [savingCoaching, setSavingCoaching] = useState(false);

  const { data, isLoading: loading, mutate } = useApiSWR(
    ["automation"],
    async (token) => {
      const [r, a, c] = await Promise.all([
        listAutomationRules(token),
        listAlerts(token, 50),
        getTenantCoachingSettings(token),
      ]);
      return { rules: r, alerts: a, coaching: c };
    },
  );

  const rules = data?.rules ?? [];
  const alerts = data?.alerts ?? [];
  const coaching = coachingDraft ?? data?.coaching ?? null;
  const refresh = mutate;

  const handleToggle = async (rule: AutomationRuleResponse) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateAutomationRule(token, rule.id, { enabled: !rule.enabled });
      toast.success(rule.enabled ? "Rule disabled" : "Rule enabled");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to toggle rule"); }
  };

  const handleDelete = async (id: string) => {
    const ok = await confirm({ title: "Delete Rule", description: "This automation rule will be permanently deleted.", confirmText: "Delete", variant: "destructive" });
    if (!ok) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteAutomationRule(token, id);
      toast.success("Rule deleted");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete rule"); }
  };

  const handleAcknowledge = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await acknowledgeAlert(token, id);
      toast.success("Alert acknowledged");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to acknowledge alert"); }
  };

  const saveCoachingSettings = async () => {
    const token = getAccessToken();
    if (!token || !coaching) return;
    setSavingCoaching(true);
    try {
      await updateTenantCoachingSettings(token, coaching);
      toast.success("Coaching settings updated");
      setCoachingDraft(null);
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to update coaching settings");
    } finally {
      setSavingCoaching(false);
    }
  };

  const severityVariant = (severity: string) => {
    if (severity === "critical") return "destructive" as const;
    if (severity === "warning") return "outline" as const;
    return "secondary" as const;
  };

  if (loading) return <PageSkeleton rows={4} cards />;

  return (
    <>
      <PageHeader
        title="Automation"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Automation" }]}
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 size-4" />
            New Rule
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <Tabs defaultValue="rules">
          <TabsList>
            <TabsTrigger value="rules">Rules ({rules.length})</TabsTrigger>
            <TabsTrigger value="alerts">
              Alerts ({alerts.filter((a) => !a.acknowledged).length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="rules">
            <div className="mt-4 space-y-3">
              {coaching && (
                <Card className="p-4">
                  <div className="mb-3 flex items-center gap-2">
                    <SlidersHorizontal className="size-4" />
                    <h3 className="font-medium">Proactive Coaching</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Tune tenant-wide coaching cadence and severity floor for scheduler nudges.
                  </p>
                  <div className="mt-3 grid gap-3 md:grid-cols-3">
                    <div className="space-y-2">
                      <Label>Enabled</Label>
                      <Select
                        value={coaching.enabled ? "enabled" : "disabled"}
                        onValueChange={(v) =>
                          setCoachingDraft({ ...coaching, enabled: v === "enabled" })
                        }
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="enabled">Enabled</SelectItem>
                          <SelectItem value="disabled">Disabled</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Cadence</Label>
                      <Select
                        value={String(coaching.cadence_hours)}
                        onValueChange={(v) =>
                          setCoachingDraft({ ...coaching, cadence_hours: Number(v ?? "24") })
                        }
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="6">Every 6 hours</SelectItem>
                          <SelectItem value="12">Every 12 hours</SelectItem>
                          <SelectItem value="24">Daily</SelectItem>
                          <SelectItem value="48">Every 2 days</SelectItem>
                          <SelectItem value="72">Every 3 days</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Minimum Severity</Label>
                      <Select
                        value={coaching.minimum_severity}
                        onValueChange={(v) =>
                          setCoachingDraft({
                            ...coaching,
                            minimum_severity: (v as TenantCoachingSettingsResponse["minimum_severity"]) ?? "info",
                          })
                        }
                      >
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="info">Info and above</SelectItem>
                          <SelectItem value="warning">Warning and above</SelectItem>
                          <SelectItem value="critical">Critical only</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Button size="sm" onClick={saveCoachingSettings} disabled={savingCoaching}>
                      {savingCoaching && <Loader2 className="mr-1 size-4 animate-spin" />}
                      Save Coaching Settings
                    </Button>
                  </div>
                </Card>
              )}

              {rules.length === 0 ? (
                <Card className="flex flex-col items-center justify-center py-16">
                  <Zap className="size-12 text-muted-foreground/50" />
                  <h3 className="mt-4 text-lg font-semibold">No automation rules yet</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Create a rule to automate alerts based on sensor readings.
                  </p>
                  <Button className="mt-4" onClick={() => setShowCreate(true)}>
                    <Plus className="mr-1 size-4" />
                    New Rule
                  </Button>
                </Card>
              ) : (
                rules.map((rule) => (
                  <Card key={rule.id} className="flex items-center justify-between p-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "size-2 rounded-full",
                            rule.enabled ? "bg-green-500" : "bg-muted-foreground/40"
                          )}
                        />
                        <span className="font-medium">{rule.name}</span>
                        <Badge variant={severityVariant(rule.severity)}>
                          {rule.severity}
                        </Badge>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {rule.sensor} {rule.condition} {rule.threshold} → {rule.action}
                      </p>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" />}>
                        <MoreHorizontal className="size-4" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleToggle(rule)}>
                          {rule.enabled ? (
                            <ToggleLeft className="mr-2 size-4" />
                          ) : (
                            <ToggleRight className="mr-2 size-4" />
                          )}
                          {rule.enabled ? "Disable" : "Enable"}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => setEditingRule(rule)}>
                          <SlidersHorizontal className="mr-2 size-4" />
                          Stage Thresholds
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          variant="destructive"
                          onClick={() => handleDelete(rule.id)}
                        >
                          <Trash2 className="mr-2 size-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="alerts">
            <AlertsPanel alerts={alerts} onAcknowledge={handleAcknowledge} severityVariant={severityVariant} />
          </TabsContent>
        </Tabs>
      </div>

      <CreateRuleDialog
        open={showCreate}
        onOpenChange={setShowCreate}
        onCreated={() => {
          setShowCreate(false);
          refresh();
        }}
      />
      <StageThresholdDialog
        key={editingRule?.id ?? "no-rule"}
        rule={editingRule}
        open={!!editingRule}
        onOpenChange={(open) => {
          if (!open) setEditingRule(null);
        }}
        onSaved={refresh}
      />
    </>
  );
}

// ── Alerts Panel with Filtering ──────────────────────────────────────────────

function alertCategory(alertType: string): string {
  if (alertType.startsWith("trend_")) return "Trend";
  if (alertType.startsWith("composite_")) return "Composite";
  if (alertType.startsWith("critical_")) return "Critical";
  if (alertType.startsWith("weather_")) return "Weather";
  return "Rule";
}

function AlertsPanel({
  alerts,
  onAcknowledge,
  severityVariant,
}: {
  alerts: AlertResponse[];
  onAcknowledge: (id: string) => void;
  severityVariant: (s: string) => "destructive" | "outline" | "secondary";
}) {
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [showAcknowledged, setShowAcknowledged] = useState(false);

  const filtered = alerts.filter((a) => {
    if (!showAcknowledged && a.acknowledged) return false;
    if (severityFilter !== "all" && a.severity !== severityFilter) return false;
    if (categoryFilter !== "all" && alertCategory(a.alert_type) !== categoryFilter) return false;
    return true;
  });

  const categories = [...new Set(alerts.map((a) => alertCategory(a.alert_type)))];

  return (
    <div className="mt-4 space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <Select value={severityFilter} onValueChange={(v) => setSeverityFilter(v ?? "all")}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="warning">Warning</SelectItem>
            <SelectItem value="info">Info</SelectItem>
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={(v) => setCategoryFilter(v ?? "all")}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {categories.map((c) => (
              <SelectItem key={c} value={c}>{c}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant={showAcknowledged ? "secondary" : "outline"}
          size="sm"
          onClick={() => setShowAcknowledged(!showAcknowledged)}
        >
          {showAcknowledged ? "Hide Acknowledged" : "Show Acknowledged"}
        </Button>
        <span className="ml-auto text-xs text-muted-foreground">
          {filtered.length} of {alerts.length} alerts
        </span>
      </div>

      {/* Alert List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <AlertTriangle className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No alerts</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {alerts.length === 0
                ? "Alerts will appear here when automation rules are triggered."
                : "No alerts match the current filters."}
            </p>
          </Card>
        ) : (
          filtered.map((alert) => (
            <Card
              key={alert.id}
              className={cn(
                "flex items-center justify-between p-4",
                alert.acknowledged && "opacity-60",
                alert.message.startsWith("[ESCALATED]") && "border-red-500/50"
              )}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant={severityVariant(alert.severity)}>
                    {alert.severity}
                  </Badge>
                  <Badge variant="secondary" className="text-[10px]">
                    {alertCategory(alert.alert_type)}
                  </Badge>
                  {alert.message.startsWith("[ESCALATED]") && (
                    <Badge variant="destructive" className="text-[10px]">Escalated</Badge>
                  )}
                </div>
                <p className="mt-1 text-sm">
                  {alert.message.replace("[ESCALATED] ", "")}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {formatDateTime(alert.created_at)}
                  {alert.sensor_value != null && ` — Value: ${alert.sensor_value}`}
                </p>
              </div>
              {!alert.acknowledged && (
                <Button variant="outline" size="sm" className="ml-3 shrink-0" onClick={() => onAcknowledge(alert.id)}>
                  <CheckCircle2 className="mr-1 size-4" />
                  Ack
                </Button>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

function CreateRuleDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState("");
  const [sensor, setSensor] = useState("ph");
  const [condition, setCondition] = useState(">");
  const [threshold, setThreshold] = useState("");
  const [action, setAction] = useState("alert");
  const [severity, setSeverity] = useState("warning");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await createAutomationRule(token, {
        name,
        sensor,
        condition,
        threshold: parseFloat(threshold),
        action,
        severity,
      });
      toast.success("Rule created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create rule");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Automation Rule</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Name</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-2">
              <Label>Sensor</Label>
              <Select value={sensor} onValueChange={(v) => setSensor(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["ph", "ec", "water_temp", "air_temp", "humidity", "co2", "vpd", "do"].map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Condition</Label>
              <Select value={condition} onValueChange={(v) => setCondition(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[">", "<", ">=", "<=", "=="].map((c) => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Threshold</Label>
              <Input
                type="number"
                step="any"
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>Action</Label>
              <Select value={action} onValueChange={(v) => setAction(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["alert", "push_notification", "log"].map((a) => (
                    <SelectItem key={a} value={a}>{a}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Severity</Label>
              <Select value={severity} onValueChange={(v) => setSeverity(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["info", "warning", "critical"].map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting}>
              {submitting && <Loader2 className="mr-1 size-4 animate-spin" />}
              Create
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function StageThresholdDialog({
  rule,
  open,
  onOpenChange,
  onSaved,
}: {
  rule: AutomationRuleResponse | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}) {
  const [saving, setSaving] = useState(false);
  const [thresholdEdits, setThresholdEdits] = useState<Record<string, string>>({});

  const { data: stageThresholdData, isLoading: loading } = useApiSWR(
    open && rule ? ["rule-stage-thresholds", rule.id] : null,
    async (token) => {
      if (!rule) return { rule_id: "", condition: "", thresholds: {} };
      return getRuleStageThresholds(token, rule.id);
    },
  );

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token || !rule) return;
    const payload: Record<string, number> = {};
    for (const stage of STAGES) {
      const fallback = stageThresholdData?.thresholds?.[stage];
      const raw = (thresholdEdits[stage] ?? (fallback == null ? "" : String(fallback))).trim();
      if (!raw) continue;
      const parsed = Number(raw);
      if (Number.isNaN(parsed)) {
        toast.error(`Invalid threshold for ${stage}`);
        return;
      }
      payload[stage] = parsed;
    }

    setSaving(true);
    try {
      await setRuleStageThresholds(token, rule.id, payload);
      toast.success("Stage thresholds saved");
      onSaved();
      onOpenChange(false);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to save stage thresholds");
    } finally {
      setSaving(false);
    }
  };

  const handleClear = async () => {
    const token = getAccessToken();
    if (!token || !rule) return;
    setSaving(true);
    try {
      await clearRuleStageThresholds(token, rule.id);
      toast.success("Stage thresholds cleared");
      onSaved();
      onOpenChange(false);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to clear stage thresholds");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Stage Thresholds{rule ? ` · ${rule.name}` : ""}</DialogTitle>
        </DialogHeader>
        {loading ? (
          <div className="py-8 text-center text-sm text-muted-foreground">Loading stage overrides...</div>
        ) : (
          <form onSubmit={handleSave} className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Override {rule?.sensor} {rule?.condition} thresholds by stage. Leave fields blank to use defaults.
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {STAGES.map((stage) => (
                <div key={stage} className="space-y-2">
                  <Label className="capitalize">{stage}</Label>
                  <Input
                    type="number"
                    step="any"
                    value={thresholdEdits[stage] ?? (stageThresholdData?.thresholds?.[stage] == null ? "" : String(stageThresholdData.thresholds[stage]))}
                    onChange={(e) => setThresholdEdits((prev) => ({ ...prev, [stage]: e.target.value }))}
                  />
                </div>
              ))}
            </div>
            <DialogFooter>
              <Button variant="outline" type="button" onClick={handleClear} disabled={saving}>
                Clear Overrides
              </Button>
              <Button variant="outline" type="button" onClick={() => onOpenChange(false)} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving && <Loader2 className="mr-1 size-4 animate-spin" />}
                Save
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
