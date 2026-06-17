"use client";

import { useCallback, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  listAutomationRules,
  createAutomationRule,
  updateAutomationRule,
  deleteAutomationRule,
  listAlerts,
  acknowledgeAlert,
  type AutomationRuleResponse,
  type AlertResponse,
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
} from "lucide-react";

export default function AutomationPage() {
  const confirm = useConfirm();
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading: loading, mutate } = useApiSWR(
    ["automation"],
    async (token) => {
      const [r, a] = await Promise.all([
        listAutomationRules(token),
        listAlerts(token, 50),
      ]);
      return { rules: r, alerts: a };
    },
  );

  const rules = data?.rules ?? [];
  const alerts = data?.alerts ?? [];
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
