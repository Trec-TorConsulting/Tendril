"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listTasks,
  completeTask,
  deleteTask,
  type TaskItem,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, formatDate } from "@/lib/utils";
import {
  CheckCircle2,
  Trash2,
  MoreHorizontal,
  Repeat,
  Calendar as CalendarIcon,
  ListChecks,
  Bot,
  Zap,
} from "lucide-react";
import Link from "next/link";

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

export function TasksTab({ growId }: { growId: string }) {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [filter, setFilter] = useState<string>("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const filters: Record<string, string> = { grow_cycle_id: growId };
      if (filter) filters.status = filter;
      setTasks(await listTasks(token, filters));
    } catch { /* empty */ }
  }, [growId, filter]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleComplete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await completeTask(id, token);
    refresh();
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteTask(id, token);
    refresh();
  };

  const activeTasks = tasks.filter((t) => t.status !== "completed" && t.status !== "cancelled");
  const completedTasks = tasks.filter((t) => t.status === "completed");

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        {[
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
        <div className="ml-auto">
          <Button variant="outline" size="sm" render={<Link href="/dashboard/tasks" />}>
            <ListChecks className="mr-1 h-4 w-4" />
            All Tasks
          </Button>
        </div>
      </div>

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
        <GrowTaskCard
          key={t.id}
          task={t}
          onComplete={handleComplete}
          onDelete={handleDelete}
        />
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
                    {t.completed_at ? formatDate(t.completed_at) : ""}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </>
      )}
    </div>
  );
}

function GrowTaskCard({
  task,
  onComplete,
  onDelete,
}: {
  task: TaskItem;
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
              task.category === "flush_and_fill" || task.category === "health_response" || task.category === "alert_response" ? "line-clamp-6" : "line-clamp-2",
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
