"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useConfirm } from "@/components/confirm-dialog";
import { formatDateTime } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { PageHeader } from "@/components/page-header";
import { getAccessToken } from "@/lib/auth";
import {
  listDevices,
  registerDevice,
  pairDevice,
  revokeDevice,
  deleteDevice,
  updateDevice,
  getDeviceQrUrl,
  listTents,
  type DeviceResponse,
  type DeviceRegisterResponse,
  type TentResponse,
} from "@/lib/api";
import {
  Plus,
  MoreHorizontal,
  Pencil,
  QrCode,
  ShieldOff,
  Trash2,
  Cpu,
  Copy,
  Check,
  Loader2,
  MapPin,
  Camera,
} from "lucide-react";
import { toast } from "sonner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CameraGrid } from "@/components/camera-grid";

type ModalState =
  | { type: "none" }
  | { type: "register" }
  | { type: "registered"; data: DeviceRegisterResponse }
  | { type: "pair" }
  | { type: "qr"; deviceId: string }
  | { type: "rename"; device: DeviceResponse };

export default function DevicesPage() {
  const confirm = useConfirm();
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<ModalState>({ type: "none" });
  const [registerLabel, setRegisterLabel] = useState("");
  const [renameLabel, setRenameLabel] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const token = getAccessToken() ?? "";

  const refresh = useCallback(async () => {
    try {
      const [devData, tentData] = await Promise.all([
        listDevices(token),
        listTents(token),
      ]);
      setDevices(devData);
      setTents(tentData);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load devices");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const result = await registerDevice(token, registerLabel || undefined);
      toast.success("Device registered");
      setModal({ type: "registered", data: result });
      setRegisterLabel("");
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to register device");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRevoke(deviceId: string) {
    if (!await confirm({ title: "Revoke Device", description: "Revoke this device's credentials? It will need to be re-paired.", confirmLabel: "Revoke", variant: "destructive" })) return;
    try {
      await revokeDevice(token, deviceId);
      toast.success("Device credentials revoked");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to revoke device"); }
  }

  async function handleDelete(deviceId: string) {
    if (!await confirm({ title: "Delete Device", description: "Permanently delete this device?", confirmLabel: "Delete", variant: "destructive" })) return;
    try {
      await deleteDevice(token, deviceId);
      toast.success("Device deleted");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete device"); }
  }

  async function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (modal.type !== "rename") return;
    setSubmitting(true);
    try {
      await updateDevice(token, modal.device.device_id, { label: renameLabel });
      toast.success("Device renamed");
      setModal({ type: "none" });
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to rename device");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleTentAssign(deviceId: string, tentId: string) {
    try {
      if (tentId === "" || tentId === "none") {
        await updateDevice(token, deviceId, { unassign_tent: true });
      } else {
        await updateDevice(token, deviceId, { tent_id: tentId });
      }
      toast.success("Device assignment updated");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to assign device"); }
  }

  const statusVariant = (status: string) => {
    if (status === "online") return "default" as const;
    if (status === "paired") return "secondary" as const;
    if (status === "revoked") return "destructive" as const;
    return "outline" as const;
  };

  return (
    <>
      <PageHeader
        title="Devices"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Devices" }]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setModal({ type: "pair" })}>
              <Cpu className="mr-1 size-4" />
              Pair Device
            </Button>
            <Button size="sm" onClick={() => setModal({ type: "register" })}>
              <Plus className="mr-1 size-4" />
              Register Device
            </Button>
          </div>
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        <Tabs defaultValue="sensors" className="w-full">
          <TabsList>
            <TabsTrigger value="sensors">
              <Cpu className="mr-1.5 size-3.5" />
              Sensors
            </TabsTrigger>
            <TabsTrigger value="cameras">
              <Camera className="mr-1.5 size-3.5" />
              Cameras
            </TabsTrigger>
          </TabsList>
          <TabsContent value="sensors" className="mt-4">
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="p-4">
                <Skeleton className="mb-2 h-5 w-32" />
                <Skeleton className="mb-1 h-3 w-48" />
                <Skeleton className="h-3 w-24" />
              </Card>
            ))}
          </div>
        ) : devices.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Cpu className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No devices registered</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Register your first IoT sensor to start collecting data.
            </p>
            <Button className="mt-4" onClick={() => setModal({ type: "register" })}>
              <Plus className="mr-1 size-4" />
              Register your first device
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {devices.map((d) => (
              <Card key={d.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium">{d.label || d.device_id}</p>
                    <p className="truncate font-mono text-xs text-muted-foreground">{d.device_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={statusVariant(d.status)}>{d.status}</Badge>
                    <DropdownMenu>
                      <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" />}>
                        <MoreHorizontal className="size-4" />
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => {
                            setRenameLabel(d.label ?? "");
                            setModal({ type: "rename", device: d });
                          }}
                        >
                          <Pencil className="mr-2 size-4" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => setModal({ type: "qr", deviceId: d.device_id })}
                        >
                          <QrCode className="mr-2 size-4" />
                          QR Code
                        </DropdownMenuItem>
                        {d.status !== "revoked" && (
                          <DropdownMenuItem onClick={() => handleRevoke(d.device_id)}>
                            <ShieldOff className="mr-2 size-4" />
                            Revoke
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          onClick={() => handleDelete(d.device_id)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="mr-2 size-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
                {d.last_seen && (
                  <p className="mt-2 text-xs text-muted-foreground">
                    Last seen: {formatDateTime(d.last_seen)}
                  </p>
                )}
                {d.firmware_version && (
                  <p className="text-xs text-muted-foreground">FW: {d.firmware_version}</p>
                )}
                {d.status !== "revoked" && tents.length > 0 && (
                  <div className="mt-3 flex items-center gap-2">
                    <MapPin className="size-3.5 text-muted-foreground" />
                    <Select
                      value={d.tent_id ?? "none"}
                      onValueChange={(val) => handleTentAssign(d.device_id, !val || val === "none" ? "" : val)}
                    >
                      <SelectTrigger className="h-7 flex-1 text-xs">
                        <SelectValue placeholder="Assign Grow Space">
                          {d.tent_id
                            ? (tents.find((t) => t.id === d.tent_id)?.name ?? "Unknown")
                            : "Unassigned"}
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">Unassigned</SelectItem>
                        {tents.map((t) => (
                          <SelectItem key={t.id} value={t.id}>
                            {t.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
          </TabsContent>
          <TabsContent value="cameras" className="mt-4">
            <CameraGrid />
          </TabsContent>
        </Tabs>
      </div>

      {/* Register Dialog */}
      <Dialog open={modal.type === "register"} onOpenChange={(open) => !open && setModal({ type: "none" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Register New Device</DialogTitle>
            <DialogDescription>Add a new IoT device to your network.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleRegister} className="space-y-4">
            <div className="space-y-2">
              <Label>Label (optional)</Label>
              <Input
                value={registerLabel}
                onChange={(e) => setRegisterLabel(e.target.value)}
                placeholder="e.g. Tent A Sensor Hub"
              />
            </div>
            <DialogFooter>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting && <Loader2 className="mr-2 size-4 animate-spin" />}
                {submitting ? "Creating…" : "Create Device"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Registered — show PSK */}
      <Dialog open={modal.type === "registered"} onOpenChange={(open) => !open && setModal({ type: "none" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="text-primary">Device Created</DialogTitle>
            <DialogDescription>
              Save the pre-shared key below — you won&apos;t see it again.
            </DialogDescription>
          </DialogHeader>
          {modal.type === "registered" && (
            <div className="space-y-3">
              <CopyField label="Device ID" value={modal.data.device_id} />
              <CopyField label="Pre-Shared Key (PSK)" value={modal.data.psk} />
            </div>
          )}
          <DialogFooter>
            <Button className="w-full" onClick={() => setModal({ type: "none" })}>
              Done
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* QR Code Dialog */}
      <Dialog open={modal.type === "qr"} onOpenChange={(open) => !open && setModal({ type: "none" })}>

      {/* Pair Device Dialog */}
      <PairDeviceDialog
        open={modal.type === "pair"}
        onOpenChange={(open) => { if (!open) setModal({ type: "none" }); }}
        tents={tents}
        onPaired={refresh}
      />
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Device QR Code</DialogTitle>
          </DialogHeader>
          {modal.type === "qr" && (
            <>
              <div className="flex justify-center rounded-md bg-white p-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`${getDeviceQrUrl(modal.deviceId)}?token=${token}`}
                  alt="Device QR Code"
                  width={240}
                  height={240}
                />
              </div>
              <p className="text-center font-mono text-xs text-muted-foreground">
                {modal.deviceId}
              </p>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Rename Dialog */}
      <Dialog open={modal.type === "rename"} onOpenChange={(open) => !open && setModal({ type: "none" })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename Device</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleRename} className="space-y-4">
            <Input
              value={renameLabel}
              onChange={(e) => setRenameLabel(e.target.value)}
              placeholder="Device label"
            />
            <DialogFooter>
              <Button type="submit" className="w-full" disabled={submitting}>
                {submitting ? "Saving…" : "Save"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}

function CopyField({ label, value }: { label: string; value: string }) {
  const [copied, setCopied] = useState(false);

  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <div className="mt-1 flex items-center gap-2">
        <code className="flex-1 rounded-md border bg-muted px-3 py-2 text-sm text-primary break-all">
          {value}
        </code>
        <Button
          variant="outline"
          size="icon"
          className="shrink-0"
          onClick={() => {
            navigator.clipboard.writeText(value);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
        >
          {copied ? <Check className="size-4 text-primary" /> : <Copy className="size-4" />}
        </Button>
      </div>
    </div>
  );
}

function PairDeviceDialog({ open, onOpenChange, tents, onPaired }: { open: boolean; onOpenChange: (o: boolean) => void; tents: TentResponse[]; onPaired: () => void }) {
  const [deviceId, setDeviceId] = useState("");
  const [psk, setPsk] = useState("");
  const [tentId, setTentId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const token = getAccessToken();
    if (!token || !deviceId || !psk) return;
    setSubmitting(true);
    try {
      await pairDevice(token, { device_id: deviceId, psk, tent_id: tentId || undefined });
      onOpenChange(false);
      setDeviceId("");
      setPsk("");
      setTentId("");
      onPaired();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Invalid device ID or PSK");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Pair Device</DialogTitle>
          <DialogDescription>
            Enter the device ID and pre-shared key (PSK) from your ESP32 to pair it with your account.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-2">
            <Label>Device ID</Label>
            <Input value={deviceId} onChange={(e) => setDeviceId(e.target.value)} placeholder="e.g. tendril-abc123" required />
          </div>
          <div className="grid gap-2">
            <Label>Pre-Shared Key (PSK)</Label>
            <Input type="password" value={psk} onChange={(e) => setPsk(e.target.value)} placeholder="Enter PSK" required />
          </div>
          <div className="grid gap-2">
            <Label>Assign to Tent (optional)</Label>
            <Select value={tentId} onValueChange={(v) => setTentId(v ?? "")}>
              <SelectTrigger><SelectValue placeholder="No tent" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">None</SelectItem>
                {tents.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <DialogFooter>
            <Button type="submit" className="w-full" disabled={submitting || !deviceId || !psk}>
              {submitting ? <><Loader2 className="mr-2 size-4 animate-spin" /> Pairing…</> : "Pair Device"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
