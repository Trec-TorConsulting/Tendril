"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  revokeDevice,
  deleteDevice,
  updateDevice,
  getDeviceQrUrl,
  type DeviceResponse,
  type DeviceRegisterResponse,
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
} from "lucide-react";

type ModalState =
  | { type: "none" }
  | { type: "register" }
  | { type: "registered"; data: DeviceRegisterResponse }
  | { type: "qr"; deviceId: string }
  | { type: "rename"; device: DeviceResponse };

export default function DevicesPage() {
  const [devices, setDevices] = useState<DeviceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<ModalState>({ type: "none" });
  const [registerLabel, setRegisterLabel] = useState("");
  const [renameLabel, setRenameLabel] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const token = getAccessToken() ?? "";

  const refresh = useCallback(async () => {
    try {
      const data = await listDevices(token);
      setDevices(data);
    } catch {
      /* ignore */
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
      setModal({ type: "registered", data: result });
      setRegisterLabel("");
      refresh();
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRevoke(deviceId: string) {
    await revokeDevice(token, deviceId);
    refresh();
  }

  async function handleDelete(deviceId: string) {
    if (!confirm("Permanently delete this device?")) return;
    await deleteDevice(token, deviceId);
    refresh();
  }

  async function handleRename(e: React.FormEvent) {
    e.preventDefault();
    if (modal.type !== "rename") return;
    setSubmitting(true);
    try {
      await updateDevice(token, modal.device.device_id, { label: renameLabel });
      setModal({ type: "none" });
      refresh();
    } finally {
      setSubmitting(false);
    }
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
          <Button size="sm" onClick={() => setModal({ type: "register" })}>
            <Plus className="mr-1 size-4" />
            Register Device
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
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
                    Last seen: {new Date(d.last_seen).toLocaleString()}
                  </p>
                )}
                {d.firmware_version && (
                  <p className="text-xs text-muted-foreground">FW: {d.firmware_version}</p>
                )}
              </Card>
            ))}
          </div>
        )}
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
