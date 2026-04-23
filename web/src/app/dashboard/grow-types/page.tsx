"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listCustomGrowTypes,
  createCustomGrowType,
  deleteCustomGrowType,
  submitGrowTypeForReview,
  listGrowTypes,
  getGrowType,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
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
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Plus, Leaf, ChevronDown, Trash2, Send } from "lucide-react";
import { PageSkeleton } from "@/components/page-skeleton";

interface CustomGrowType {
  id: string;
  slug: string;
  name: string;
  category: string;
  description: string;
  base_type: string | null;
  profile: Record<string, unknown>;
  submitted_for_review: boolean;
  approved: boolean;
}

interface BuiltInType {
  id: string;
  name: string;
  category: string;
  description: string;
}

const CATEGORIES = ["hydroponic", "soilless", "soil", "outdoor", "custom"];

const CATEGORY_VARIANT: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  hydroponic: "default",
  soilless: "secondary",
  soil: "outline",
  outdoor: "default",
  custom: "secondary",
};

export default function GrowTypesPage() {
  const [customTypes, setCustomTypes] = useState<CustomGrowType[]>([]);
  const [builtIn, setBuiltIn] = useState<BuiltInType[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [expandedProfile, setExpandedProfile] = useState<Record<string, unknown> | null>(null);

  // Type-safe profile accessors
  const profilePhRange = expandedProfile?.ph_range as Record<string, number> | undefined;
  const profileEcRanges = expandedProfile?.ec_ranges as Record<string, Record<string, number>> | undefined;
  const profilePrimarySensors = expandedProfile?.primary_sensors as string[] | undefined;
  const profileFeedingApproach = expandedProfile?.feeding_approach as string | undefined;
  const profileTerminology = expandedProfile?.terminology as Record<string, string> | undefined;
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [category, setCategory] = useState("custom");
  const [description, setDescription] = useState("");
  const [baseType, setBaseType] = useState("");
  const [phMin, setPhMin] = useState("5.5");
  const [phMax, setPhMax] = useState("6.5");
  const [feedingApproach, setFeedingApproach] = useState("");
  const [aiContext, setAiContext] = useState("");
  const [error, setError] = useState("");
  const [tab, setTab] = useState("built-in");
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      const built = await listGrowTypes(token);
      setBuiltIn(built);
    } catch {
      /* empty */
    }
    try {
      const custom = await listCustomGrowTypes(token);
      setCustomTypes(custom);
    } catch {
      /* tier restricted */
    } finally { setLoading(false); }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleExpand = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
      setExpandedProfile(null);
      return;
    }
    const token = getAccessToken();
    if (!token) return;
    try {
      const profile = await getGrowType(token, id);
      setExpandedId(id);
      setExpandedProfile(profile);
    } catch {
      /* empty */
    }
  };

  const handleCreate = async () => {
    const token = getAccessToken();
    if (!token || !name || !slug) return;
    setError("");
    try {
      await createCustomGrowType(
        {
          name,
          slug: slug.toLowerCase().replace(/\s+/g, "-"),
          category,
          description,
          base_type: baseType || undefined,
          profile: {
            ph_range: { min: parseFloat(phMin), max: parseFloat(phMax) },
            feeding_approach: feedingApproach,
            ai_prompt_context: aiContext,
          },
        },
        token,
      );
      setDialogOpen(false);
      setName("");
      setSlug("");
      setDescription("");
      setBaseType("");
      setFeedingApproach("");
      setAiContext("");
      setTab("custom");
      refresh();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create");
    }
  };

  const handleDelete = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await deleteCustomGrowType(id, token);
    refresh();
  };

  const handleSubmit = async (id: string) => {
    const token = getAccessToken();
    if (!token) return;
    await submitGrowTypeForReview(id, token);
    refresh();
  };

  const groupedBuiltIn = builtIn.reduce(
    (acc, gt) => {
      const cat = gt.category || "other";
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(gt);
      return acc;
    },
    {} as Record<string, BuiltInType[]>,
  );

  if (loading) return <PageSkeleton rows={4} cards />;

  return (
    <>
      <PageHeader
        title="Grow Types"
        breadcrumbs={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Grow Types" },
        ]}
        actions={
          <Button size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="mr-1 size-4" />
            Custom Grow Type
          </Button>
        }
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">
        <Tabs value={tab} onValueChange={setTab}>
          <TabsList>
            <TabsTrigger value="built-in">Built-in ({builtIn.length})</TabsTrigger>
            <TabsTrigger value="custom">My Custom ({customTypes.length})</TabsTrigger>
          </TabsList>

          {/* Built-in types */}
          <TabsContent value="built-in" className="space-y-6">
            <p className="text-sm text-muted-foreground">
              Tendril supports {builtIn.length} grow methods out of the box. Click any type to see its full sensor profile, pH/EC ranges, and AI coaching context.
            </p>
            {Object.entries(groupedBuiltIn).map(([cat, types]) => (
              <div key={cat}>
                <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  {cat} ({types.length})
                </h2>
                <div className="space-y-2">
                  {types.map((gt) => (
                    <Collapsible
                      key={gt.id}
                      open={expandedId === gt.id}
                      onOpenChange={() => handleExpand(gt.id)}
                    >
                      <CollapsibleTrigger render={<Card className={cn("cursor-pointer transition hover:border-border/80", expandedId === gt.id && "border-primary")} />}>
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <h3 className="font-medium">{gt.name}</h3>
                              <Badge variant={CATEGORY_VARIANT[cat] ?? "secondary"}>
                                {cat}
                              </Badge>
                            </div>
                            <ChevronDown
                              className={cn(
                                "size-4 text-muted-foreground transition-transform",
                                expandedId === gt.id && "rotate-180",
                              )}
                            />
                          </div>
                          {gt.description && (
                            <p className="mt-1 text-sm text-muted-foreground">{gt.description}</p>
                          )}
                        </CardContent>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        {expandedProfile && (
                          <Card className="mt-1 rounded-t-none border-t-0">
                            <CardContent className="space-y-3 p-4">
                              {profilePhRange && (
                                <div>
                                  <span className="text-xs font-semibold text-muted-foreground">pH Range</span>
                                  <p className="text-sm">
                                    {profilePhRange.min} – {profilePhRange.max}
                                  </p>
                                </div>
                              )}
                              {profileEcRanges && (
                                <div>
                                  <span className="text-xs font-semibold text-muted-foreground">EC Ranges</span>
                                  <div className="mt-1 grid grid-cols-3 gap-2 text-sm">
                                    {Object.entries(profileEcRanges).map(([stage, range]) => (
                                      <div key={stage} className="rounded bg-muted px-2 py-1">
                                        <span className="text-muted-foreground">{stage}:</span>{" "}
                                        <span>{range.min}–{range.max}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {profilePrimarySensors && (
                                <div>
                                  <span className="text-xs font-semibold text-muted-foreground">
                                    Primary Sensors
                                  </span>
                                  <div className="mt-1 flex flex-wrap gap-1">
                                    {profilePrimarySensors.map((s) => (
                                      <Badge key={s} variant="secondary">
                                        {s}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                              {profileFeedingApproach && (
                                <div>
                                  <span className="text-xs font-semibold text-muted-foreground">
                                    Feeding Approach
                                  </span>
                                  <p className="text-sm">{profileFeedingApproach}</p>
                                </div>
                              )}
                              {profileTerminology && (
                                <div>
                                  <span className="text-xs font-semibold text-muted-foreground">
                                    Terminology
                                  </span>
                                  <div className="mt-1 grid grid-cols-2 gap-1 text-sm">
                                    {Object.entries(profileTerminology).map(([k, v]) => (
                                      <div key={k}>
                                        <span className="text-muted-foreground">{k}:</span>{" "}
                                        <span>{v}</span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        )}
                      </CollapsibleContent>
                    </Collapsible>
                  ))}
                </div>
              </div>
            ))}
          </TabsContent>

          {/* Custom types */}
          <TabsContent value="custom" className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Build custom grow type profiles based on built-in templates, or start from scratch.
              Pro &amp; Commercial plans only.
            </p>
            {customTypes.length === 0 ? (
              <Card className="flex flex-col items-center justify-center py-16">
                <Leaf className="size-12 text-muted-foreground/50" />
                <h3 className="mt-4 text-lg font-semibold">No custom grow types yet</h3>
                <p className="mt-1 text-sm text-muted-foreground">Create one from a built-in template or from scratch.</p>
                <Button className="mt-4" onClick={() => setDialogOpen(true)}>
                  <Plus className="mr-1 size-4" />
                  Build your first custom type
                </Button>
              </Card>
            ) : (
              <div className="space-y-3">
                {customTypes.map((gt) => (
                  <Card key={gt.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">{gt.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {gt.category} · {gt.slug}
                          {gt.base_type ? ` (based on ${gt.base_type})` : ""}
                        </p>
                        <p className="mt-1 text-xs text-muted-foreground">{gt.description}</p>
                        {gt.submitted_for_review && (
                          <Badge
                            variant={gt.approved ? "default" : "outline"}
                            className="mt-1"
                          >
                            {gt.approved ? "Approved" : "Pending Review"}
                          </Badge>
                        )}
                      </div>
                      <div className="flex gap-2">
                        {!gt.submitted_for_review && (
                          <Button variant="outline" size="sm" onClick={() => handleSubmit(gt.id)}>
                            <Send className="mr-1 size-3" />
                            Submit
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-destructive hover:bg-destructive/10"
                          onClick={() => handleDelete(gt.id)}
                        >
                          <Trash2 className="mr-1 size-3" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>New Custom Grow Type</DialogTitle>
          </DialogHeader>
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Slug (URL-friendly ID)</Label>
              <Input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder="e.g. my-custom-dwc"
              />
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={category} onValueChange={(v) => setCategory(v ?? "")}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Base Template (optional)</Label>
              <Select value={baseType} onValueChange={(v) => setBaseType(v ?? "")}>
                <SelectTrigger>
                  <SelectValue placeholder="None — start from scratch" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None — start from scratch</SelectItem>
                  {builtIn.map((b) => (
                    <SelectItem key={b.id} value={b.id}>
                      {b.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label>pH Min</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={phMin}
                  onChange={(e) => setPhMin(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>pH Max</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={phMax}
                  onChange={(e) => setPhMax(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Feeding Approach</Label>
              <Input
                value={feedingApproach}
                onChange={(e) => setFeedingApproach(e.target.value)}
                placeholder="e.g. liquid nutrients, top dress"
              />
            </div>
            <div className="space-y-2">
              <Label>AI Context (how AI should advise on this type)</Label>
              <Textarea
                value={aiContext}
                onChange={(e) => setAiContext(e.target.value)}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreate}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
