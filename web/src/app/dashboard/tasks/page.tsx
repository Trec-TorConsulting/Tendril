"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { listTasks, createTask, completeTask, deleteTask } from "@/lib/api";
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
import { cn } from "@/lib/utils";
import { Plus, CheckCircle2, Trash2, MoreHorizontal, Repeat, Calendar } from "lucide-react";

interface TaskItem {
  id: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  assigned_to: string | null;
  created_by: string;
  due_date: string | null;
  completed_at: string | null;
  recurring: string | null;
  created_at: string;
}

const PRIORITY_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  low: "secondary",
  medium: "outline",
  high: "default",
  urgent: "destructive",
};

const STATUS_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  pending: "secondary",
  in_progress: "default",
  completed: "outline",
  cancelled: "secondary",
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState<string>("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [dueDate, setDueDate] = useState("");
  const [recurring, setRecurring] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const filters = filter ? { status: filter } : undefined;
      setTasks(await listTasks(token, filters));
    } catch {
      /* tier restricted */
    }
  }, [filter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

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
          due_date: dueDate || undefined,
          recurring: recurring || undefined,
        },
        token,
      );
      setShowCreate(false);
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setRecurring("");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create");
    }
  };

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

  const activeTasks = tasks.filter((t) => t.status !== "completed");
  const completedTasks = tasks.filter((t) => t.status === "completed");

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
        {/* Filters */}
        <div className="flex gap-2">
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
        </div>

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
                      <SelectValue />
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
                  <Label>Recurring</Label>
                  <Select value={recurring || "none"} onValueChange={(v) => setRecurring(!v || v === "none" ? "" : v)}>
                    <SelectTrigger>
                      <SelectValue />
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

        {/* Active tasks */}
        {activeTasks.length === 0 && completedTasks.length === 0 ? (
          <p className="text-muted-foreground">No tasks yet. Commercial plan required.</p>
        ) : (
          <div className="space-y-3">
            {activeTasks.map((t) => (
              <Card key={t.id}>
                <CardContent className="flex items-center justify-between p-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{t.title}</h3>
                      <Badge variant={STATUS_VARIANT[t.status] || "secondary"}>
                        {t.status}
                      </Badge>
                      <Badge variant={PRIORITY_VARIANT[t.priority] || "outline"}>
                        {t.priority}
                      </Badge>
                    </div>
                    {t.description && (
                      <p className="text-sm text-muted-foreground">{t.description}</p>
                    )}
                    <div className="flex gap-3 text-xs text-muted-foreground">
                      {t.due_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Due: {new Date(t.due_date).toLocaleDateString()}
                        </span>
                      )}
                      {t.recurring && (
                        <span className="flex items-center gap-1">
                          <Repeat className="h-3 w-3" />
                          {t.recurring}
                        </span>
                      )}
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="h-8 w-8 p-0" />}>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleComplete(t.id)}>
                        <CheckCircle2 className="mr-2 h-4 w-4" />
                        Complete
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive focus:text-destructive"
                        onClick={() => handleDelete(t.id)}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardContent>
              </Card>
            ))}

            {/* Completed section */}
            {completedTasks.length > 0 && (
              <>
                <h2 className="pt-4 text-sm font-semibold text-muted-foreground">
                  Completed ({completedTasks.length})
                </h2>
                {completedTasks.slice(0, 10).map((t) => (
                  <Card key={t.id} className="opacity-60">
                    <CardContent className="p-3">
                      <h3 className="font-medium text-muted-foreground line-through">
                        {t.title}
                      </h3>
                      <span className="text-xs text-muted-foreground">
                        {t.completed_at
                          ? new Date(t.completed_at).toLocaleDateString()
                          : ""}
                      </span>
                    </CardContent>
                  </Card>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}
