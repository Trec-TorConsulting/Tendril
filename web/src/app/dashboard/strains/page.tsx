"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { PageSkeleton } from "@/components/page-skeleton";
import { useConfirm } from "@/components/confirm-dialog";
import {
  listStrains,
  createStrain,
  deleteStrain,
  getStrainLeaderboard,
  getStrainComparison,
  type StrainResponse,
  type StrainGrowComparison,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { Plus, Trash2, Trophy, Library, MoreHorizontal, BarChart3 } from "lucide-react";

export default function StrainsPage() {
  const [strains, setStrains] = useState<StrainResponse[]>([]);
  const [leaderboard, setLeaderboard] = useState<
    { strain_name: string; harvests: number; avg_dry_weight_g: number | null; avg_quality: number | null }[]
  >([]);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", breeder: "", genetics: "" });
  const [tab, setTab] = useState<"library" | "leaderboard" | "comparison">("library");
  const confirm = useConfirm();
  const [loading, setLoading] = useState(true);
  const [comparisonStrainId, setComparisonStrainId] = useState("");
  const [comparison, setComparison] = useState<StrainGrowComparison[]>([]);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const [s, lb] = await Promise.all([listStrains(token), getStrainLeaderboard(token)]);
      setStrains(s);
      setLeaderboard(lb);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreate = async () => {
    const token = getAccessToken();
    if (!token || !form.name) return;
    await createStrain(token, {
      name: form.name,
      breeder: form.breeder || undefined,
      genetics: form.genetics || undefined,
    });
    setShowCreate(false);
    setForm({ name: "", breeder: "", genetics: "" });
    refresh();
  };

  const handleDelete = async (id: string) => {
    if (!await confirm({ title: "Delete Strain", description: "Delete this strain?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    await deleteStrain(token, id);
    refresh();
  };

  if (loading) return <PageSkeleton rows={4} cards />;

  return (
    <>
      <PageHeader
        title="Strains"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Strains" },
        ]}
        actions={
          <Button onClick={() => setShowCreate(true)} size="sm">
            <Plus className="mr-1 h-4 w-4" />
            Add Strain
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        {/* Tabs */}
        <div className="flex gap-2">
          <Button
            variant={tab === "library" ? "default" : "outline"}
            size="sm"
            onClick={() => setTab("library")}
          >
            <Library className="mr-1 h-4 w-4" />
            Library
          </Button>
          <Button
            variant={tab === "leaderboard" ? "default" : "outline"}
            size="sm"
            onClick={() => setTab("leaderboard")}
          >
            <Trophy className="mr-1 h-4 w-4" />
            Leaderboard
          </Button>
          <Button
            variant={tab === "comparison" ? "default" : "outline"}
            size="sm"
            onClick={() => setTab("comparison")}
          >
            <BarChart3 className="mr-1 h-4 w-4" />
            Comparison
          </Button>
        </div>

        {tab === "library" && (
          <>
            {strains.length === 0 ? (
              <Card className="flex flex-col items-center justify-center py-16">
                <Library className="size-12 text-muted-foreground/50" />
                <h3 className="mt-4 text-lg font-semibold">No strains yet</h3>
                <p className="mt-1 text-sm text-muted-foreground">Add your first strain to start tracking genetics.</p>
                <Button className="mt-4" size="sm" onClick={() => setShowCreate(true)}>
                  <Plus className="mr-1 h-4 w-4" /> Add Strain
                </Button>
              </Card>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {strains.map((s) => (
                  <Card key={s.id}>
                    <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                      <CardTitle className="text-lg">{s.name}</CardTitle>
                      <DropdownMenu>
                        <DropdownMenuTrigger render={<Button variant="ghost" size="sm" className="h-8 w-8 p-0" />}>
                          <MoreHorizontal className="h-4 w-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() => handleDelete(s.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </CardHeader>
                    <CardContent>
                      {s.breeder && (
                        <p className="text-sm text-muted-foreground">Breeder: {s.breeder}</p>
                      )}
                      {s.genetics && (
                        <p className="text-sm text-muted-foreground">Genetics: {s.genetics}</p>
                      )}
                      <div className="mt-3 flex flex-wrap gap-2">
                        {s.flowering_days && (
                          <Badge variant="secondary">{s.flowering_days}d flower</Badge>
                        )}
                        {s.thc_pct != null && (
                          <Badge variant="secondary">THC {s.thc_pct}%</Badge>
                        )}
                        {s.cbd_pct != null && (
                          <Badge variant="secondary">CBD {s.cbd_pct}%</Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </>
        )}

        {tab === "leaderboard" && (
          <>
            {leaderboard.length === 0 ? (
              <Card className="flex flex-col items-center justify-center py-16">
                <Trophy className="size-12 text-muted-foreground/50" />
                <h3 className="mt-4 text-lg font-semibold">No harvest data yet</h3>
                <p className="mt-1 text-sm text-muted-foreground">Complete grows to see strain rankings.</p>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-16">Rank</TableHead>
                        <TableHead>Strain</TableHead>
                        <TableHead>Harvests</TableHead>
                        <TableHead>Avg Dry (g)</TableHead>
                        <TableHead>Avg Quality</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {leaderboard.map((row, i) => (
                        <TableRow key={row.strain_name}>
                          <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                          <TableCell className="font-medium">{row.strain_name}</TableCell>
                          <TableCell>{row.harvests}</TableCell>
                          <TableCell>{row.avg_dry_weight_g ?? "—"}</TableCell>
                          <TableCell>{row.avg_quality ?? "—"}/10</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {tab === "comparison" && (
          <div className="space-y-4">
            <div className="max-w-xs">
              <Label className="mb-1 text-sm">Select a strain to compare across grows</Label>
              <Select
                value={comparisonStrainId}
                onValueChange={async (v) => {
                  const id = v ?? "";
                  setComparisonStrainId(id);
                  if (!id) { setComparison([]); return; }
                  const token = getAccessToken();
                  if (!token) return;
                  const data = await getStrainComparison(token, id);
                  setComparison(data);
                }}
              >
                <SelectTrigger>
                  <SelectValue>
                    {comparisonStrainId
                      ? strains.find((s) => s.id === comparisonStrainId)?.name ?? "Select strain"
                      : "Select strain"}
                  </SelectValue>
                </SelectTrigger>
                <SelectContent>
                  {strains.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {comparison.length > 0 && (
              <Card>
                <CardContent className="p-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Grow</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Buckets</TableHead>
                        <TableHead>Avg Dry (g)</TableHead>
                        <TableHead>Total Dry (g)</TableHead>
                        <TableHead>Avg Quality</TableHead>
                        <TableHead>Duration (d)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {comparison.map((row) => (
                        <TableRow key={row.grow_id}>
                          <TableCell className="font-medium">{row.grow_name}</TableCell>
                          <TableCell>{row.grow_type}</TableCell>
                          <TableCell>{row.bucket_count}</TableCell>
                          <TableCell>{row.avg_dry_weight_g ?? "—"}</TableCell>
                          <TableCell>{row.total_dry_weight_g ?? "—"}</TableCell>
                          <TableCell>{row.avg_quality ? `${row.avg_quality}/10` : "—"}</TableCell>
                          <TableCell>{row.grow_duration_days ?? "—"}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            )}
            {comparisonStrainId && comparison.length === 0 && (
              <p className="text-muted-foreground">No grows found with this strain.</p>
            )}
          </div>
        )}

        {/* Create dialog */}
        <Dialog open={showCreate} onOpenChange={setShowCreate}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Strain</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="strain-name">Strain name *</Label>
                <Input
                  id="strain-name"
                  placeholder="Strain name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="strain-breeder">Breeder</Label>
                <Input
                  id="strain-breeder"
                  placeholder="Breeder"
                  value={form.breeder}
                  onChange={(e) => setForm({ ...form, breeder: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="strain-genetics">Genetics</Label>
                <Input
                  id="strain-genetics"
                  placeholder="Genetics"
                  value={form.genetics}
                  onChange={(e) => setForm({ ...form, genetics: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate}>Save</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </>
  );
}
