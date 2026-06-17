"use client";

import { useState } from "react";
import { Power, PowerOff, Plus, Settings2, Trash2, Wifi, WifiOff, Zap } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { useConfirm } from "@/components/confirm-dialog";
import { PageHeader } from "@/components/page-header";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  createEquipment,
  deleteEquipment,
  EquipmentResponse,
  listEquipment,
  sendEquipmentCommand,
  updateEquipment,
} from "@/lib/api";

const EQUIPMENT_TYPES = [
  { value: "relay", label: "Relay" },
  { value: "dimmer", label: "Dimmer" },
  { value: "smart_plug", label: "Smart Plug" },
  { value: "pump", label: "Pump" },
  { value: "fan_controller", label: "Fan Controller" },
];

const PROTOCOLS = [
  { value: "tasmota_mqtt", label: "Tasmota (MQTT)" },
  { value: "shelly_http", label: "Shelly (HTTP)" },
  { value: "tuya_cloud", label: "Tuya (Cloud)" },
  { value: "generic_mqtt", label: "Generic MQTT" },
  { value: "kasa_local", label: "TP-Link Kasa (Local)" },
];

type ModalState =
  | { type: "none" }
  | { type: "create" }
  | { type: "edit"; equipment: EquipmentResponse };

export default function EquipmentPage() {
  const { data: rawData, isLoading: loading, mutate } = useApiSWR(
    ["equipment"],
    (token) => listEquipment(token),
  );
  const equipment = rawData?.items ?? [];
  const load = mutate;
  const [modal, setModal] = useState<ModalState>({ type: "none" });
  const [submitting, setSubmitting] = useState(false);
  const confirm = useConfirm();

  const handleToggle = async (equip: EquipmentResponse) => {
    const isOn = equip.requested_state?.is_on;
    const action = isOn ? "off" : "on";
    try {
      const token = getAccessToken() ?? "";
      await sendEquipmentCommand(token, equip.id, { action });
      toast.success(`${equip.name} turned ${action.toUpperCase()}`);
      await load();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Command failed";
      toast.error(message);
    }
  };

  const handleDelete = async (equip: EquipmentResponse) => {
    const ok = await confirm({
      title: "Delete Equipment",
      description: `Are you sure you want to delete "${equip.name}"? This will send an OFF command if the device is currently on.`,
      confirmLabel: "Delete",
      variant: "destructive",
    });
    if (!ok) return;

    try {
      const token = getAccessToken() ?? "";
      await deleteEquipment(token, equip.id);
      toast.success(`${equip.name} deleted`);
      await load();
    } catch {
      toast.error("Failed to delete equipment");
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 p-6">
        <PageHeader title="Equipment" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-48 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <PageHeader
        title="Equipment"
        actions={
          <Button onClick={() => setModal({ type: "create" })}>
            <Plus className="mr-2 h-4 w-4" />
            Add Equipment
          </Button>
        }
      />

      {equipment.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <Zap className="mb-4 h-12 w-12 text-muted-foreground" />
            <h3 className="text-lg font-semibold">No equipment configured</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Add relays, smart plugs, or dimmers to control your grow environment.
            </p>
            <Button className="mt-4" onClick={() => setModal({ type: "create" })}>
              <Plus className="mr-2 h-4 w-4" />
              Add First Equipment
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {equipment.map((equip) => (
            <EquipmentCard
              key={equip.id}
              equipment={equip}
              onToggle={() => handleToggle(equip)}
              onEdit={() => setModal({ type: "edit", equipment: equip })}
              onDelete={() => handleDelete(equip)}
            />
          ))}
        </div>
      )}

      {modal.type !== "none" && (
        <EquipmentFormDialog
          open
          mode={modal.type}
          equipment={modal.type === "edit" ? modal.equipment : undefined}
          submitting={submitting}
          onClose={() => setModal({ type: "none" })}
          onSubmit={async (data) => {
            setSubmitting(true);
            try {
              const token = getAccessToken() ?? "";
              if (modal.type === "create") {
                await createEquipment(token, data as Parameters<typeof createEquipment>[1]);
                toast.success("Equipment added");
              } else if (modal.type === "edit") {
                await updateEquipment(token, modal.equipment.id, data);
                toast.success("Equipment updated");
              }
              setModal({ type: "none" });
              await load();
            } catch (err: unknown) {
              const message = err instanceof Error ? err.message : "Operation failed";
              toast.error(message);
            } finally {
              setSubmitting(false);
            }
          }}
        />
      )}
    </div>
  );
}

// ── Equipment Card ────────────────────────────────────────────────────────────

