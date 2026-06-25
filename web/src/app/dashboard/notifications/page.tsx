"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  listChannels,
  createChannel,
  updateChannel,
  deleteChannel,
  testChannel,
  pushSubscribe,
  pushUnsubscribe,
  listNotificationPreferences,
  listNotificationLogs,
  createNotificationPreference,
  updateNotificationPreference,
  deleteNotificationPreference,
  type ChannelResponse,
  type NotificationLogEntry,
  type NotificationPreference,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
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
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { cn } from "@/lib/utils";
import {
  Plus,
  MoreHorizontal,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Bell,
  Send,
  MessageSquare,
  Mail,
  Smartphone,
  Loader2,
  Pencil,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { useConfirm } from "@/components/confirm-dialog";

const typeIcon: Record<string, React.ReactNode> = {
  discord: <MessageSquare className="size-4" />,
  slack: <Send className="size-4" />,
  email: <Mail className="size-4" />,
  sms: <Smartphone className="size-4" />,
};

const notificationEventLabels: Record<string, string> = {
  all: "All Events",
  ai_action_lifecycle: "AI Lifecycle",
  sensor_alert: "Sensor Alerts",
  automation: "Automation Triggers",
  health_check: "Health Checks",
  stage_change: "Stage Changes",
  feeding_reminder: "Feeding Reminders",
};

const severityBadgeClass: Record<string, string> = {
  critical: "border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300",
  warning: "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  info: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
};

const statusBadgeClass: Record<string, string> = {
  sent: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  skipped: "border-slate-500/30 bg-slate-500/10 text-slate-700 dark:text-slate-300",
  failed: "border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300",
};

function formatNotificationTimestamp(timestamp: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(timestamp));
}

