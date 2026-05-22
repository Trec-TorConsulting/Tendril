"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { formatDateTime } from "@/lib/utils";
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { useConfirm } from "@/components/confirm-dialog";
import {
  listIntegrations,
  createIntegration,
  updateIntegration,
  deleteIntegration,
  listDeviceMaps,
  createDeviceMap,
  updateDeviceMap,
  deleteDeviceMap,
  listSyncLogs,
  triggerSync,
  discoverDevices,
  listTents,
  type IntegrationResponse,
  type DeviceMapResponse,
  type SyncLogResponse,
  type DiscoveredDeviceResponse,
  type TentResponse,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Plus,
  MoreHorizontal,
  RefreshCw,
  Trash2,
  Pencil,
  Plug,
  Search,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Wifi,
  WifiOff,
} from "lucide-react";
import { toast } from "sonner";

const INTEGRATION_TYPES = [
  { value: "home_assistant", label: "Home Assistant" },
  { value: "ecowitt", label: "Ecowitt" },
  { value: "pulse", label: "Pulse (Autopot)" },
  { value: "tuya", label: "Tuya Smart" },
  { value: "vivosun", label: "VIVOSUN GrowHub" },
  { value: "mqtt_bridge", label: "MQTT Bridge" },
  { value: "generic_webhook", label: "Generic Webhook" },
];

// Per-type config field definitions for friendly forms
interface ConfigFieldDef {
  key: string;
  label: string;
  type: "text" | "password" | "url" | "number";
  placeholder: string;
  required?: boolean;
}

const CONFIG_FIELDS: Record<string, ConfigFieldDef[]> = {
  vivosun: [
    { key: "email", label: "Vivosun Email", type: "text", placeholder: "your@email.com", required: true },
    { key: "password", label: "Vivosun Password", type: "password", placeholder: "Your Vivosun app password", required: true },
  ],
  pulse: [
    { key: "api_key", label: "API Key", type: "password", placeholder: "Pulse Grow API key from app.pulsegrow.com/account", required: true },
  ],
  home_assistant: [
    { key: "url", label: "Home Assistant URL", type: "url", placeholder: "http://homeassistant.local:8123", required: true },
    { key: "token", label: "Long-Lived Access Token", type: "password", placeholder: "Your HA access token", required: true },
  ],
  ecowitt: [
    { key: "api_key", label: "API Key", type: "password", placeholder: "Ecowitt API key" },
    { key: "app_key", label: "Application Key", type: "password", placeholder: "Ecowitt application key" },
  ],
  tuya: [
    { key: "access_id", label: "Access ID", type: "password", placeholder: "Tuya Cloud project Access ID", required: true },
    { key: "access_secret", label: "Access Secret", type: "password", placeholder: "Tuya Cloud project Access Secret", required: true },
    { key: "region", label: "Region", type: "text", placeholder: "us (us, eu, cn, in)" },
    { key: "uid", label: "App User UID", type: "text", placeholder: "Linked Tuya Smart app user UID (from Devices tab)" },
  ],
  mqtt_bridge: [
    { key: "host", label: "MQTT Broker Host", type: "text", placeholder: "mqtt.example.com", required: true },
    { key: "port", label: "Port", type: "number", placeholder: "1883" },
    { key: "username", label: "Username", type: "text", placeholder: "mqtt-user" },
    { key: "password", label: "Password", type: "password", placeholder: "mqtt-password" },
    { key: "topic_prefix", label: "Topic Prefix", type: "text", placeholder: "tendril/" },
  ],
};

