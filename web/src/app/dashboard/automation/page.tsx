"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
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
  const [rules, setRules] = useState<AutomationRuleResponse[]>([]);
  const [alerts, setAlerts] = useState<AlertResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const [r, a] = await Promise.all([
      listAutomationRules(token),
      listAlerts(token, 50),
    ]);
    setRules(r);
    setAlerts(a);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleToggle = async (rule: AutomationRuleResponse) => {
    const token = getAccessToken();
    if (!token) return;
    await updateAutomationRule(token, rule.id, { enabled: !rule.enabled });
    refresh();
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteAutomationRule(token, id);
    refresh();
  };

  const handleAcknowledge = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await acknowledgeAlert(token, id);
    refresh();
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
            <div className="mt-4 space-y-3">
              {alerts.length === 0 ? (
                <Card className="flex flex-col items-center justify-center py-16">
                  <AlertTriangle className="size-12 text-muted-foreground/50" />
                  <h3 className="mt-4 text-lg font-semibold">No alerts</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Alerts will appear here when automation rules are triggered.
                  </p>
                </Card>
              ) : (
                alerts.map((alert) => (
                  <Card
                    key={alert.id}
                    className={cn(
                      "flex items-center justify-between p-4",
                      alert.acknowledged && "opacity-60"
                    )}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant={severityVariant(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        <span className="text-sm">{alert.message}</span>
                      </div>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {formatDateTime(alert.created_at)}
                        {alert.sensor_value != null && ` — Value: ${alert.sensor_value}`}
                      </p>
                    </div>
                    {!alert.acknowledged && (
                      <Button variant="outline" size="sm" onClick={() => handleAcknowledge(alert.id)}>
                        <CheckCircle2 className="mr-1 size-4" />
                        Acknowledge
                      </Button>
                    )}
                  </Card>
                ))
              )}
            </div>
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
      onCreated();
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
