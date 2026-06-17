"use client";

import { useCallback, useMemo, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  adminListGrowTypeProfiles,
  adminGetGrowTypeProfile,
  adminCreateGrowTypeProfile,
  adminDeleteGrowTypeProfile,
  adminListTaskTemplates,
  adminDeleteTaskTemplate,
  adminExportConfig,
  type GrowTypeProfileSummary,
  type GrowTypeProfileFull,
  type TaskTemplateSummary,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import {
  Leaf,
  ListChecks,
  Plus,
  Trash2,
  Download,
  ChevronRight,
  ArrowLeft,
} from "lucide-react";

type Tab = "grow-types" | "task-templates";

export default function AdminConfigPage() {
  const [tab, setTab] = useState<Tab>("grow-types");
  const [selectedProfile, setSelectedProfile] = useState<GrowTypeProfileFull | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const {
    data,
    error: loadError,
    isLoading: loading,
    mutate,
  } = useApiSWR<{
    profiles: GrowTypeProfileSummary[];
    templates: TaskTemplateSummary[];
  }>(["admin", "config", tab], async (token) => {
    if (tab === "grow-types") {
      return {
        profiles: await adminListGrowTypeProfiles(token),
        templates: [],
      };
    }
    return {
      profiles: [],
      templates: await adminListTaskTemplates(token),
    };
  });
  const profiles = data?.profiles ?? [];
  const templates = data?.templates ?? [];
  const error = useMemo(
    () => (loadError ? (loadError instanceof Error ? loadError.message : "Access denied — admin required") : ""),
    [loadError],
  );

  // Create form state
  const [newName, setNewName] = useState("");
  const [newSlug, setNewSlug] = useState("");

  const refresh = useCallback(async () => {
    await mutate();
  }, [mutate]);

  const handleViewProfile = async (slug: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await adminGetGrowTypeProfile(token, slug);
      setSelectedProfile(data);
    } catch {
      toast.error("Failed to load profile details");
    }
  };

  const handleCreateProfile = async () => {
    if (!newName || !newSlug) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminCreateGrowTypeProfile(token, { name: newName, slug: newSlug });
      toast.success(`Created profile: ${newName}`);
      setShowCreateForm(false);
      setNewName("");
      setNewSlug("");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to create profile");
    }
  };

  const handleDeleteProfile = async (slug: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminDeleteGrowTypeProfile(token, slug);
      toast.success("Profile deleted");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to delete");
    }
  };

  const handleDeleteTemplate = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await adminDeleteTaskTemplate(token, id);
      toast.success("Template deleted");
      refresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to delete");
    }
  };

  const handleExport = async (type: string) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const data = await adminExportConfig(token, type);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}-export.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported ${data.count} items`);
    } catch {
      toast.error("Export failed");
    }
  };

  if (error) {
    return (
      <div className="p-6">
        <PageHeader title="Config Management" />
        <Card className="mt-4">
          <CardContent className="p-6 text-destructive">{error}</CardContent>
        </Card>
      </div>
    );
  }

  // Profile detail view
  if (selectedProfile) {
    return (
      <div className="p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={() => setSelectedProfile(null)}>
            <ArrowLeft className="w-4 h-4 mr-1" /> Back
          </Button>
          <h1 className="text-xl font-semibold">{selectedProfile.name}</h1>
          <Badge variant="secondary">{selectedProfile.slug}</Badge>
        </div>

        {selectedProfile.ai_context_prompt && (
          <Card>
            <CardHeader><CardTitle className="text-sm">AI Context Prompt</CardTitle></CardHeader>
            <CardContent><p className="text-sm text-muted-foreground whitespace-pre-wrap">{selectedProfile.ai_context_prompt}</p></CardContent>
          </Card>
        )}

        <Card>
          <CardHeader><CardTitle className="text-sm">Stages ({selectedProfile.stages.length})</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Slug</TableHead>
                  <TableHead>Duration (days)</TableHead>
                  <TableHead>Temp (°F)</TableHead>
                  <TableHead>Humidity (%)</TableHead>
                  <TableHead>Light (hrs)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {selectedProfile.stages.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell>{s.order}</TableCell>
                    <TableCell className="font-medium">{s.name}</TableCell>
                    <TableCell className="text-muted-foreground">{s.slug}</TableCell>
                    <TableCell>{s.duration_days_min}–{s.duration_days_max}</TableCell>
                    <TableCell>{s.environment?.temp_min ?? "–"}–{s.environment?.temp_max ?? "–"}</TableCell>
                    <TableCell>{s.environment?.humidity_min ?? "–"}–{s.environment?.humidity_max ?? "–"}</TableCell>
                    <TableCell>{s.environment?.light_hours ?? "–"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader><CardTitle className="text-sm">Equipment ({selectedProfile.equipment.length})</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-1 text-sm">
                {selectedProfile.equipment.map((e) => (
                  <li key={e.id} className="flex justify-between">
                    <span>{e.item_name}</span>
                    <Badge variant={e.required ? "default" : "secondary"} className="text-xs">
                      {e.category ?? "misc"}
                    </Badge>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-sm">Troubleshooting ({selectedProfile.troubleshooting.length})</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                {selectedProfile.troubleshooting.slice(0, 10).map((t) => (
                  <li key={t.id}>
                    <span className="font-medium">{t.symptom}</span>
                    {t.severity && <Badge variant="outline" className="ml-2 text-xs">{t.severity}</Badge>}
                  </li>
                ))}
                {selectedProfile.troubleshooting.length > 10 && (
                  <li className="text-muted-foreground">+{selectedProfile.troubleshooting.length - 10} more</li>
                )}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <PageHeader title="Config Management" description="Manage grow type configurations, task templates, and system settings" />

      {/* Tab bar */}
      <div className="flex gap-2 border-b pb-2">
        <Button
          variant={tab === "grow-types" ? "default" : "ghost"}
          size="sm"
          onClick={() => setTab("grow-types")}
        >
          <Leaf className="w-4 h-4 mr-1" /> Grow Types
        </Button>
        <Button
          variant={tab === "task-templates" ? "default" : "ghost"}
          size="sm"
          onClick={() => setTab("task-templates")}
        >
          <ListChecks className="w-4 h-4 mr-1" /> Task Templates
        </Button>
      </div>

      {loading ? (
        <div className="space-y-2">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : tab === "grow-types" ? (
        <>
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">{profiles.length} grow type profiles</p>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={() => handleExport("grow-types")}>
                <Download className="w-4 h-4 mr-1" /> Export
              </Button>
              <Button size="sm" onClick={() => setShowCreateForm(true)}>
                <Plus className="w-4 h-4 mr-1" /> New Profile
              </Button>
            </div>
          </div>

          {showCreateForm && (
            <Card>
              <CardContent className="p-4 flex gap-2 items-end">
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground">Name</label>
                  <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Cannabis Indoor" />
                </div>
                <div className="flex-1">
                  <label className="text-xs text-muted-foreground">Slug</label>
                  <Input value={newSlug} onChange={(e) => setNewSlug(e.target.value)} placeholder="cannabis-indoor" />
                </div>
                <Button onClick={handleCreateProfile}>Create</Button>
                <Button variant="ghost" onClick={() => setShowCreateForm(false)}>Cancel</Button>
              </CardContent>
            </Card>
          )}

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Slug</TableHead>
                <TableHead>Sensor Kit</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="w-24">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {profiles.map((p) => (
                <TableRow key={p.id} className="cursor-pointer hover:bg-muted/50" onClick={() => handleViewProfile(p.slug)}>
                  <TableCell className="font-medium">{p.name}</TableCell>
                  <TableCell className="text-muted-foreground">{p.slug}</TableCell>
                  <TableCell>{p.sensor_kit ?? "—"}</TableCell>
                  <TableCell>
                    <Badge variant={p.is_system ? "secondary" : "default"}>
                      {p.is_system ? "System" : "Custom"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                      {!p.is_system && (
                        <Button size="icon" variant="ghost" onClick={() => handleDeleteProfile(p.slug)}>
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      )}
                      <ChevronRight className="w-4 h-4 text-muted-foreground mt-2" />
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      ) : (
        <>
          <div className="flex justify-between items-center">
            <p className="text-sm text-muted-foreground">{templates.length} task templates</p>
            <Button size="sm" variant="outline" onClick={() => handleExport("task-templates")}>
              <Download className="w-4 h-4 mr-1" /> Export
            </Button>
          </div>

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Grow Types</TableHead>
                <TableHead className="w-16">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {templates.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="font-medium">{t.name}</TableCell>
                  <TableCell><Badge variant="outline">{t.category}</Badge></TableCell>
                  <TableCell>
                    <Badge variant={t.priority === "high" || t.priority === "urgent" ? "destructive" : "secondary"}>
                      {t.priority}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {t.frequency_hours > 0 ? `Every ${t.frequency_hours}h` : "One-time"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {t.grow_type_slugs ? t.grow_type_slugs.join(", ") : "All"}
                  </TableCell>
                  <TableCell>
                    {!t.is_system && (
                      <Button size="icon" variant="ghost" onClick={() => handleDeleteTemplate(t.id)}>
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </div>
  );
}