export default function NotificationsPage() {
  const confirm = useConfirm();
  const [showCreate, setShowCreate] = useState(false);
  const [showPref, setShowPref] = useState(false);
  const [editingPref, setEditingPref] = useState<NotificationPreference | null>(null);
  const [pushEnabled, setPushEnabled] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);

  const { data, isLoading: loading, mutate } = useApiSWR(
    ["notifications"],
    async (token) => {
      const [ch, prefs, logs] = await Promise.all([
        listChannels(token).catch(() => [] as ChannelResponse[]),
        listNotificationPreferences(token).catch(() => [] as NotificationPreference[]),
        listNotificationLogs(token, {
          eventType: "ai_action_lifecycle",
          channelType: "in_app",
          pageSize: 8,
        }).catch(() => [] as NotificationLogEntry[]),
      ]);
      return { channels: ch, preferences: prefs, logs };
    },
  );

  const channels = data?.channels ?? [];
  const preferences = data?.preferences ?? [];
  const aiLifecycleLogs = data?.logs ?? [];

  const refresh = mutate;

  // Check push subscription status on mount only
  useEffect(() => {
    if ("serviceWorker" in navigator && "PushManager" in window) {
      navigator.serviceWorker.ready.then((reg) => {
        reg.pushManager.getSubscription().then((sub) => {
          setPushEnabled(!!sub);
        });
      });
    }
  }, []);

  const handleToggle = async (ch: ChannelResponse) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateChannel(token, ch.id, { enabled: !ch.enabled });
      toast.success(ch.enabled ? "Channel disabled" : "Channel enabled");
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to update channel");
    }
  };

  const handleDelete = async (id: string) => {
    const ok = await confirm({ title: "Delete Channel", description: "This notification channel will be permanently removed.", confirmText: "Delete", variant: "destructive" });
    if (!ok) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteChannel(token, id);
      toast.success("Channel deleted");
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to delete channel");
    }
  };

  const handleTest = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    setTesting(id);
    try {
      await testChannel(token, id);
      toast.success("Test notification sent");
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to send test notification");
    } finally {
      setTesting(null);
    }
  };

  const handlePushToggle = async () => {
    const token = getAccessToken();
    if (!token || !("serviceWorker" in navigator)) return;
    try {
      if (pushEnabled) {
        await pushUnsubscribe(token);
        const reg = await navigator.serviceWorker.ready;
        const sub = await reg.pushManager.getSubscription();
        if (sub) await sub.unsubscribe();
        setPushEnabled(false);
        toast.success("Push notifications disabled");
      } else {
        const reg = await navigator.serviceWorker.ready;
        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY,
        });
        const keys = sub.toJSON().keys || {};
        await pushSubscribe(token, {
          endpoint: sub.endpoint,
          p256dh: keys.p256dh || "",
          auth: keys.auth || "",
        });
        setPushEnabled(true);
        toast.success("Push notifications enabled");
      }
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to update push notifications");
    }
  };

  if (loading) return <PageSkeleton rows={4} cards />;

  return (
    <>
      <PageHeader
        title="Notifications"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Notifications" }]}
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 size-4" />
            Add Channel
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Push Notifications */}
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2 text-base">
                <Bell className="size-4" />
                Push Notifications
              </CardTitle>
              <CardDescription>
                Receive alerts directly on this device via your browser.
              </CardDescription>
            </div>
            <Switch
              checked={pushEnabled}
              onCheckedChange={handlePushToggle}
            />
          </CardHeader>
        </Card>

        <Card className="overflow-hidden border-border/70 bg-card">
          <CardHeader className="border-b border-border/60 bg-muted/30">
            <div className="flex items-start gap-3">
              <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-2 text-emerald-700 dark:text-emerald-300">
                <Sparkles className="size-4" />
              </div>
              <div className="space-y-1">
                <CardTitle className="text-base">AI Lifecycle Feed</CardTitle>
                <CardDescription>
                  Recent approvals, blocks, failures, and verifications routed into your notification system.
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3 p-4">
            {aiLifecycleLogs.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border/70 bg-muted/20 p-5 text-sm text-muted-foreground">
                AI lifecycle alerts will appear here after the assistant proposes, blocks, fails, or verifies an action.
              </div>
            ) : (
              aiLifecycleLogs.map((log) => (
                <div key={log.id} className="rounded-xl border border-border/70 bg-background/80 p-4 shadow-sm">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge className={cn("border", severityBadgeClass[log.severity] ?? severityBadgeClass.info)} variant="outline">
                          {log.severity}
                        </Badge>
                        <Badge className={cn("border", statusBadgeClass[log.status] ?? statusBadgeClass.sent)} variant="outline">
                          {log.status}
                        </Badge>
                        <Badge variant="secondary">
                          {notificationEventLabels[log.event_type] ?? log.event_type}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-foreground">{log.subject}</p>
                        {log.body ? <p className="mt-1 text-sm text-muted-foreground">{log.body}</p> : null}
                        {log.error ? <p className="mt-2 text-xs text-destructive">Delivery error: {log.error}</p> : null}
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground sm:text-right">{formatNotificationTimestamp(log.created_at)}</p>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Channels */}
        {channels.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Bell className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No notification channels</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Add a channel to receive alerts via Discord, Slack, or email.
            </p>
            <Button className="mt-4" onClick={() => setShowCreate(true)}>
              <Plus className="mr-1 size-4" />
              Add Channel
            </Button>
          </Card>
        ) : (
          <div className="space-y-3">
            {channels.map((ch) => (
              <Card key={ch.id} className="flex items-center justify-between p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "size-2 rounded-full",
                        ch.enabled ? "bg-green-500" : "bg-muted-foreground/40"
                      )}
                    />
                    <span className="text-muted-foreground">
                      {typeIcon[ch.channel_type] || <Bell className="size-4" />}
                    </span>
                    <span className="font-medium">{ch.name}</span>
                    <Badge variant="secondary">{ch.channel_type}</Badge>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" />}>
                    <MoreHorizontal className="size-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => handleTest(ch.id)}
                      disabled={testing === ch.id}
                    >
                      {testing === ch.id ? (
                        <Loader2 className="mr-2 size-4 animate-spin" />
                      ) : (
                        <Send className="mr-2 size-4" />
                      )}
                      {testing === ch.id ? "Sending…" : "Test"}
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleToggle(ch)}>
                      {ch.enabled ? (
                        <ToggleLeft className="mr-2 size-4" />
                      ) : (
                        <ToggleRight className="mr-2 size-4" />
                      )}
                      {ch.enabled ? "Disable" : "Enable"}
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      variant="destructive"
                      onClick={() => handleDelete(ch.id)}
                    >
                      <Trash2 className="mr-2 size-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </Card>
            ))}
          </div>
        )}

        {/* Notification Preferences */}
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0 pb-2">
            <div className="space-y-1">
              <CardTitle className="text-base">Alert Preferences</CardTitle>
              <CardDescription>
                Choose which events trigger notifications and on which channels.
              </CardDescription>
            </div>
            <Button size="sm" variant="outline" onClick={() => setShowPref(true)} disabled={channels.length === 0}>
              <Plus className="mr-1 size-4" /> Add Rule
            </Button>
          </CardHeader>
          <CardContent>
            {preferences.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8">
                <Bell className="size-10 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground text-center">
                  {channels.length === 0 ? "Add a channel first to configure preferences." : "No preferences configured. All events go to all enabled channels."}
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {preferences.map((pref) => {
                  const ch = channels.find((c) => c.id === pref.channel_id);
                  return (
                    <div key={pref.id} className="flex items-center justify-between rounded-md border p-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">{pref.event_types === "all" ? "All Events" : pref.event_types}</Badge>
                          <span className="text-xs text-muted-foreground">→</span>
                          <span className="text-sm font-medium">{ch?.name || "Unknown channel"}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-0.5">Severity: {pref.severity_filter}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => setEditingPref(pref)}>
                          <Pencil className="size-3" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={async () => {
                          const ok = await confirm({ title: "Delete Preference", description: "Remove this notification preference?", confirmText: "Delete", variant: "destructive" });
                          if (!ok) return;
                          const token = getAccessToken();
                          if (!token) return;
                          try {
                            await deleteNotificationPreference(token, pref.id);
                            toast.success("Preference deleted");
                            refresh();
                          } catch (e) {
                            toast.error(e instanceof Error ? e.message : "Failed to delete preference");
                          }
                        }}>
                          <Trash2 className="size-3" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <CreateChannelDialog
        open={showCreate}
        onOpenChange={setShowCreate}
        onCreated={() => {
          setShowCreate(false);
          refresh();
        }}
      />

      <CreatePreferenceDialog
        open={showPref}
        onOpenChange={setShowPref}
        channels={channels}
        onCreated={() => {
          setShowPref(false);
          refresh();
        }}
      />

      {editingPref && (
        <EditPreferenceDialog
          key={editingPref.id}
          open={!!editingPref}
          onOpenChange={(open) => { if (!open) setEditingPref(null); }}
          pref={editingPref}
          channels={channels}
          onUpdated={() => {
            setEditingPref(null);
            refresh();
          }}
        />
      )}
    </>
  );
}

function CreateChannelDialog({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [type, setType] = useState("discord");
  const [name, setName] = useState("");
  const [webhookUrl, setWebhookUrl] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;

    const config: Record<string, string> = {};
    if (type === "discord" || type === "slack") {
      config.webhook_url = webhookUrl;
    } else if (type === "email") {
      config.email = email;
    }

    setSubmitting(true);
    try {
      await createChannel(token, { channel_type: type, name, config });
      toast.success("Channel created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create channel");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Notification Channel</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Type</Label>
            <Select value={type} onValueChange={(v) => setType(v ?? "")}>
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="discord">Discord Webhook</SelectItem>
                <SelectItem value="slack">Slack Webhook</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="sms">SMS (Twilio)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Name</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. My Discord Server"
              required
            />
          </div>
          {(type === "discord" || type === "slack") && (
            <div className="space-y-2">
              <Label>Webhook URL</Label>
              <Input
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://discord.com/api/webhooks/..."
                required
              />
            </div>
          )}
          {type === "email" && (
            <div className="space-y-2">
              <Label>Email Address</Label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}
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

const EVENT_TYPE_OPTIONS = [
  { value: "all", label: "All Events" },
  { value: "ai_action_lifecycle", label: "AI Action Lifecycle" },
  { value: "sensor_alert", label: "Sensor Alerts" },
  { value: "automation", label: "Automation Triggers" },
  { value: "health_check", label: "Health Checks" },
  { value: "stage_change", label: "Stage Changes" },
  { value: "feeding_reminder", label: "Feeding Reminders" },
];

const SEVERITY_OPTIONS = [
  { value: "info,warning,critical", label: "All Severities" },
  { value: "warning,critical", label: "Warning & Critical" },
  { value: "critical", label: "Critical Only" },
];

function CreatePreferenceDialog({
  open,
  onOpenChange,
  channels,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  channels: ChannelResponse[];
  onCreated: () => void;
}) {
  const enabledChannels = channels.filter((channel) => channel.enabled);
  const [channelId, setChannelId] = useState("");
  const [eventTypes, setEventTypes] = useState("all");
  const [severity, setSeverity] = useState("warning,critical");
  const [submitting, setSubmitting] = useState(false);
  const resolvedChannelId = channelId || enabledChannels[0]?.id || "";
  const selectedChannel = enabledChannels.find((channel) => channel.id === resolvedChannelId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token || !resolvedChannelId) return;
    setSubmitting(true);
    try {
      await createNotificationPreference(token, {
        channel_id: resolvedChannelId,
        severity_filter: severity,
        event_types: eventTypes,
      });
      toast.success("Preference created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create preference");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Notification Preference</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Channel</Label>
            <Select value={resolvedChannelId} onValueChange={(v) => setChannelId(v ?? "")}>
              <SelectTrigger className="w-full">
                <span>
                  {selectedChannel ? `${selectedChannel.name} (${selectedChannel.channel_type})` : "Select channel"}
                </span>
              </SelectTrigger>
              <SelectContent>
                {enabledChannels.map((c) => (
                  <SelectItem key={c.id} value={c.id}>{c.name} ({c.channel_type})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Event Types</Label>
            <Select value={eventTypes} onValueChange={(v) => setEventTypes(v ?? "all")}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {EVENT_TYPE_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Severity Filter</Label>
            <Select value={severity} onValueChange={(v) => setSeverity(v ?? "warning,critical")}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {SEVERITY_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={submitting || !resolvedChannelId}>
              {submitting && <Loader2 className="mr-1 size-4 animate-spin" />}
              Save Preference
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EditPreferenceDialog({
  open,
  onOpenChange,
  pref,
  channels,
  onUpdated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  pref: NotificationPreference;
  channels: ChannelResponse[];
  onUpdated: () => void;
}) {
  const [eventTypes, setEventTypes] = useState(pref.event_types);
  const [severity, setSeverity] = useState(pref.severity_filter);
  const [enabled, setEnabled] = useState(pref.enabled);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    setSubmitting(true);
    try {
      await updateNotificationPreference(token, pref.id, {
        event_types: eventTypes,
        severity_filter: severity,
        enabled,
      });
      toast.success("Preference updated");
      onUpdated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to update preference");
    } finally {
      setSubmitting(false);
    }
  };

  const ch = channels.find((c) => c.id === pref.channel_id);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit Notification Preference</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Channel</Label>
            <Input value={ch?.name || "Unknown"} disabled className="opacity-70" />
          </div>
          <div className="space-y-2">
            <Label>Event Types</Label>
            <Select value={eventTypes} onValueChange={(v) => setEventTypes(v ?? "all")}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {EVENT_TYPE_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Severity Filter</Label>
            <Select value={severity} onValueChange={(v) => setSeverity(v ?? "warning,critical")}>
              <SelectTrigger className="w-full"><SelectValue /></SelectTrigger>
              <SelectContent>
                {SEVERITY_OPTIONS.map((o) => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center justify-between">
            <Label>Enabled</Label>
            <Switch checked={enabled} onCheckedChange={setEnabled} />
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={submitting}>
              {submitting && <Loader2 className="mr-1 size-4 animate-spin" />}
              Update Preference
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
