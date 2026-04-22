"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listTasks,
  createTask,
  completeTask,
  deleteTask,
  getCalendarTasks,
  listGrows,
  type TaskItem,
  type GrowResponse,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatDate, formatMonthYear } from "@/lib/utils";
import {
  Plus,
  CheckCircle2,
  Trash2,
  MoreHorizontal,
  Repeat,
  Calendar as CalendarIcon,
  ListChecks,
  ChevronLeft,
  ChevronRight,
  Bot,
  Zap,
} from "lucide-react";

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
};

function getCategoryLabel(cat: string | null) {
  return cat ? CATEGORY_LABELS[cat] || cat.replace(/_/g, " ") : null;
}

// Calendar helpers
function getMonthDays(year: number, month: number) {
  const first = new Date(year, month, 1);
  const last = new Date(year, month + 1, 0);
  const startDay = first.getDay();
  const totalDays = last.getDate();
  return { startDay, totalDays };
}

function fmtMonthYear(year: number, month: number) {
  return formatMonthYear(year, month);
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState<string>("");
  const [growFilter, setGrowFilter] = useState<string>("");
  const [view, setView] = useState<"list" | "calendar">("list");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [category, setCategory] = useState("");
  const [growId, setGrowId] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [recurring, setRecurring] = useState("");
  const [error, setError] = useState("");

  // Calendar state
  const now = new Date();
  const [calYear, setCalYear] = useState(now.getFullYear());
  const [calMonth, setCalMonth] = useState(now.getMonth());
  const [calTasks, setCalTasks] = useState<TaskItem[]>([]);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const filters: Record<string, string> = {};
      if (filter) filters.status = filter;
      if (growFilter) filters.grow_cycle_id = growFilter;
      const [t, g] = await Promise.all([listTasks(token, filters), listGrows(token)]);
      setTasks(t);
      setGrows(g);
    } catch {
      /* empty */
    }
  }, [filter, growFilter]);

  const refreshCalendar = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    const start = new Date(calYear, calMonth, 1).toISOString();
    const end = new Date(calYear, calMonth + 1, 0, 23, 59, 59).toISOString();
    try {
      setCalTasks(await getCalendarTasks(token, start, end));
    } catch {
      /* empty */
    }
  }, [calYear, calMonth]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (view === "calendar") refreshCalendar();
  }, [view, refreshCalendar]);

  const handleCreate = async () => {
    const token = getAccessToken();
    if (!token || !title) return;
    setError("");
    try {
      await createTask(
        {
          title,
          description: description || undefined,
          priority,
          category: category || undefined,
          grow_cycle_id: growId || undefined,
          due_date: dueDate || undefined,
          recurring: recurring || undefined,
        },
        token,
      );
      setShowCreate(false);
      setTitle("");
      setDescription("");
      setPriority("medium");
      setCategory("");
      setGrowId("");
      setDueDate("");
      setRecurring("");
      refresh();
      if (view === "calendar") refreshCalendar();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create");
    }
  };

  const handleComplete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await completeTask(id, token);
    refresh();
    if (view === "calendar") refreshCalendar();
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteTask(id, token);
    refresh();
    if (view === "calendar") refreshCalendar();
  };

  const activeTasks = tasks.filter((t) => t.status !== "completed" && t.status !== "cancelled");
  const completedTasks = tasks.filter((t) => t.status === "completed");

  // Build calendar grid
  const { startDay, totalDays } = getMonthDays(calYear, calMonth);
  const tasksByDay = useMemo(() => {
    const map: Record<number, TaskItem[]> = {};
    for (const t of calTasks) {
      if (!t.due_date) continue;
      const d = new Date(t.due_date).getDate();
      (map[d] ||= []).push(t);
    }
    return map;
  }, [calTasks]);

  const growMap = Object.fromEntries(grows.map((g) => [g.id, g.name]));

  return (
    <>
      <PageHeader
        title="Tasks"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Tasks" },
        ]}
        actions={
          <Button onClick={() => setShowCreate(true)} size="sm">
            <Plus className="mr-1 h-4 w-4" />
            New Task
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* View toggle + filters */}
        <div className="flex flex-wrap items-center gap-2">
          <Button
            variant={view === "list" ? "default" : "outline"}
            size="sm"
            onClick={() => setView("list")}
          >
            <ListChecks className="mr-1 h-4 w-4" />
            List
          </Button>
          <Button
            variant={view === "calendar" ? "default" : "outline"}
            size="sm"
            onClick={() => setView("calendar")}
          >
            <CalendarIcon className="mr-1 h-4 w-4" />
            Calendar
          </Button>

          <div className="ml-auto" />

          {/* Grow filter */}
          {grows.length > 0 && (
            <Select value={growFilter || "all"} onValueChange={(v) => setGrowFilter(!v || v === "all" ? "" : v)}>
              <SelectTrigger className="h-8 w-[180px]">
                <SelectValue>{growFilter ? grows.find((g) => g.id === growFilter)?.name ?? "Grow" : "All Grows"}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Grows</SelectItem>
                {grows.filter((g) => g.status === "active").map((g) => (
                  <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          {view === "list" &&
            [
              { value: "", label: "All" },
              { value: "pending", label: "Pending" },
              { value: "in_progress", label: "In Progress" },
              { value: "completed", label: "Completed" },
            ].map((s) => (
              <Button
                key={s.value}
                variant={filter === s.value ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(s.value)}
              >
                {s.label}
              </Button>
            ))}
        </div>

        {/* ─── List View ──────────────────────────────── */}
        {view === "list" && (
          <div className="space-y-3">
            {activeTasks.length === 0 && completedTasks.length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <ListChecks className="size-10 text-muted-foreground/50" />
                  <p className="mt-3 text-muted-foreground">No tasks yet. Auto-generated tasks will appear when you have active grows.</p>
                </CardContent>
              </Card>
            )}

            {activeTasks.map((t) => (
              <TaskCard
                key={t.id}
                task={t}
                growName={t.grow_cycle_id ? growMap[t.grow_cycle_id] : undefined}
                onComplete={handleComplete}
                onDelete={handleDelete}
              />
            ))}

            {completedTasks.length > 0 && (
              <>
                <h2 className="pt-4 text-sm font-semibold text-muted-foreground">
                  Completed ({completedTasks.length})
                </h2>
                {completedTasks.slice(0, 15).map((t) => (
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
                          {t.completed_at ? formatDate(t.completed_at) : ""}
                          {t.grow_cycle_id && growMap[t.grow_cycle_id] ? ` — ${growMap[t.grow_cycle_id]}` : ""}
                        </span>
                      </div>
                      <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-muted-foreground" onClick={() => handleDelete(t.id)}>
                        <Trash2 className="size-3" />
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </>
            )}
          </div>
        )}

        {/* ─── Calendar View ──────────────────────────── */}
        {view === "calendar" && (
          <div>
            <div className="mb-4 flex items-center justify-between">
              <Button variant="outline" size="sm" onClick={() => {
                if (calMonth === 0) { setCalMonth(11); setCalYear(calYear - 1); }
                else setCalMonth(calMonth - 1);
              }}>
                <ChevronLeft className="size-4" />
              </Button>
              <h2 className="text-lg font-semibold">{fmtMonthYear(calYear, calMonth)}</h2>
              <Button variant="outline" size="sm" onClick={() => {
                if (calMonth === 11) { setCalMonth(0); setCalYear(calYear + 1); }
                else setCalMonth(calMonth + 1);
              }}>
                <ChevronRight className="size-4" />
              </Button>
            </div>

            {/* Day headers */}
            <div className="grid grid-cols-7 gap-px text-center text-xs font-medium text-muted-foreground">
              {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
                <div key={d} className="py-2">{d}</div>
              ))}
            </div>

            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-px">
              {/* Empty slots before first day */}
              {Array.from({ length: startDay }).map((_, i) => (
                <div key={`empty-${i}`} className="min-h-[80px] rounded-md bg-muted/30 p-1" />
              ))}

              {/* Day cells */}
              {Array.from({ length: totalDays }).map((_, i) => {
                const day = i + 1;
                const dayTasks = tasksByDay[day] || [];
                const isToday = day === now.getDate() && calMonth === now.getMonth() && calYear === now.getFullYear();
                return (
                  <div
                    key={day}
                    className={cn(
                      "min-h-[80px] rounded-md border p-1",
                      isToday && "border-primary bg-primary/5",
                    )}
                  >
                    <div className={cn("text-xs font-medium", isToday && "text-primary")}>{day}</div>
                    <div className="mt-0.5 space-y-0.5">
                      {dayTasks.slice(0, 3).map((t) => (
                        <div
                          key={t.id}
                          className={cn(
                            "truncate rounded px-1 text-[10px] leading-tight",
                            t.status === "completed" ? "bg-green-500/20 text-green-700 line-through" :
                            t.priority === "urgent" ? "bg-red-500/20 text-red-700" :
                            t.priority === "high" ? "bg-orange-500/20 text-orange-700" :
                            "bg-blue-500/20 text-blue-700",
                          )}
                          title={t.title}
                        >
                          {t.title}
                        </div>
                      ))}
                      {dayTasks.length > 3 && (
                        <div className="text-[10px] text-muted-foreground">+{dayTasks.length - 3} more</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Create dialog */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Task</DialogTitle>
            </DialogHeader>
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="task-title">Title</Label>
                <Input
                  id="task-title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="task-desc">Description</Label>
                <Textarea
                  id="task-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>Priority</Label>
                  <Select value={priority} onValueChange={(v) => setPriority(v ?? "medium")}>
                    <SelectTrigger>
                      <SelectValue>{priority}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={category || "none"} onValueChange={(v) => setCategory(!v || v === "none" ? "" : v)}>
                    <SelectTrigger>
                      <SelectValue>{category ? getCategoryLabel(category) : "None"}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      <SelectItem value="ph_check">pH Check</SelectItem>
                      <SelectItem value="ec_check">EC Check</SelectItem>
                      <SelectItem value="flush_and_fill">Flush & Fill</SelectItem>
                      <SelectItem value="water_change">Water Change</SelectItem>
                      <SelectItem value="watering">Watering</SelectItem>
                      <SelectItem value="feeding">Feeding</SelectItem>
                      <SelectItem value="health_check">Health Check</SelectItem>
                      <SelectItem value="pest_check">Pest Check</SelectItem>
                      <SelectItem value="defoliation">Defoliation</SelectItem>
                      <SelectItem value="trichome_check">Trichome Check</SelectItem>
                      <SelectItem value="flush">Flush</SelectItem>
                      <SelectItem value="harvest">Harvest</SelectItem>
                      <SelectItem value="root_check">Root Check</SelectItem>
                      <SelectItem value="water_level">Water Level</SelectItem>
                      <SelectItem value="nozzle_check">Nozzle Check</SelectItem>
                      <SelectItem value="circulation_check">Circulation</SelectItem>
                      <SelectItem value="algae_check">Algae Check</SelectItem>
                      <SelectItem value="weather_check">Weather Check</SelectItem>
                      <SelectItem value="soil_amendment">Soil Amendment</SelectItem>
                      <SelectItem value="runoff_check">Runoff Check</SelectItem>
                      <SelectItem value="dryback_check">Dry-back</SelectItem>
                      <SelectItem value="calmag">CalMag</SelectItem>
                      <SelectItem value="top_dress">Top Dress</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>Grow</Label>
                  <Select value={growId || "none"} onValueChange={(v) => setGrowId(!v || v === "none" ? "" : v)}>
                    <SelectTrigger>
                      <SelectValue>{growId ? growMap[growId] ?? "Select" : "None"}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      {grows.filter((g) => g.status === "active").map((g) => (
                        <SelectItem key={g.id} value={g.id}>{g.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Recurring</Label>
                  <Select value={recurring || "none"} onValueChange={(v) => setRecurring(!v || v === "none" ? "" : v)}>
                    <SelectTrigger>
                      <SelectValue>{recurring || "None"}</SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="biweekly">Biweekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="task-due">Due Date</Label>
                <Input
                  id="task-due"
                  type="datetime-local"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </>
  );
}

function TaskCard({
  task,
  growName,
  onComplete,
  onDelete,
}: {
  task: TaskItem;
  growName?: string;
  onComplete: (id: string) => void;
  onDelete: (id: string) => void;
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
          </div>
          {task.description && (
            <p className={cn(
              "text-sm text-muted-foreground whitespace-pre-line",
              task.category === "flush_and_fill" || task.category === "health_response" || task.category === "alert_response" ? "line-clamp-6" : "line-clamp-1",
            )}>{task.description}</p>
          )}
          <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
            {task.due_date && (
              <span className={cn("flex items-center gap-1", isOverdue && "text-red-500 font-medium")}>
                <CalendarIcon className="h-3 w-3" />
                {isOverdue ? "Overdue: " : "Due: "}
                {formatDate(task.due_date)}
              </span>
            )}
            {task.recurring && (
              <span className="flex items-center gap-1">
                <Repeat className="h-3 w-3" />
                {task.recurring}
              </span>
            )}
            {growName && <span>Grow: {growName}</span>}
          </div>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="h-8 w-8 p-0" />}>
            <MoreHorizontal className="h-4 w-4" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onComplete(task.id)}>
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Complete
            </DropdownMenuItem>
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
