"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listChannels,
  createChannel,
  updateChannel,
  deleteChannel,
  testChannel,
  pushSubscribe,
  pushUnsubscribe,
  listNotificationPreferences,
  createNotificationPreference,
  deleteNotificationPreference,
  type ChannelResponse,
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
} from "lucide-react";

const typeIcon: Record<string, React.ReactNode> = {
  discord: <MessageSquare className="size-4" />,
  slack: <Send className="size-4" />,
  email: <Mail className="size-4" />,
  sms: <Smartphone className="size-4" />,
};

export default function NotificationsPage() {
  const [channels, setChannels] = useState<ChannelResponse[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreference[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showPref, setShowPref] = useState(false);
  const [pushEnabled, setPushEnabled] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const [ch, prefs] = await Promise.all([
      listChannels(token),
      listNotificationPreferences(token).catch(() => [] as NotificationPreference[]),
    ]);
    setChannels(ch);
    setPreferences(prefs);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
    // Check push subscription status
    if ("serviceWorker" in navigator && "PushManager" in window) {
      navigator.serviceWorker.ready.then((reg) => {
        reg.pushManager.getSubscription().then((sub) => {
          setPushEnabled(!!sub);
        });
      });
    }
  }, [refresh]);

  const handleToggle = async (ch: ChannelResponse) => {
    const token = getAccessToken();
    if (!token) return;
    await updateChannel(token, ch.id, { enabled: !ch.enabled });
    refresh();
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteChannel(token, id);
    refresh();
  };

  const handleTest = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    setTesting(id);
    try {
      await testChannel(token, id);
    } finally {
      setTesting(null);
    }
  };

  const handlePushToggle = async () => {
    const token = getAccessToken();
    if (!token || !("serviceWorker" in navigator)) return;

    if (pushEnabled) {
      await pushUnsubscribe(token);
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.getSubscription();
      if (sub) await sub.unsubscribe();
      setPushEnabled(false);
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
                      <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:text-destructive" onClick={async () => {
                        const token = getAccessToken();
                        if (!token) return;
                        await deleteNotificationPreference(token, pref.id);
                        refresh();
                      }}>
                        <Trash2 className="size-3" />
                      </Button>
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
      onCreated();
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
  const [channelId, setChannelId] = useState("");
  const [eventTypes, setEventTypes] = useState("all");
  const [severity, setSeverity] = useState("warning,critical");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open && channels.length > 0 && !channelId) {
      setChannelId(channels[0].id);
    }
  }, [open, channels, channelId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token || !channelId) return;
    setSubmitting(true);
    try {
      await createNotificationPreference(token, {
        channel_id: channelId,
        severity_filter: severity,
        event_types: eventTypes,
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
          <DialogTitle>Add Notification Preference</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label>Channel</Label>
            <Select value={channelId} onValueChange={(v) => setChannelId(v ?? "")}>
              <SelectTrigger className="w-full"><SelectValue placeholder="Select channel" /></SelectTrigger>
              <SelectContent>
                {channels.filter((c) => c.enabled).map((c) => (
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
            <Button type="submit" disabled={submitting || !channelId}>
              {submitting && <Loader2 className="mr-1 size-4 animate-spin" />}
              Save Preference
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