function EquipmentCard({
  equipment,
  onToggle,
  onEdit,
  onDelete,
}: {
  equipment: EquipmentResponse;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const isOn = !!equipment.requested_state?.is_on;
  const confirmed = equipment.confirmed_state?.is_on;
  const powerW = equipment.confirmed_state?.power_w as number | undefined;
  const protocol = PROTOCOLS.find((p) => p.value === equipment.protocol);

  return (
    <Card className={!equipment.enabled ? "opacity-60" : undefined}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{equipment.name}</CardTitle>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onEdit}>
            <Settings2 className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={onDelete}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              {isOn ? (
                <Power className="h-5 w-5 text-green-500" />
              ) : (
                <PowerOff className="h-5 w-5 text-muted-foreground" />
              )}
              <span className="text-2xl font-bold">{isOn ? "ON" : "OFF"}</span>
            </div>
            {powerW !== undefined && (
              <p className="text-xs text-muted-foreground">{powerW.toFixed(1)}W</p>
            )}
          </div>
          <Switch checked={isOn} onCheckedChange={onToggle} disabled={!equipment.enabled} />
        </div>

        <div className="mt-4 flex flex-wrap gap-1">
          <Badge variant="outline">{protocol?.label ?? equipment.protocol}</Badge>
          <Badge variant={equipment.enabled ? "default" : "secondary"}>
            {equipment.enabled ? "Enabled" : "Disabled"}
          </Badge>
          {confirmed !== undefined && (
            <Badge variant="outline" className="gap-1">
              {confirmed ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              {confirmed === isOn ? "Confirmed" : "Unconfirmed"}
            </Badge>
          )}
        </div>

        {equipment.last_confirmed_at && (
          <p className="mt-2 text-xs text-muted-foreground">
            Last confirmed: {new Date(equipment.last_confirmed_at).toLocaleString()}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// ── Equipment Form Dialog ─────────────────────────────────────────────────────

function EquipmentFormDialog({
  open,
  mode,
  equipment,
  submitting,
  onClose,
  onSubmit,
}: {
  open: boolean;
  mode: "create" | "edit";
  equipment?: EquipmentResponse;
  submitting: boolean;
  onClose: () => void;
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
}) {
  const [name, setName] = useState(equipment?.name ?? "");
  const [equipmentType, setEquipmentType] = useState(equipment?.equipment_type ?? "relay");
  const [protocol, setProtocol] = useState(equipment?.protocol ?? "tasmota_mqtt");
  const [configJson, setConfigJson] = useState(
    equipment?.protocol_config ? JSON.stringify(equipment.protocol_config, null, 2) : "{}",
  );
  const [maxOn, setMaxOn] = useState(equipment?.max_on_minutes?.toString() ?? "");
  const [cooldown, setCooldown] = useState(equipment?.cooldown_minutes?.toString() ?? "0");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    let parsedConfig: Record<string, unknown>;
    try {
      parsedConfig = JSON.parse(configJson);
    } catch {
      toast.error("Invalid JSON in protocol config");
      return;
    }

    const data: Record<string, unknown> = {
      name,
      equipment_type: equipmentType,
      protocol,
      protocol_config: parsedConfig,
      max_on_minutes: maxOn ? parseInt(maxOn, 10) : null,
      cooldown_minutes: parseInt(cooldown, 10) || 0,
    };

    await onSubmit(data);
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{mode === "create" ? "Add Equipment" : "Edit Equipment"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Exhaust Fan"
              required
            />
          </div>

          <div>
            <Label htmlFor="type">Type</Label>
            <Select value={equipmentType} onValueChange={(v) => setEquipmentType(v ?? "relay")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {EQUIPMENT_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="protocol">Protocol</Label>
            <Select value={protocol} onValueChange={(v) => setProtocol(v ?? "tasmota_mqtt")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROTOCOLS.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="config">Protocol Config (JSON)</Label>
            <textarea
              id="config"
              className="min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
              value={configJson}
              onChange={(e) => setConfigJson(e.target.value)}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              {protocol === "tasmota_mqtt" && '{"mqtt_topic": "your_tasmota_topic"}'}
              {protocol === "shelly_http" && '{"ip_address": "192.168.1.x", "generation": 2, "channel": 0}'}
              {protocol === "generic_mqtt" && '{"command_topic": "topic/set", "on_payload": "ON", "off_payload": "OFF"}'}
              {protocol === "tuya_cloud" && '{"integration_id": "uuid", "external_device_id": "tuya_id"}'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="maxOn">Max ON (minutes)</Label>
              <Input
                id="maxOn"
                type="number"
                value={maxOn}
                onChange={(e) => setMaxOn(e.target.value)}
                placeholder="None"
                min={1}
              />
            </div>
            <div>
              <Label htmlFor="cooldown">Cooldown (minutes)</Label>
              <Input
                id="cooldown"
                type="number"
                value={cooldown}
                onChange={(e) => setCooldown(e.target.value)}
                min={0}
              />
            </div>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={submitting || !name.trim()}>
              {submitting ? "Saving..." : mode === "create" ? "Add" : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
