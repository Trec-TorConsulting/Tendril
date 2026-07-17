"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listTasks,
  completeTask,
  deleteTask,
  createTask,
  updateTask,
  skipTask,
  getTaskRoutines,
  completeRoutine,
  type TaskItem,
  type RoutineGroup,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatCalendarDate } from "@/lib/utils";
import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock,
  SkipForward,
  Trash2,
  MoreHorizontal,
  Repeat,
  Calendar as CalendarIcon,
  ListChecks,
  Bot,
  Zap,
  Plus,
  Pencil,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { SwipeableCard } from "@/components/swipeable-card";
import { useApiSWR } from "@/lib/swr";

const PRIORITY_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  low: "secondary",
  medium: "outline",
  high: "default",
  urgent: "destructive",
};

const CATEGORY_LABELS: Record<string, string> = {
  ph_check: "pH Check",
  ec_check: "EC Check",
  flush_and_fill: "Flush & Fill",
  water_change: "Water Change",
  water_temp: "Water Temp",
  top_off: "Top Off",
  watering: "Watering",
  health_check: "Health Check",
  pest_check: "Pest Check",
  defoliation: "Defoliation",
  trichome_check: "Trichomes",
  flush: "Flush",
  flush_start: "Start Flush",
  harvest: "Harvest",
  calmag: "CalMag",
  top_dress: "Top Dress",
  feeding: "Feeding",
  health_response: "Health Action",
  alert_response: "Alert Response",
  stage_transition: "Stage Prep",
  followup: "Follow-up",
  water_level: "Water Level",
  nozzle_check: "Nozzle Check",
  circulation_check: "Circulation",
  algae_check: "Algae Check",
  root_check: "Root Check",
  weather_check: "Weather Check",
  soil_amendment: "Soil Amendment",
  runoff_check: "Runoff Check",
  dryback_check: "Dry-back",
  ipm_spray: "IPM Spray",
  equipment_check: "Equipment",
  meter_calibration: "Calibration",
  photo_documentation: "Photo Doc",
  nutrient_prep: "Nutrient Prep",
  deep_clean: "Deep Clean",
  carbon_filter: "Carbon Filter",
  air_stone: "Air Stone",
  light_check: "Light Check",
  harvest_check: "Harvest Check",
  pest_scout: "Field Scout",
  companion_check: "Companions",
  rain_gauge: "Rain Gauge",
  verify_automation: "Verify Auto",
};

const ROUTINE_LABELS: Record<string, string> = {
  morning: "Morning",
  evening: "Evening",
  weekly: "Weekly",
  biweekly: "Biweekly",
  monthly: "Monthly",
  on_demand: "Action",
};

function getCategoryLabel(cat: string | null) {
  return cat ? CATEGORY_LABELS[cat] || cat.replace(/_/g, " ") : null;
}

function getRoutineLabel(routine: string | null) {
  return routine ? ROUTINE_LABELS[routine] || routine : null;
}

function getIntervalLabel(days: number | null): string | null {
  if (!days) return null;
  const map: Record<number, string> = { 1: "Daily", 2: "Every 2 days", 3: "Every 3 days", 7: "Weekly", 14: "Biweekly", 30: "Monthly" };
  return map[days] ?? `Every ${days} days`;
}

