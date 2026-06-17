"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import { getMe, getMyTenant, updateProfile, listGrows } from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Loader2, Pencil, X, Download, Trash2, Check,
  User, Palette, Ruler, LayoutGrid, Shield,
} from "lucide-react";
import { toast } from "sonner";
import { useLayoutMode } from "@/hooks/use-layout-mode";
import { usePreferences } from "@/hooks/use-preferences";
import { LAYOUT_CONFIGS, type LayoutMode } from "@/lib/layout-config";

/* ─────────────────────── helpers ─────────────────────── */

interface PrefOption { value: string; label: string }

const TEMP_UNITS: PrefOption[] = [
  { value: "fahrenheit", label: "Fahrenheit (°F)" },
  { value: "celsius", label: "Celsius (°C)" },
];
const MEASUREMENT_SYSTEMS: PrefOption[] = [
  { value: "imperial", label: "Imperial (US)" },
  { value: "metric", label: "Metric (SI)" },
];
const WIND_UNITS: PrefOption[] = [
  { value: "mph", label: "mph" },
  { value: "kmh", label: "km/h" },
  { value: "ms", label: "m/s" },
];
const PRESSURE_UNITS: PrefOption[] = [
  { value: "inhg", label: "inHg" },
  { value: "hpa", label: "hPa" },
];
const DATE_FORMATS: PrefOption[] = [
  { value: "MM/DD/YYYY", label: "MM/DD/YYYY" },
  { value: "DD/MM/YYYY", label: "DD/MM/YYYY" },
  { value: "YYYY-MM-DD", label: "YYYY-MM-DD (ISO)" },
];
const TIME_FORMATS: PrefOption[] = [
  { value: "12h", label: "12-hour (1:30 PM)" },
  { value: "24h", label: "24-hour (13:30)" },
];
const WEEK_STARTS: PrefOption[] = [
  { value: "sunday", label: "Sunday" },
  { value: "monday", label: "Monday" },
];
const THEMES: PrefOption[] = [
  { value: "system", label: "System Default" },
  { value: "light", label: "Light" },
  { value: "dark", label: "Dark" },
];

/* ─────────────────── reusable selector row ─────────────────── */