function ConfigFields({ type, config, onChange }: { type: string; config: Record<string, string>; onChange: (config: Record<string, string>) => void }) {
  const fields = CONFIG_FIELDS[type];
  if (!fields) return null;
  return (
    <>
      {fields.map((f) => (
        <div key={f.key} className="grid gap-2">
          <Label>{f.label}{f.required && <span className="text-destructive"> *</span>}</Label>
          <Input
            type={f.type}
            value={config[f.key] || ""}
            onChange={(e) => onChange({ ...config, [f.key]: e.target.value })}
            placeholder={f.placeholder}
          />
        </div>
      ))}
    </>
  );
}

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<IntegrationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [editIntegration, setEditIntegration] = useState<IntegrationResponse | null>(null);
  const [selectedIntegration, setSelectedIntegration] = useState<IntegrationResponse | null>(null);
  const [deviceMaps, setDeviceMaps] = useState<DeviceMapResponse[]>([]);
  const [syncLogs, setSyncLogs] = useState<SyncLogResponse[]>([]);
  const [discovered, setDiscovered] = useState<DiscoveredDeviceResponse[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [showDeviceMapCreate, setShowDeviceMapCreate] = useState(false);
  const confirm = useConfirm();

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [ints, t] = await Promise.all([
        listIntegrations(token),
        listTents(token).catch(() => [] as TentResponse[]),
      ]);
      setIntegrations(ints);
      setTents(t);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load integrations");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const loadDetail = async (integration: IntegrationResponse) => {
    const token = getAccessToken();
    if (!token) return;
    setSelectedIntegration(integration);
    try {
      const [maps, logs] = await Promise.all([
        listDeviceMaps(token, integration.id),
        listSyncLogs(token, integration.id),
      ]);
      setDeviceMaps(maps);
      setSyncLogs(logs);
      setDiscovered([]);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load integration details");
    }
  };

  const handleSync = async () => {
    if (!selectedIntegration) return;
    const token = getAccessToken();
    if (!token) return;
    setSyncing(true);
    try {
      const result = await triggerSync(token, selectedIntegration.id);
      toast.success(`Sync complete: ${result.readings_count} readings`);
      loadDetail(selectedIntegration);
    } catch {
      toast.error("Sync failed");
    } finally {
      setSyncing(false);
    }
  };

  const handleDiscover = async () => {
    if (!selectedIntegration) return;
    const token = getAccessToken();
    if (!token) return;
    setDiscovering(true);
    try {
      const devices = await discoverDevices(token, selectedIntegration.id);
      setDiscovered(devices);
      if (devices.length === 0) toast.info("No new devices found");
    } catch {
      toast.error("Discovery failed");
    } finally {
      setDiscovering(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!await confirm({ title: "Delete Integration", description: "This will remove the integration and all device mappings. This cannot be undone.", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteIntegration(token, id);
      if (selectedIntegration?.id === id) setSelectedIntegration(null);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete integration"); }
  };

  const handleToggleEnabled = async (integration: IntegrationResponse) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateIntegration(token, integration.id, { enabled: !integration.enabled });
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to toggle integration"); }
  };

  const handleDeleteDeviceMap = async (deviceId: string) => {
    if (!selectedIntegration) return;
    if (!await confirm({ title: "Remove Device Mapping", description: "Stop syncing this device?", confirmLabel: "Remove", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteDeviceMap(token, selectedIntegration.id, deviceId);
      loadDetail(selectedIntegration);
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to remove device mapping"); }
  };

  if (loading) return <PageSkeleton rows={3} cards />;

  return (
    <>
      <PageHeader
        title="Integrations"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Integrations" }]}
        actions={
          <Button onClick={() => setShowCreate(true)} size="sm">
            <Plus className="mr-1 size-4" /> Add Integration
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {integrations.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Plug className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No integrations configured</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Connect Home Assistant, Ecowitt, or other platforms to sync sensor data.
            </p>
            <Button className="mt-4" size="sm" onClick={() => setShowCreate(true)}>
              <Plus className="mr-1 size-4" /> Add Integration
            </Button>
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
            {/* Integration List */}
            <div className="flex flex-col gap-3">
              {integrations.map((intg) => (
                <Card
                  key={intg.id}
                  className={`cursor-pointer transition-colors hover:border-primary/40 ${selectedIntegration?.id === intg.id ? "border-primary" : ""}`}
                  onClick={() => loadDetail(intg)}
                >
                  <CardContent className="flex items-center gap-3 py-3">
                    <div className={`flex size-9 items-center justify-center rounded-lg ${intg.enabled ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}>
                      {intg.enabled ? <Wifi className="size-4" /> : <WifiOff className="size-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{intg.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{intg.type.replace(/_/g, " ")}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {intg.error_count > 0 && (
                        <Badge variant="destructive" className="text-[10px]">{intg.error_count} errors</Badge>
                      )}
                      <DropdownMenu>
                        <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="size-7 p-0" onClick={(e) => e.stopPropagation()} />}>
                          <MoreHorizontal className="size-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); setEditIntegration(intg); }}>
                            <Pencil className="mr-2 size-4" /> Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleToggleEnabled(intg); }}>
                            {intg.enabled ? <WifiOff className="mr-2 size-4" /> : <Wifi className="mr-2 size-4" />}
                            {intg.enabled ? "Disable" : "Enable"}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem className="text-destructive" onClick={(e) => { e.stopPropagation(); handleDelete(intg.id); }}>
                            <Trash2 className="mr-2 size-4" /> Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Detail Panel */}
            {selectedIntegration ? (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0">
                  <div>
                    <CardTitle>{selectedIntegration.name}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1 capitalize">
                      {selectedIntegration.type.replace(/_/g, " ")} ·{" "}
                      {selectedIntegration.last_synced_at
                        ? `Last sync: ${formatDateTime(selectedIntegration.last_synced_at)}`
                        : "Never synced"}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleDiscover} disabled={discovering}>
                      <Search className="mr-1 size-4" /> {discovering ? "Discovering..." : "Discover"}
                    </Button>
                    <Button size="sm" onClick={handleSync} disabled={syncing}>
                      <RefreshCw className={`mr-1 size-4 ${syncing ? "animate-spin" : ""}`} /> {syncing ? "Syncing..." : "Sync Now"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="devices">
                    <TabsList>
                      <TabsTrigger value="devices">Device Mappings ({deviceMaps.length})</TabsTrigger>
                      <TabsTrigger value="logs">Sync Logs ({syncLogs.length})</TabsTrigger>
                      {discovered.length > 0 && <TabsTrigger value="discovered">Discovered ({discovered.length})</TabsTrigger>}
                    </TabsList>

                    <TabsContent value="devices" className="mt-4">
                      <div className="flex justify-end mb-3">
                        <Button variant="outline" size="sm" onClick={() => setShowDeviceMapCreate(true)}>
                          <Plus className="mr-1 size-4" /> Map Device
                        </Button>
                      </div>
                      {deviceMaps.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-8">No device mappings. Use Discover to find available devices.</p>
                      ) : (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>External ID</TableHead>
                              <TableHead>Name</TableHead>
                              <TableHead>Target</TableHead>
                              <TableHead>Enabled</TableHead>
                              <TableHead className="w-12" />
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {deviceMaps.map((dm) => (
                              <TableRow key={dm.id}>
                                <TableCell className="font-mono text-xs">{dm.external_id}</TableCell>
                                <TableCell>{dm.external_name || "—"}</TableCell>
                                <TableCell className="text-xs text-muted-foreground">
                                  {dm.tent_id ? tents.find((t) => t.id === dm.tent_id)?.name || "Tent" : dm.bucket_id ? "Bucket" : "—"}
                                </TableCell>
                                <TableCell>
                                  <Badge variant={dm.enabled ? "default" : "secondary"}>
                                    {dm.enabled ? "On" : "Off"}
                                  </Badge>
                                </TableCell>
                                <TableCell>
                                  <Button variant="ghost" size="sm" className="size-7 p-0" onClick={() => handleDeleteDeviceMap(dm.id)}>
                                    <Trash2 className="size-4 text-muted-foreground" />
                                  </Button>
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      )}
                    </TabsContent>

                    <TabsContent value="logs" className="mt-4">
                      {syncLogs.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-8">No sync history yet.</p>
                      ) : (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Time</TableHead>
                              <TableHead>Status</TableHead>
                              <TableHead>Readings</TableHead>
                              <TableHead>Error</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {syncLogs.slice(0, 20).map((log) => (
                              <TableRow key={log.id}>
                                <TableCell className="text-xs">{formatDateTime(log.synced_at)}</TableCell>
                                <TableCell>
                                  <SyncStatusBadge status={log.status} />
                                </TableCell>
                                <TableCell>{log.readings_count}</TableCell>
                                <TableCell className="text-xs text-muted-foreground max-w-48 truncate">
                                  {log.error_message || "—"}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      )}
                    </TabsContent>

                    {discovered.length > 0 && (
                      <TabsContent value="discovered" className="mt-4">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Device</TableHead>
                              <TableHead>Type</TableHead>
                              <TableHead>External ID</TableHead>
                              <TableHead className="w-24" />
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {discovered.map((d) => {
                              const alreadyMapped = deviceMaps.some((dm) => dm.external_id === d.external_id);
                              return (
                                <TableRow key={d.external_id}>
                                  <TableCell className="font-medium">{d.name}</TableCell>
                                  <TableCell className="text-xs text-muted-foreground">{d.device_type}</TableCell>
                                  <TableCell className="font-mono text-xs">{d.external_id}</TableCell>
                                  <TableCell>
                                    {alreadyMapped ? (
                                      <Badge variant="secondary">Mapped</Badge>
                                    ) : (
                                      <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => quickMapDevice(d)}>
                                        <Plus className="mr-1 size-3" /> Map
                                      </Button>
                                    )}
                                  </TableCell>
                                </TableRow>
                              );
                            })}
                          </TableBody>
                        </Table>
                      </TabsContent>
                    )}
                  </Tabs>
                </CardContent>
              </Card>
            ) : (
              <Card className="flex items-center justify-center py-16">
                <p className="text-sm text-muted-foreground">Select an integration to view details</p>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Create Integration Dialog */}
      <CreateIntegrationDialog open={showCreate} onOpenChange={setShowCreate} onCreated={refresh} />

      {/* Edit Integration Dialog */}
      {editIntegration && (
        <EditIntegrationDialog
          integration={editIntegration}
          open={!!editIntegration}
          onOpenChange={(open) => { if (!open) setEditIntegration(null); }}
          onUpdated={() => { refresh(); setEditIntegration(null); }}
        />
      )}

      {/* Create Device Map Dialog */}
      {selectedIntegration && (
        <CreateDeviceMapDialog
          open={showDeviceMapCreate}
          onOpenChange={setShowDeviceMapCreate}
          integrationId={selectedIntegration.id}
          tents={tents}
          onCreated={() => loadDetail(selectedIntegration)}
        />
      )}
    </>
  );

  async function quickMapDevice(d: DiscoveredDeviceResponse) {
    if (!selectedIntegration) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await createDeviceMap(token, selectedIntegration.id, {
        external_id: d.external_id,
        external_name: d.name,
        enabled: true,
      });
      toast.success(`Mapped ${d.name}`);
      loadDetail(selectedIntegration);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to map device");
    }
  }
}

// ─── Sub-Components ───────────────────────────────────────────────────────────

function SyncStatusBadge({ status }: { status: string }) {
  switch (status) {
    case "success":
      return <Badge variant="default" className="gap-1"><CheckCircle2 className="size-3" /> Success</Badge>;
    case "error":
      return <Badge variant="destructive" className="gap-1"><XCircle className="size-3" /> Error</Badge>;
    case "partial":
      return <Badge variant="secondary" className="gap-1"><AlertTriangle className="size-3" /> Partial</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
}

function CreateIntegrationDialog({ open, onOpenChange, onCreated }: { open: boolean; onOpenChange: (o: boolean) => void; onCreated: () => void }) {
  const [form, setForm] = useState({ type: "", name: "", poll_interval_s: "300" });
  const [configFields, setConfigFields] = useState<Record<string, string>>({});
  const [configJson, setConfigJson] = useState("{}");
  const [saving, setSaving] = useState(false);

  const hasTypedFields = !!CONFIG_FIELDS[form.type];

  const handleSubmit = async () => {
    const token = getAccessToken();
    if (!token || !form.type || !form.name) return;
    setSaving(true);
    try {
      let config: Record<string, unknown>;
      if (hasTypedFields) {
        config = { ...configFields };
      } else {
        try { config = JSON.parse(configJson); } catch { toast.error("Invalid JSON config"); return; }
      }
      await createIntegration(token, {
        type: form.type,
        name: form.name,
        config,
        poll_interval_s: parseInt(form.poll_interval_s) || undefined,
      });
      toast.success("Integration created");
      onOpenChange(false);
      setForm({ type: "", name: "", poll_interval_s: "300" });
      setConfigFields({});
      setConfigJson("{}");
      onCreated();
    } catch {
      toast.error("Failed to create integration");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Add Integration</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Type</Label>
            <Select value={form.type} onValueChange={(v) => setForm((f) => ({ ...f, type: v ?? "" }))}>
              <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
              <SelectContent>
                {INTEGRATION_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-2">
            <Label>Name</Label>
            <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="My Home Assistant" />
          </div>
          <div className="grid gap-2">
            <Label>Poll Interval (seconds)</Label>
            <Input type="number" value={form.poll_interval_s} onChange={(e) => setForm((f) => ({ ...f, poll_interval_s: e.target.value }))} min={60} />
          </div>
          {hasTypedFields ? (
            <ConfigFields type={form.type} config={configFields} onChange={setConfigFields} />
          ) : (
            <div className="grid gap-2">
              <Label>Configuration (JSON)</Label>
              <textarea
                className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                value={configJson}
                onChange={(e) => setConfigJson(e.target.value)}
                placeholder='{"url": "http://...", "token": "..."}'
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={!form.type || !form.name || saving}>
            {saving ? "Creating..." : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function EditIntegrationDialog({ integration, open, onOpenChange, onUpdated }: { integration: IntegrationResponse; open: boolean; onOpenChange: (o: boolean) => void; onUpdated: () => void }) {
  const [form, setForm] = useState({ name: integration.name, poll_interval_s: String(integration.poll_interval_s || ""), enabled: integration.enabled });
  const initConfig = integration.config as Record<string, string> || {};
  const [configFields, setConfigFields] = useState<Record<string, string>>(initConfig);
  const [configJson, setConfigJson] = useState(JSON.stringify(integration.config, null, 2));
  const [saving, setSaving] = useState(false);

  const hasTypedFields = !!CONFIG_FIELDS[integration.type];

  const handleSubmit = async () => {
    const token = getAccessToken();
    if (!token) return;
    setSaving(true);
    try {
      let config: Record<string, unknown> | undefined;
      if (hasTypedFields) {
        config = { ...configFields };
      } else if (configJson !== JSON.stringify(integration.config, null, 2)) {
        try { config = JSON.parse(configJson); } catch { toast.error("Invalid JSON"); return; }
      }
      await updateIntegration(token, integration.id, {
        name: form.name || undefined,
        enabled: form.enabled,
        poll_interval_s: parseInt(form.poll_interval_s) || undefined,
        config,
      });
      toast.success("Integration updated");
      onUpdated();
    } catch {
      toast.error("Update failed");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Edit Integration</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Name</Label>
            <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          </div>
          <div className="flex items-center gap-3">
            <Switch checked={form.enabled} onCheckedChange={(v) => setForm((f) => ({ ...f, enabled: v }))} />
            <Label>Enabled</Label>
          </div>
          <div className="grid gap-2">
            <Label>Poll Interval (seconds)</Label>
            <Input type="number" value={form.poll_interval_s} onChange={(e) => setForm((f) => ({ ...f, poll_interval_s: e.target.value }))} min={60} />
          </div>
          {hasTypedFields ? (
            <ConfigFields type={integration.type} config={configFields} onChange={setConfigFields} />
          ) : (
            <div className="grid gap-2">
              <Label>Configuration (JSON)</Label>
              <textarea
                className="min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                value={configJson}
                onChange={(e) => setConfigJson(e.target.value)}
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={saving}>{saving ? "Saving..." : "Save"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function CreateDeviceMapDialog({ open, onOpenChange, integrationId, tents, onCreated }: { open: boolean; onOpenChange: (o: boolean) => void; integrationId: string; tents: TentResponse[]; onCreated: () => void }) {
  const [form, setForm] = useState({ external_id: "", external_name: "", tent_id: "" });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    const token = getAccessToken();
    if (!token || !form.external_id) return;
    setSaving(true);
    try {
      await createDeviceMap(token, integrationId, {
        external_id: form.external_id,
        external_name: form.external_name || undefined,
        tent_id: form.tent_id || undefined,
        enabled: true,
      });
      toast.success("Device mapped");
      onOpenChange(false);
      setForm({ external_id: "", external_name: "", tent_id: "" });
      onCreated();
    } catch {
      toast.error("Failed to create mapping");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Map External Device</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>External Device ID</Label>
            <Input value={form.external_id} onChange={(e) => setForm((f) => ({ ...f, external_id: e.target.value }))} placeholder="e.g. sensor_001" />
          </div>
          <div className="grid gap-2">
            <Label>Display Name</Label>
            <Input value={form.external_name} onChange={(e) => setForm((f) => ({ ...f, external_name: e.target.value }))} placeholder="Optional" />
          </div>
          <div className="grid gap-2">
            <Label>Target Tent</Label>
            <Select value={form.tent_id} onValueChange={(v) => setForm((f) => ({ ...f, tent_id: v ?? "" }))}>
              <SelectTrigger><SelectValue placeholder="Select tent" /></SelectTrigger>
              <SelectContent>
                {tents.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={!form.external_id || saving}>{saving ? "Mapping..." : "Create Mapping"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