export function TasksTab({ growId }: { growId: string }) {
  const [view, setView] = useState<"today" | "routines" | "all">("today");
  const todayEOD = new Date();
  todayEOD.setHours(23, 59, 59, 999);

  const {
    data: rawTasks,
    mutate,
  } = useApiSWR(["grow", "tasks", growId, view], async (token) => {
    const filters: Record<string, string> = { grow_cycle_id: growId, status: "pending" };
    if (view === "today") filters.due_to = todayEOD.toISOString();
    return listTasks(token, filters);
  });
  const tasks: TaskItem[] = rawTasks ?? [];

  const {
    data: routinesData,
    mutate: mutateRoutines,
  } = useApiSWR(view === "routines" ? ["grow", "routines", growId] : null, async (token) => {
    return getTaskRoutines(token, growId);
  });

  // Create / Edit dialog
  const [taskDialog, setTaskDialog] = useState(false);
  const [editingTask, setEditingTask] = useState<TaskItem | null>(null);
  const [taskForm, setTaskForm] = useState({ title: "", description: "", priority: "medium", category: "", due_date: "", recurring: "" });
  const [taskSaving, setTaskSaving] = useState(false);

  const refresh = () => { mutate(); mutateRoutines(); };

  const handleComplete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await completeTask(id, token);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to complete task"); }
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteTask(id, token);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete task"); }
  };

  const handleSkip = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await skipTask(id, token);
      toast.success("Skipped — next occurrence scheduled");
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to skip task"); }
  };

  const handleCompleteRoutine = async (group: RoutineGroup) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const { completed } = await completeRoutine(group.tasks.map((t) => t.id), token);
      toast.success(`Completed ${completed} ${group.label} tasks`);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to complete routine"); }
  };

  const openCreateDialog = () => {
    setEditingTask(null);
    setTaskForm({ title: "", description: "", priority: "medium", category: "", due_date: "", recurring: "" });
    setTaskDialog(true);
  };

  const openEditDialog = (task: TaskItem) => {
    setEditingTask(task);
    setTaskForm({
      title: task.title,
      description: task.description || "",
      priority: task.priority,
      category: task.category || "",
      due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 10) : "",
      recurring: task.recurring || "",
    });
    setTaskDialog(true);
  };

  const handleTaskSave = async () => {
    const token = getAccessToken();
    if (!token || !taskForm.title.trim()) return;
    setTaskSaving(true);
    try {
      if (editingTask) {
        const data: Record<string, unknown> = {
          title: taskForm.title.trim(),
          description: taskForm.description.trim() || null,
          priority: taskForm.priority,
        };
        if (taskForm.category) data.category = taskForm.category;
        if (taskForm.due_date) data.due_date = new Date(taskForm.due_date).toISOString();
        if (taskForm.recurring) data.recurring = taskForm.recurring;
        else data.recurring = null;
        await updateTask(editingTask.id, data, token);
      } else {
        const data: Parameters<typeof createTask>[0] = {
          title: taskForm.title.trim(),
          grow_cycle_id: growId,
          priority: taskForm.priority,
        };
        if (taskForm.description.trim()) data.description = taskForm.description.trim();
        if (taskForm.category) data.category = taskForm.category;
        if (taskForm.due_date) data.due_date = new Date(taskForm.due_date).toISOString();
        if (taskForm.recurring) data.recurring = taskForm.recurring;
        await createTask(data, token);
      }
      setTaskDialog(false);
      refresh();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save task"); } finally { setTaskSaving(false); }
  };

  const activeTasks = tasks
    .filter((t) => t.status !== "completed" && t.status !== "cancelled" && t.status !== "skipped")
    .sort((a, b) => {
      if (!a.due_date && !b.due_date) return 0;
      if (!a.due_date) return 1;
      if (!b.due_date) return -1;
      return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
    });
  const completedTasks = tasks
    .filter((t) => t.status === "completed")
    .sort((a, b) => {
      if (!a.completed_at && !b.completed_at) return 0;
      if (!a.completed_at) return 1;
      if (!b.completed_at) return -1;
      return new Date(b.completed_at).getTime() - new Date(a.completed_at).getTime();
    });

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {(["today", "routines", "all"] as const).map((v) => (
          <Button
            key={v}
            variant={view === v ? "default" : "outline"}
            size="sm"
            onClick={() => setView(v)}
          >
            {v === "today" ? "Today" : v === "routines" ? "Routines" : "All"}
          </Button>
        ))}
        <div className="ml-auto flex gap-2">
          <Button variant="default" size="sm" onClick={openCreateDialog}>
            <Plus className="mr-1 h-4 w-4" />
            Add Task
          </Button>
          <Button variant="outline" size="sm" render={<Link href="/dashboard/tasks" />}>
            <ListChecks className="mr-1 h-4 w-4" />
            All Tasks
          </Button>
        </div>
      </div>

      {/* ── Routine grouped view ── */}
      {view === "routines" && (
        <div className="space-y-3">
          {!routinesData?.routines?.length ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <ListChecks className="size-8 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">No tasks due today.</p>
              </CardContent>
            </Card>
          ) : (
            routinesData.routines.map((group) => (
              <RoutineCard
                key={group.routine}
                group={group}
                onCompleteAll={handleCompleteRoutine}
                onComplete={handleComplete}
                onDelete={handleDelete}
                onSkip={handleSkip}
                onEdit={openEditDialog}
              />
            ))
          )}
        </div>
      )}

      {/* ── List view (today / all) ── */}
      {view !== "routines" && (
        <>
          {activeTasks.length === 0 && completedTasks.length === 0 && (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-8">
                <ListChecks className="size-8 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">
                  No tasks for this grow yet. They&apos;ll appear as the scheduler generates them.
                </p>
              </CardContent>
            </Card>
          )}

          {activeTasks.map((t) => (
            <SwipeableCard
              key={t.id}
              onSwipeRight={() => handleComplete(t.id)}
              onSwipeLeft={() => handleDelete(t.id)}
            >
              <GrowTaskCard
                task={t}
                onComplete={handleComplete}
                onDelete={handleDelete}
                onSkip={handleSkip}
                onEdit={openEditDialog}
              />
            </SwipeableCard>
          ))}

          {completedTasks.length > 0 && (
            <>
              <h3 className="pt-3 text-sm font-semibold text-muted-foreground">
                Completed ({completedTasks.length})
              </h3>
              {completedTasks.slice(0, 10).map((t) => (
                <Card key={t.id} className="opacity-50">
                  <CardContent className="flex items-center justify-between p-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <CheckCircle2 className="size-4 text-green-500" />
                        <span className="font-medium text-muted-foreground line-through">{t.title}</span>
                        {t.category && (
                          <Badge variant="secondary" className="text-xs">{getCategoryLabel(t.category)}</Badge>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {t.completed_at ? formatCalendarDate(t.completed_at) : ""}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </>
      )}

      {/* Create / Edit Task Dialog */}
      <Dialog open={taskDialog} onOpenChange={(open) => !open && setTaskDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingTask ? "Edit Task" : "Create Task"}</DialogTitle>
            <DialogDescription>{editingTask ? "Update task details" : "Add a manual task for this grow"}</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Title</Label>
              <Input value={taskForm.title} onChange={(e) => setTaskForm((p) => ({ ...p, title: e.target.value }))} placeholder="e.g. Check pH levels" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Description</Label>
              <Textarea rows={2} value={taskForm.description} onChange={(e) => setTaskForm((p) => ({ ...p, description: e.target.value }))} placeholder="Optional details..." />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Priority</Label>
                <Select value={taskForm.priority} onValueChange={(v) => setTaskForm((p) => ({ ...p, priority: v || "" }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Category</Label>
                <Select value={taskForm.category} onValueChange={(v) => setTaskForm((p) => ({ ...p, category: v || "" }))}>
                  <SelectTrigger><SelectValue placeholder="Optional" /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                      <SelectItem key={k} value={k}>{v}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Due Date</Label>
                <Input type="date" value={taskForm.due_date} onChange={(e) => setTaskForm((p) => ({ ...p, due_date: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Recurring</Label>
                <Select value={taskForm.recurring} onValueChange={(v) => setTaskForm((p) => ({ ...p, recurring: v || "" }))}>
                  <SelectTrigger><SelectValue placeholder="None" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">None</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="every_2_days">Every 2 Days</SelectItem>
                    <SelectItem value="every_3_days">Every 3 Days</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="biweekly">Biweekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setTaskDialog(false)}>Cancel</Button>
            <Button type="button" onClick={handleTaskSave} disabled={taskSaving || !taskForm.title.trim()}>
              {taskSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editingTask ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function RoutineCard({
  group,
  onCompleteAll,
  onComplete,
  onDelete,
  onSkip,
  onEdit,
}: {
  group: RoutineGroup;
  onCompleteAll: (g: RoutineGroup) => void;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
  onSkip: (id: string) => void;
  onEdit: (task: TaskItem) => void;
}) {
  const [expanded, setExpanded] = useState(true);
  return (
    <Card>
      <CardContent className="p-0">
        <button
          className="flex w-full items-center justify-between px-4 py-3 text-left"
          onClick={() => setExpanded((v) => !v)}
        >
          <div className="flex items-center gap-3">
            {expanded ? <ChevronDown className="size-4 text-muted-foreground" /> : <ChevronRight className="size-4 text-muted-foreground" />}
            <span className="font-semibold">{group.label}</span>
            <Badge variant="secondary">{group.task_count} tasks</Badge>
            {group.estimated_minutes > 0 && (
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Clock className="size-3" />
                ~{group.estimated_minutes} min
              </span>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            className="shrink-0"
            onClick={(e) => { e.stopPropagation(); onCompleteAll(group); }}
          >
            <CheckCircle2 className="mr-1 size-3 text-green-500" />
            Complete all
          </Button>
        </button>
        {expanded && (
          <div className="divide-y border-t">
            {group.tasks.map((t) => (
              <div key={t.id} className="px-4 py-3">
                <GrowTaskCard task={t} onComplete={onComplete} onDelete={onDelete} onSkip={onSkip} onEdit={onEdit} />
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function GrowTaskCard({
  task,
  onComplete,
  onDelete,
  onSkip,
  onEdit,
}: {
  task: TaskItem;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
  onSkip: (id: string) => void;
  onEdit: (task: TaskItem) => void;
}) {
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "completed";

  return (
    <Card className={cn(isOverdue && "border-red-500/50")}>
      <CardContent className="flex items-center justify-between p-4">
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <button
              className="flex size-5 shrink-0 items-center justify-center rounded-full border-2 border-muted-foreground/40 transition hover:border-green-500 hover:bg-green-500/10"
              onClick={() => onComplete(task.id)}
              title="Complete"
            >
              <CheckCircle2 className="size-3 text-transparent hover:text-green-500" />
            </button>
            <h3 className="font-medium">{task.title}</h3>
            <Badge variant={PRIORITY_VARIANT[task.priority] || "outline"} className="text-xs">
              {task.priority}
            </Badge>
            {task.category && (
              <Badge variant="secondary" className="text-xs">{getCategoryLabel(task.category)}</Badge>
            )}
            {task.source === "auto" && (
              <span title="Auto-generated"><Zap className="size-3 text-amber-500" /></span>
            )}
            {task.source === "ai" && (
              <span title="AI-suggested"><Bot className="size-3 text-purple-500" /></span>
            )}
            {task.routine && (
              <Badge variant="outline" className="text-xs border-blue-500/30 text-blue-600 dark:text-blue-400">{getRoutineLabel(task.routine)}</Badge>
            )}
            {task.estimated_minutes && (
              <span className="text-xs text-muted-foreground">~{task.estimated_minutes} min</span>
            )}
          </div>
          {task.description && (
            <p className={cn(
              "text-sm text-muted-foreground whitespace-pre-line",
              task.category === "flush_and_fill" || task.category === "health_response" || task.category === "alert_response" ? "line-clamp-6" : "line-clamp-2",
            )}>{task.description}</p>
          )}
          <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
            {task.due_date && (
              <span className={cn("flex items-center gap-1", isOverdue && "text-red-500 font-medium")}>
                <CalendarIcon className="h-3 w-3" />
                {isOverdue ? "Overdue: " : "Due: "}
                {formatCalendarDate(task.due_date)}
              </span>
            )}
            {task.recurring_interval_days != null ? (
              <span className="flex items-center gap-1">
                <Repeat className="h-3 w-3" />
                {getIntervalLabel(task.recurring_interval_days)}
              </span>
            ) : task.recurring ? (
              <span className="flex items-center gap-1">
                <Repeat className="h-3 w-3" />
                {task.recurring}
              </span>
            ) : null}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="h-8 w-8 p-0" />}>
            <MoreHorizontal className="h-4 w-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(task)}>
              <Pencil className="mr-2 h-4 w-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onComplete(task.id)}>
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Complete
            </DropdownMenuItem>
            {(task.recurring || task.recurring_interval_days) && (
              <DropdownMenuItem onClick={() => onSkip(task.id)}>
                <SkipForward className="mr-2 h-4 w-4" />
                Skip
              </DropdownMenuItem>
            )}
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={() => onDelete(task.id)}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </CardContent>
    </Card>
  );
}