function PrefSelect({
  label,
  description,
  value,
  options,
  onValueChange,
  disabled,
}: {
  label: string;
  description?: string;
  value: string;
  options: PrefOption[];
  onValueChange: (v: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="min-w-0">
        <p className="text-sm font-medium">{label}</p>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <Select value={value} onValueChange={(v) => onValueChange(v ?? "")} disabled={disabled}>
        <SelectTrigger className="w-full sm:w-[180px] shrink-0">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function PrefToggle({
  label,
  description,
  checked,
  onCheckedChange,
  disabled,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="min-w-0">
        <p className="text-sm font-medium">{label}</p>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} disabled={disabled} />
    </div>
  );
}

/* ═══════════════════════ MAIN PAGE ═══════════════════════ */

export default function SettingsPage() {
  const { data: rawProfile, mutate: refreshProfile } = useApiSWR(
    ["settings-profile"],
    async (token) => {
      const [u, t] = await Promise.all([getMe(token), getMyTenant(token)]);
      return { user: u, tenant: t };
    },
  );
  const user = rawProfile?.user ?? null;
  const tenant = rawProfile?.tenant ?? null;
  const [editing, setEditing] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  // Sync form values when profile loads or refreshes
  useEffect(() => {
    if (rawProfile?.user) {
      setDisplayName(rawProfile.user.display_name || "");
      setEmail(rawProfile.user.email);
    }
  }, [rawProfile]);

  const refresh = refreshProfile;

  const handleSave = async () => {
    const token = getAccessToken();
    if (!token || !user) return;
    setSaving(true);
    setMessage({ type: "", text: "" });
    try {
      const updates: { display_name?: string; email?: string } = {};
      if (displayName !== (user.display_name || "")) updates.display_name = displayName;
      if (email !== user.email) updates.email = email;

      if (Object.keys(updates).length === 0) {
        setEditing(false);
        return;
      }

      await updateProfile(token, updates);
      setMessage({ type: "success", text: "Profile updated successfully" });
      setEditing(false);
      refresh();
    } catch (e: unknown) {
      setMessage({ type: "error", text: e instanceof Error ? e.message : "Failed to update" });
    } finally {
      setSaving(false);
    }
  };

  const initials = user?.display_name
    ? user.display_name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() ?? "?";

  return (
    <>
      <PageHeader
        title="Settings"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Settings", href: "/dashboard/settings" },
        ]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {message.text && (
          <Alert variant={message.type === "success" ? "default" : "destructive"}>
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="mb-4 flex w-full flex-wrap justify-start gap-1 bg-transparent p-0">
            <TabsTrigger value="profile" className="gap-1.5 data-[state=active]:bg-muted">
              <User className="size-3.5" /> Profile
            </TabsTrigger>
            <TabsTrigger value="display" className="gap-1.5 data-[state=active]:bg-muted">
              <Palette className="size-3.5" /> Display
            </TabsTrigger>
            <TabsTrigger value="units" className="gap-1.5 data-[state=active]:bg-muted">
              <Ruler className="size-3.5" /> Units & Locale
            </TabsTrigger>
            <TabsTrigger value="dashboard" className="gap-1.5 data-[state=active]:bg-muted">
              <LayoutGrid className="size-3.5" /> Dashboard
            </TabsTrigger>
            <TabsTrigger value="data" className="gap-1.5 data-[state=active]:bg-muted">
              <Shield className="size-3.5" /> Data & Privacy
            </TabsTrigger>
          </TabsList>

          {/* ──── Profile Tab ──── */}
          <TabsContent value="profile">
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Personal Information</CardTitle>
                    {!editing && user && (
                      <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                        <Pencil className="mr-1 size-3" /> Edit
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {!user ? (
                    <div className="space-y-4">
                      <Skeleton className="h-12 w-12 rounded-full" />
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-48" />
                    </div>
                  ) : !editing ? (
                    <div className="flex items-start gap-4">
                      <Avatar className="size-14">
                        <AvatarFallback className="bg-primary/20 text-primary text-lg">
                          {initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="space-y-3 text-sm">
                        <div>
                          <p className="text-muted-foreground">Display Name</p>
                          <p className="font-medium">{user.display_name || "Not set"}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Email</p>
                          <p className="font-medium">{user.email}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Role</p>
                          <Badge variant="secondary" className="capitalize">{user.role}</Badge>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Display Name</Label>
                        <Input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
                      </div>
                      <div className="space-y-2">
                        <Label>Email</Label>
                        <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                        {email !== user.email && (
                          <p className="text-xs text-amber-400">
                            Changing email will require re-verification
                          </p>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" onClick={handleSave} disabled={saving}>
                          {saving && <Loader2 className="mr-1 size-3 animate-spin" />}
                          {saving ? "Saving…" : "Save Changes"}
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => {
                          setEditing(false);
                          setDisplayName(user.display_name || "");
                          setEmail(user.email);
                        }}>
                          <X className="mr-1 size-3" /> Cancel
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Organization</CardTitle>
                </CardHeader>
                <CardContent>
                  {tenant ? (
                    <div className="space-y-3 text-sm">
                      <div>
                        <p className="text-muted-foreground">Name</p>
                        <p className="font-medium">{tenant.name}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Plan</p>
                        <Badge variant="secondary" className="capitalize">{tenant.plan}</Badge>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ──── Display Tab ──── */}
          <TabsContent value="display">
            <div className="grid gap-6">
              <DisplayPreferences />
              <Card>
                <CardHeader>
                  <CardTitle>UI Layout Mode</CardTitle>
                  <CardDescription>Choose how the interface is organized based on your experience level.</CardDescription>
                </CardHeader>
                <CardContent>
                  <LayoutModeSelector />
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* ──── Units & Locale Tab ──── */}
          <TabsContent value="units">
            <UnitsLocalePreferences />
          </TabsContent>

          {/* ──── Dashboard Tab ──── */}
          <TabsContent value="dashboard">
            <DashboardPreferences />
          </TabsContent>

          {/* ──── Data & Privacy Tab ──── */}
          <TabsContent value="data">
            <Card>
              <CardHeader>
                <CardTitle>Data & Privacy</CardTitle>
                <CardDescription>Export your data or permanently remove your account.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between gap-4 py-2">
                  <div>
                    <p className="text-sm font-medium">Export All Data</p>
                    <p className="text-xs text-muted-foreground">
                      Download a JSON archive of your grows, readings, and preferences.
                    </p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => toast.info("Data export coming soon")}>
                    <Download className="mr-1 size-3" /> Export
                  </Button>
                </div>
                <Separator />
                <div className="flex items-center justify-between gap-4 py-2">
                  <div>
                    <p className="text-sm font-medium text-destructive">Delete Account</p>
                    <p className="text-xs text-muted-foreground">
                      Permanently delete your account and all associated data. This action cannot be undone.
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="text-destructive hover:text-destructive" onClick={() => toast.info("Account deletion coming soon — contact support")}>
                    <Trash2 className="mr-1 size-3" /> Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
}

/* ─────────────────── Display Preferences ─────────────────── */

function DisplayPreferences() {
  const { prefs, update, loading } = usePreferences();
  const [busy, setBusy] = useState(false);

  const save = async (patch: Record<string, unknown>) => {
    setBusy(true);
    try {
      await update(patch);
      toast.success("Preference saved");
    } catch {
      toast.error("Failed to save preference");
    } finally {
      setBusy(false);
    }
  };

  const disabled = loading || busy;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Appearance</CardTitle>
        <CardDescription>Customize the look and feel of the application.</CardDescription>
      </CardHeader>
      <CardContent className="divide-y">
        <PrefSelect
          label="Theme"
          description="Color scheme for the interface"
          value={prefs.theme}
          options={THEMES}
          onValueChange={(v) => save({ theme: v })}
          disabled={disabled}
        />
        <PrefToggle
          label="Compact Numbers"
          description="Show large numbers in abbreviated form (e.g. 1.2K instead of 1,200)"
          checked={prefs.compact_numbers}
          onCheckedChange={(v) => save({ compact_numbers: v })}
          disabled={disabled}
        />
        <PrefToggle
          label="Show Onboarding"
          description="Display the getting-started guide for new users"
          checked={prefs.show_onboarding}
          onCheckedChange={(v) => save({ show_onboarding: v })}
          disabled={disabled}
        />
      </CardContent>
    </Card>
  );
}

/* ─────────────────── Units & Locale Preferences ─────────────────── */

function UnitsLocalePreferences() {
  const { prefs, update, loading } = usePreferences();
  const [busy, setBusy] = useState(false);

  const save = async (patch: Record<string, unknown>) => {
    setBusy(true);
    try {
      await update(patch);
      toast.success("Preference saved");
    } catch {
      toast.error("Failed to save preference");
    } finally {
      setBusy(false);
    }
  };

  const disabled = loading || busy;

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Units</CardTitle>
          <CardDescription>Configure measurement units used across the app.</CardDescription>
        </CardHeader>
        <CardContent className="divide-y">
          <PrefSelect
            label="Temperature"
            description="Unit for all temperature readings"
            value={prefs.temp_unit}
            options={TEMP_UNITS}
            onValueChange={(v) => save({ temp_unit: v })}
            disabled={disabled}
          />
          <PrefSelect
            label="Measurement System"
            description="Affects default unit choices for new metrics"
            value={prefs.measurement_system}
            options={MEASUREMENT_SYSTEMS}
            onValueChange={(v) => save({ measurement_system: v })}
            disabled={disabled}
          />
          <PrefSelect
            label="Wind Speed"
            description="Unit for wind speed display"
            value={prefs.wind_unit}
            options={WIND_UNITS}
            onValueChange={(v) => save({ wind_unit: v })}
            disabled={disabled}
          />
          <PrefSelect
            label="Pressure"
            description="Unit for barometric pressure"
            value={prefs.pressure_unit}
            options={PRESSURE_UNITS}
            onValueChange={(v) => save({ pressure_unit: v })}
            disabled={disabled}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Locale</CardTitle>
          <CardDescription>Date, time, and regional formatting.</CardDescription>
        </CardHeader>
        <CardContent className="divide-y">
          <PrefSelect
            label="Date Format"
            description="How dates are displayed throughout the app"
            value={prefs.date_format}
            options={DATE_FORMATS}
            onValueChange={(v) => save({ date_format: v })}
            disabled={disabled}
          />
          <PrefSelect
            label="Time Format"
            description="12-hour or 24-hour clock"
            value={prefs.time_format}
            options={TIME_FORMATS}
            onValueChange={(v) => save({ time_format: v })}
            disabled={disabled}
          />
          <PrefSelect
            label="Week Starts On"
            description="First day of the week in calendars"
            value={prefs.week_start}
            options={WEEK_STARTS}
            onValueChange={(v) => save({ week_start: v })}
            disabled={disabled}
          />
          <TimezoneSelector
            value={prefs.timezone}
            onValueChange={(v) => save({ timezone: v })}
            disabled={disabled}
          />
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────────────── Timezone Selector ─────────────────── */

function TimezoneSelector({
  value,
  onValueChange,
  disabled,
}: {
  value: string;
  onValueChange: (v: string) => void;
  disabled?: boolean;
}) {
  const common = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Anchorage",
    "Pacific/Honolulu",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
    "Australia/Sydney",
    "Pacific/Auckland",
  ];
  const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const all = Array.from(new Set([detected, value, ...common]));

  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div className="min-w-0">
        <p className="text-sm font-medium">Timezone</p>
        <p className="text-xs text-muted-foreground">Used for scheduling and time displays</p>
      </div>
      <Select value={value} onValueChange={(v) => onValueChange(v ?? "")} disabled={disabled}>
        <SelectTrigger className="w-full sm:w-[220px] shrink-0">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {all.map((tz) => (
            <SelectItem key={tz} value={tz}>
              {tz.replace(/_/g, " ")}{tz === detected ? " (detected)" : ""}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

/* ─────────────────── Dashboard Preferences ─────────────────── */

function DashboardPreferences() {
  const { prefs, update, loading } = usePreferences();
  const [busy, setBusy] = useState(false);

  const { data: growsData, isLoading: loadingGrows } = useApiSWR(
    ["dashboard-grows"],
    (token) => listGrows(token),
  );
  const grows = (Array.isArray(growsData) ? growsData : (growsData as { items?: { id: string; name: string }[] } | undefined)?.items ?? [])
    .map((g: { id: string; name: string }) => ({ id: g.id, name: g.name }));

  const save = async (patch: Record<string, unknown>) => {
    setBusy(true);
    try {
      await update(patch);
      toast.success("Preference saved");
    } catch {
      toast.error("Failed to save preference");
    } finally {
      setBusy(false);
    }
  };

  const disabled = loading || busy;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dashboard Defaults</CardTitle>
        <CardDescription>Configure the default dashboard experience.</CardDescription>
      </CardHeader>
      <CardContent className="divide-y">
        <div className="flex items-center justify-between gap-4 py-3">
          <div className="min-w-0">
            <p className="text-sm font-medium">Default Grow</p>
            <p className="text-xs text-muted-foreground">
              Which grow is shown when you open the dashboard
            </p>
          </div>
          {loadingGrows ? (
            <Skeleton className="h-9 w-[180px]" />
          ) : (
            <Select
              value={prefs.default_grow_id || "_none"}
              onValueChange={(v) => save({ default_grow_id: v === "_none" ? "" : v })}
              disabled={disabled}
            >
              <SelectTrigger className="w-full sm:w-[180px] shrink-0">
                <SelectValue placeholder="Auto (most recent)" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="_none">Auto (most recent)</SelectItem>
                {grows.map((g) => (
                  <SelectItem key={g.id} value={g.id}>
                    {g.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/* ─────────────────── Layout Mode Selector ─────────────────── */

function LayoutModeSelector() {
  const { mode: currentMode, setMode } = useLayoutMode();
  const [switching, setSwitching] = useState<LayoutMode | null>(null);

  const handleSelect = async (mode: LayoutMode) => {
    if (mode === currentMode) return;
    setSwitching(mode);
    try {
      await setMode(mode);
    } finally {
      setSwitching(null);
    }
  };

  const modes = Object.values(LAYOUT_CONFIGS);

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      {modes.map((cfg) => (
        <button
          key={cfg.mode}
          onClick={() => handleSelect(cfg.mode)}
          disabled={switching !== null}
          className={`relative rounded-lg border p-4 text-left transition-colors hover:bg-accent/50 ${
            currentMode === cfg.mode
              ? "border-primary bg-primary/5"
              : "border-border"
          }`}
        >
          {currentMode === cfg.mode && (
            <div className="absolute right-2 top-2">
              <Check className="size-4 text-primary" />
            </div>
          )}
          <p className="font-medium text-sm">{cfg.label}</p>
          <p className="mt-1 text-xs text-muted-foreground">{cfg.description}</p>
          <Badge variant="outline" className="mt-2 text-[10px]">
            {cfg.density}
          </Badge>
          {switching === cfg.mode && (
            <Loader2 className="absolute right-2 top-2 size-4 animate-spin" />
          )}
        </button>
      ))}
    </div>
  );
}
