"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { z } from "zod";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { getAccessToken } from "@/lib/auth";
import { useConfirm } from "@/components/confirm-dialog";
import { formatCalendarDate } from "@/lib/utils";
import {
  listGrows,
  listTents,
  createGrow,
  deleteGrow,
  listGrowTypes,
  type GrowResponse,
  type TentResponse,
  type GrowTypeSummary,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import { Plus, Sprout, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { PullToRefresh } from "@/components/pull-to-refresh";
import { PageSkeleton } from "@/components/page-skeleton";

const createGrowSchema = z.object({
  name: z.string().min(1, "Name is required"),
  tent_id: z.string().min(1, "Grow space is required"),
  grow_type: z.string().min(1, "Grow type is required"),
});
type CreateGrowForm = z.infer<typeof createGrowSchema>;

export default function GrowsPage() {
  const router = useRouter();
  const confirm = useConfirm();
  const [grows, setGrows] = useState<GrowResponse[]>([]);
  const [tents, setTents] = useState<TentResponse[]>([]);
  const [growTypes, setGrowTypes] = useState<GrowTypeSummary[]>([]);
  const [filter, setFilter] = useState<string>("active");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [error, setError] = useState("");

  const { register, handleSubmit, control, reset, formState: { errors, isSubmitting } } = useForm<CreateGrowForm>({
    resolver: zodResolver(createGrowSchema),
    defaultValues: { name: "", tent_id: "", grow_type: "" },
  });

  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [g, t, gt] = await Promise.all([
        listGrows(token, filter !== "all" ? { status: filter } : undefined),
        listTents(token),
        listGrowTypes(token),
      ]);
      setGrows(g);
      setTents(t);
      setGrowTypes(gt);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to load grows");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreate = async (data: CreateGrowForm) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await createGrow(token, {
        tent_id: data.tent_id,
        name: data.name,
        grow_type: data.grow_type,
      });
      toast.success("Grow created");
      setDialogOpen(false);
      reset();
      refresh();
    } catch {
      setError("Failed to create grow");
    }
  };

  const handleDelete = async (id: string) => {
    if (!await confirm({ title: "Delete Grow", description: "Delete this grow cycle? All associated tasks, buckets, and data will be removed.", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteGrow(token, id);
      toast.success("Grow deleted");
      refresh();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Failed to delete grow");
    }
  };

  const tentName = (id: string) => tents.find((t) => t.id === id)?.name ?? "—";

  const statusVariant = (status: string) => {
    if (status === "active") return "default" as const;
    if (status === "completed") return "secondary" as const;
    return "outline" as const;
  };

  return (
    <>
      <PageHeader
        title="Grows"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Grows" }]}
        actions={
          <Button size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="mr-1 size-4" />
            New Grow
          </Button>
        }
      />
      <PullToRefresh onRefresh={refresh}>
      <div className="flex flex-1 flex-col gap-4 p-4 lg:p-6">
        <Tabs value={filter} onValueChange={setFilter}>
          <TabsList>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="archived">Archived</TabsTrigger>
            <TabsTrigger value="all">All</TabsTrigger>
          </TabsList>
        </Tabs>

        {loading ? (
          <PageSkeleton rows={3} cards />
        ) : grows.length === 0 ? (
          <Card className="flex flex-col items-center justify-center py-16">
            <Sprout className="size-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No grows found</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Start a new grow cycle to track your progress.
            </p>
            <Button className="mt-4" onClick={() => setDialogOpen(true)}>
              <Plus className="mr-1 size-4" />
              New Grow
            </Button>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {grows.map((g) => (
              <motion.div key={g.id} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
              <Card className="p-4 transition-colors hover:border-primary/50 cursor-pointer" onClick={() => router.push(`/dashboard/grows/${g.id}`)}>
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <Link
                      href={`/dashboard/grows/${g.id}`}
                      className="font-semibold hover:text-primary"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {g.name}
                    </Link>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {tentName(g.tent_id)} · {g.grow_type}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Stage: {g.stage} · Started{" "}
                      {formatCalendarDate(g.started_at)}
                    </p>
                  </div>
                  <Badge variant={statusVariant(g.status)} className="ml-2 shrink-0">
                    {g.status}
                  </Badge>
                </div>
                <div className="mt-3 flex items-center justify-end">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 text-muted-foreground hover:text-destructive"
                    onClick={(e) => { e.stopPropagation(); handleDelete(g.id); }}
                  >
                    <Trash2 className="size-4" />
                  </Button>
                </div>
              </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
      </PullToRefresh>

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) { reset(); setError(""); } }}>
        <DialogContent>
          <form onSubmit={handleSubmit(handleCreate)}>
          <DialogHeader>
            <DialogTitle>New Grow Cycle</DialogTitle>
            <DialogDescription>Start tracking a new grow from seed to harvest.</DialogDescription>
          </DialogHeader>
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                placeholder="Grow name"
                {...register("name")}
              />
              {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Grow Space</Label>
              <Controller name="tent_id" control={control} render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select space" />
                  </SelectTrigger>
                  <SelectContent>
                    {tents.map((t) => (
                      <SelectItem key={t.id} value={t.id}>
                        {t.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )} />
              {errors.tent_id && <p className="text-xs text-destructive">{errors.tent_id.message}</p>}
            </div>
            <div className="space-y-2">
              <Label>Grow Type</Label>
              <Controller name="grow_type" control={control} render={({ field }) => (
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    {growTypes.map((gt) => (
                      <SelectItem key={gt.id} value={gt.id}>
                        {gt.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )} />
              {errors.grow_type && <p className="text-xs text-destructive">{errors.grow_type.message}</p>}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>Create</Button>
          </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </>
  );
}
