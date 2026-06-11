"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  listTents,
  type ScheduleResponse,
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
import { PageHeader } from "@/components/page-header";
import { PageSkeleton } from "@/components/page-skeleton";
import { cn } from "@/lib/utils";
import {
  Plus,
  MoreHorizontal,
  Trash2,
  ToggleLeft,
  ToggleRight,
  Calendar,
  Loader2,
  Lightbulb,
  Fan,
  Snowflake,
  Droplets,
  Settings,
} from "lucide-react";
import { toast } from "sonner";
import { useConfirm } from "@/components/confirm-dialog";

interface TentOption {
  id: string;
  name: string;
}

const typeIcon: Record<string, React.ReactNode> = {
  light: <Lightbulb className="size-4" />,
  fan: <Fan className="size-4" />,
  hvac: <Snowflake className="size-4" />,
  pump: <Droplets className="size-4" />,
};

export default function SchedulesPage() {
  const confirm = useConfirm();
  const [schedules, setSchedules] = useState<ScheduleResponse[]>([]);
  const [tents, setTents] = useState<TentOption[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [s, t] = await Promise.all([
        listSchedules(token),
        listTents(token),
      ]);
      setSchedules(s);
      setTents(t.map((t: { id: string; name: string }) => ({ id: t.id, name: t.name })));
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load schedules");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleToggle = async (sched: ScheduleResponse) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateSchedule(token, sched.id, { enabled: !sched.enabled });
      toast.success(sched.enabled ? "Schedule disabled" : "Schedule enabled");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to toggle schedule"); }
  };

  const handleDelete = async (id: string) => {
    const ok = await confirm({ title: "Delete Schedule", description: "This schedule will be permanently deleted.", confirmText: "Delete", variant: "destructive" });
    if (!ok) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteSchedule(token, id);
      toast.success("Schedule deleted");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete schedule"); }
  };

  if (loading) return <PageSkeleton rows={4} cards />;

  return (
    <>
      <PageHeader
        title="Schedules"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Schedules" }]}
        actions={
          <Button size="sm" onClick={() => setShowCreate(true)}>
            <Plus className="mr-1 size-4" />
            New Schedule
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {schedules.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Calendar className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No schedules configured</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Create a schedule to automate lights, fans, HVAC, and pumps.
            </p>
            <Button className="mt-4" onClick={() => setShowCreate(true)}>
              <Plus className="mr-1 size-4" />
              New Schedule
            </Button>
          </Card>
        ) : (
          <div className="space-y-3">
            {schedules.map((sched) => (
              <Card key={sched.id} className="flex items-center justify-between p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "size-2 rounded-full",
                        sched.enabled ? "bg-green-500" : "bg-muted-foreground/40"
                      )}
                    />
                    <span className="text-muted-foreground">
                      {typeIcon[sched.schedule_type] || <Settings className="size-4" />}
                    </span>
                    <span className="font-medium">{sched.name}</span>
                    <Badge variant="secondary">{sched.schedule_type}</Badge>
                    {sched.stage && (
                      <Badge variant="outline">{sched.stage}</Badge>
                    )}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">
                    ON {sched.on_time} → OFF {sched.off_time}
                    {" · "}
                    Tent: {tents.find((t) => t.id === sched.tent_id)?.name || sched.tent_id.slice(0, 8)}
                  </p>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="size-8" />}>
                    <MoreHorizontal className="size-4" />
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleToggle(sched)}>
                      {sched.enabled ? (
                        <ToggleLeft className="mr-2 size-4" />
                      ) : (
                        <ToggleRight className="mr-2 size-4" />
                      )}
                      {sched.enabled ? "Disable" : "Enable"}
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      variant="destructive"
                      onClick={() => handleDelete(sched.id)}
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
      </div>

      <CreateScheduleDialog
        tents={tents}
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

function CreateScheduleDialog({
  tents,
  open,
  onOpenChange,
  onCreated,
}: {
  tents: TentOption[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState("");
  const [tentId, setTentId] = useState(tents[0]?.id || "");
  const [scheduleType, setScheduleType] = useState("light");
  const [onTime, setOnTime] = useState("06:00");
  const [offTime, setOffTime] = useState("18:00");
  const [stage, setStage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await createSchedule(token, {
        tent_id: tentId,
        name,
        schedule_type: scheduleType,
        on_time: onTime,
        off_time: offTime,
        ...(stage ? { stage } : {}),
      });
      toast.success("Schedule created");
      onCreated();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to create schedule");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Schedule</DialogTitle>
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
          <div className="space-y-2">
            <Label>Tent</Label>
            <Select value={tentId} onValueChange={(v) => setTentId(v ?? "")}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select a tent" />
              </SelectTrigger>
              <SelectContent>
                {tents.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>Type</Label>
              <Select value={scheduleType} onValueChange={(v) => setScheduleType(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["light", "fan", "hvac", "pump"].map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Stage (optional)</Label>
              <Select value={stage} onValueChange={(v) => setStage(v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Any stage" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Any stage</SelectItem>
                  {["seedling", "vegetative", "flowering", "ripening", "harvesting", "drying", "curing"].map((s) => (
                    <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <Label>ON Time</Label>
              <Input
                type="time"
                value={onTime}
                onChange={(e) => setOnTime(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>OFF Time</Label>
              <Input
                type="time"
                value={offTime}
                onChange={(e) => setOffTime(e.target.value)}
              />
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
