"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  getFeedingAdvice,
  updateGrow,
  listFeedingSchedules,
  createFeedingSchedule,
  updateFeedingSchedule,
  deleteFeedingSchedule,
  listDoseProfiles,
  createDoseProfile,
  updateDoseProfile,
  deleteDoseProfile,
  type BucketResponse,
  type FeedingAdviceResponse,
  type DoseProfileResponse,
} from "@/lib/api";
import { NUTRIENT_BRANDS, STANDALONE_ADDITIVES, type NutrientBrand, type FeedChartPhase, type StandaloneAdditive } from "@/lib/nutrient-brands";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useConfirm } from "@/components/confirm-dialog";
import {
  FlaskConical,
  Sparkles,
  AlertTriangle,
  ArrowRight,
  Heart,
  Loader2,
  Check,
  ChevronRight,
  CalendarDays,
  ArrowLeft,
  RefreshCw,
  Plus,
  Droplets,
  X,
  Pencil,
  Trash2,
  ClipboardList,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const STAGES = ["seedling", "vegetative", "flowering", "ripening", "drying", "curing"];
const STAGE_ORDER: Record<string, number> = Object.fromEntries(STAGES.map((s, i) => [s, i]));

interface FeedingTabProps {
  growId: string;
  growStage: string;
  growStartedAt: string;
  milestones: Record<string, string>;
  settings: Record<string, unknown>;
  buckets: BucketResponse[];
  onRefresh: () => void;
}

/** Determine which feed-chart phase is current based on stage + milestones */
function getCurrentPhaseIndex(
  phases: FeedChartPhase[],
  growStage: string,
  milestones: Record<string, string>,
  startedAt: string,
): number {
  const stagePhases = phases.map((p, i) => ({ ...p, idx: i })).filter((p) => p.stage === growStage);
  if (stagePhases.length === 0) {
    const currentOrder = STAGE_ORDER[growStage] ?? 0;
    for (let i = phases.length - 1; i >= 0; i--) {
      if ((STAGE_ORDER[phases[i].stage] ?? 0) <= currentOrder) return i;
    }
    return 0;
  }
  if (stagePhases.length === 1) return stagePhases[0].idx;

  const milestoneDate = milestones[growStage] || startedAt;
  const stageStart = new Date(milestoneDate);
  const now = new Date();
  const weeksSinceStage = Math.max(0, Math.floor((now.getTime() - stageStart.getTime()) / (7 * 24 * 60 * 60 * 1000)));

  const baseWeek = (() => {
    const br = stagePhases[0].weekRange.replace(/[–—]/g, "-");
    const bp = br.split("-").map((s) => parseInt(s.trim(), 10));
    return (bp[0] || 1) - 1;
  })();

  for (let i = stagePhases.length - 1; i >= 0; i--) {
    const range = stagePhases[i].weekRange.replace(/[–—]/g, "-");
    const parts = range.split("-").map((s) => parseInt(s.trim(), 10));
    const phaseWeekStart = (parts[0] || 1) - 1;
    const relativePhaseStart = phaseWeekStart - baseWeek;
    if (weeksSinceStage >= relativePhaseStart) return stagePhases[i].idx;
  }
  return stagePhases[0].idx;
}

export function FeedingTab({ growId, growStage, growStartedAt, milestones, settings, buckets, onRefresh }: FeedingTabProps) {
  // Brand from grow settings
  const brandId = settings?.nutrient_brand_id as string | undefined;
  const productIds = (settings?.nutrient_product_ids as string[]) || [];
  const additiveIds = (settings?.additive_ids as string[]) || [];

  // Brand dialog state
  const [brandDialog, setBrandDialog] = useState(false);
  const [brandStep, setBrandStep] = useState<1 | 2 | 3>(1);
  const [pendingBrand, setPendingBrand] = useState<NutrientBrand | null>(null);
  const [pendingProducts, setPendingProducts] = useState<Set<string>>(new Set());
  const [pendingAdditives, setPendingAdditives] = useState<Set<string>>(new Set());
  const [brandSaving, setBrandSaving] = useState(false);

  // Additive quick-add dialog
  const [additiveDialog, setAdditiveDialog] = useState(false);
  const [pendingQuickAdditives, setPendingQuickAdditives] = useState<Set<string>>(new Set());
  const [additiveSaving, setAdditiveSaving] = useState(false);

  // AI advice
  const [advice, setAdvice] = useState<FeedingAdviceResponse | null>(null);
  const [adviceLoading, setAdviceLoading] = useState(false);
  const [adviceError, setAdviceError] = useState(false);

  // Custom feeding schedules
  const confirm = useConfirm();
  const [schedules, setSchedules] = useState<{ id: string; name: string; stage: string; nutrients: object[]; target_ppm?: number | null; target_ec?: number | null; notes?: string | null }[]>([]);
  const [scheduleDialog, setScheduleDialog] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<typeof schedules[0] | null>(null);
  const [scheduleForm, setScheduleForm] = useState({ name: "", stage: "vegetative", target_ppm: "", target_ec: "", notes: "" });
  const [scheduleSaving, setScheduleSaving] = useState(false);

  // Dose profiles
  const [doseProfiles, setDoseProfiles] = useState<DoseProfileResponse[]>([]);
  const [doseDialog, setDoseDialog] = useState(false);
  const [editingDose, setEditingDose] = useState<DoseProfileResponse | null>(null);
  const [doseForm, setDoseForm] = useState({ name: "", dose_type: "nutrient", dose_ml: "" });
  const [doseSaving, setDoseSaving] = useState(false);

  // Resolve brand data
  const brand = useMemo(() => NUTRIENT_BRANDS.find((b) => b.id === brandId) || null, [brandId]);

  // Filter phases to selected products only
  const phases = useMemo(() => {
    if (!brand) return [];
    const pids = new Set(productIds);
    if (pids.size === 0) return brand.feedChart;
    return brand.feedChart.map((phase) => ({
      ...phase,
      products: phase.products.filter((p) => pids.has(p.productId)),
    })).filter((phase) => phase.products.length > 0);
  }, [brand, productIds]);

  // Product name lookup
  const productNameMap = useMemo(() => {
    const map: Record<string, string> = {};
    brand?.products.forEach((p) => { map[p.id] = p.name; });
    return map;
  }, [brand]);

  // Selected additives (user-chosen, stored in settings)
  const selectedAdditives = useMemo(
    () => {
      if (additiveIds.length === 0) return [];
      const idSet = new Set(additiveIds);
      return STANDALONE_ADDITIVES.filter((a) => idSet.has(a.id));
    },
    [additiveIds],
  );

  // Current phase
  const currentPhaseIdx = useMemo(
    () => phases.length > 0 ? getCurrentPhaseIndex(phases, growStage, milestones, growStartedAt) : -1,
    [phases, growStage, milestones, growStartedAt],
  );
  const currentPhase = currentPhaseIdx >= 0 ? phases[currentPhaseIdx] : null;
  const nextPhase = currentPhaseIdx >= 0 && currentPhaseIdx < phases.length - 1 ? phases[currentPhaseIdx + 1] : null;

  // Active buckets for dose calculations
  const activeBuckets = useMemo(
    () => buckets.filter((b) => b.volume_gallons && b.status === "active"),
    [buckets],
  );

  // Load AI advice
  const loadAdvice = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setAdviceLoading(true);
    setAdviceError(false);
    try {
      setAdvice(await getFeedingAdvice(token, growId));
    } catch {
      setAdviceError(true);
    } finally {
      setAdviceLoading(false);
    }
  }, [growId]);

  const loadSchedules = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setSchedules(await listFeedingSchedules(token, growId));
    } catch { setSchedules([]); }
  }, [growId]);

  const loadDoseProfiles = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    try {
      setDoseProfiles(await listDoseProfiles(token, growId));
    } catch { setDoseProfiles([]); }
  }, [growId]);

  useEffect(() => {
    if (brand) loadAdvice();
    loadSchedules();
    loadDoseProfiles();
  }, [brand, loadAdvice, loadSchedules, loadDoseProfiles]);

  // --- Custom schedule handlers ---
  const openScheduleCreate = () => {
    setEditingSchedule(null);
    setScheduleForm({ name: "", stage: growStage || "vegetative", target_ppm: "", target_ec: "", notes: "" });
    setScheduleDialog(true);
  };

  const openScheduleEdit = (s: typeof schedules[0]) => {
    setEditingSchedule(s);
    setScheduleForm({
      name: s.name,
      stage: s.stage,
      target_ppm: s.target_ppm != null ? String(s.target_ppm) : "",
      target_ec: s.target_ec != null ? String(s.target_ec) : "",
      notes: s.notes || "",
    });
    setScheduleDialog(true);
  };

  const handleScheduleSave = async () => {
    const token = getAccessToken();
    if (!token || !scheduleForm.name.trim()) return;
    setScheduleSaving(true);
    try {
      if (editingSchedule) {
        await updateFeedingSchedule(token, editingSchedule.id, {
          name: scheduleForm.name.trim(),
          stage: scheduleForm.stage,
          target_ppm: scheduleForm.target_ppm ? parseFloat(scheduleForm.target_ppm) : null,
          target_ec: scheduleForm.target_ec ? parseFloat(scheduleForm.target_ec) : null,
          notes: scheduleForm.notes.trim() || undefined,
        });
      } else {
        await createFeedingSchedule(token, {
          grow_cycle_id: growId,
          name: scheduleForm.name.trim(),
          stage: scheduleForm.stage,
          nutrients: [],
          target_ppm: scheduleForm.target_ppm ? parseFloat(scheduleForm.target_ppm) : undefined,
          target_ec: scheduleForm.target_ec ? parseFloat(scheduleForm.target_ec) : undefined,
          notes: scheduleForm.notes.trim() || undefined,
        });
      }
      setScheduleDialog(false);
      loadSchedules();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save schedule"); } finally { setScheduleSaving(false); }
  };

  const handleScheduleDelete = async (id: string) => {
    if (!await confirm({ title: "Delete Schedule", description: "Remove this feeding schedule?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteFeedingSchedule(token, id);
      loadSchedules();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete schedule"); }
  };

  // --- Dose profile handlers ---
  const openDoseCreate = () => {
    setEditingDose(null);
    setDoseForm({ name: "", dose_type: "nutrient", dose_ml: "" });
    setDoseDialog(true);
  };

  const openDoseEdit = (d: DoseProfileResponse) => {
    setEditingDose(d);
    setDoseForm({ name: d.name, dose_type: d.dose_type, dose_ml: String(d.dose_ml) });
    setDoseDialog(true);
  };

  const handleDoseSave = async () => {
    const token = getAccessToken();
    if (!token || !doseForm.name.trim() || !doseForm.dose_ml) return;
    setDoseSaving(true);
    try {
      if (editingDose) {
        await updateDoseProfile(token, editingDose.id, {
          name: doseForm.name.trim(),
          dose_ml: parseFloat(doseForm.dose_ml),
        });
      } else {
        await createDoseProfile(token, {
          grow_cycle_id: growId,
          name: doseForm.name.trim(),
          dose_type: doseForm.dose_type,
          dose_ml: parseFloat(doseForm.dose_ml),
        });
      }
      setDoseDialog(false);
      loadDoseProfiles();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to save dose profile"); } finally { setDoseSaving(false); }
  };

  const handleDoseDelete = async (id: string) => {
    if (!await confirm({ title: "Delete Dose", description: "Remove this dose profile?", confirmLabel: "Delete", variant: "destructive" })) return;
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteDoseProfile(token, id);
      loadDoseProfiles();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to delete dose"); }
  };

  const handleDoseToggle = async (d: DoseProfileResponse) => {
    const token = getAccessToken();
    if (!token) return;
    try {
      await updateDoseProfile(token, d.id, { enabled: !d.enabled });
      loadDoseProfiles();
    } catch (e) { toast.error(e instanceof Error ? e.message : "Failed to toggle dose"); }
  };

  // --- Brand selection handlers ---
  const openBrandSelector = () => {
    setBrandStep(1);
    setPendingBrand(null);
    setPendingProducts(new Set());
    setPendingAdditives(new Set(additiveIds));
    setBrandDialog(true);
  };

  const handleBrandPick = (b: NutrientBrand) => {
    setPendingBrand(b);
    setPendingProducts(new Set(b.products.map((p) => p.id)));
    setBrandStep(2);
  };

  const togglePendingProduct = (pid: string) => {
    setPendingProducts((prev) => {
      const next = new Set(prev);
      if (next.has(pid)) next.delete(pid); else next.add(pid);
      return next;
    });
  };

  const togglePendingAdditive = (aid: string) => {
    setPendingAdditives((prev) => {
      const next = new Set(prev);
      if (next.has(aid)) next.delete(aid); else next.add(aid);
      return next;
    });
  };

  const saveBrandSelection = async () => {
    const token = getAccessToken();
    if (!token || !pendingBrand) return;
    setBrandSaving(true);
    try {
      await updateGrow(token, growId, {
        settings: {
          ...(settings || {}),
          nutrient_brand_id: pendingBrand.id,
          nutrient_product_ids: Array.from(pendingProducts),
          additive_ids: Array.from(pendingAdditives),
        },
      });
      setBrandDialog(false);
      onRefresh();
    } catch { /* empty */ } finally {
      setBrandSaving(false);
    }
  };

  // --- Additive quick-add handlers ---
  const openAdditiveDialog = () => {
    setPendingQuickAdditives(new Set(additiveIds));
    setAdditiveDialog(true);
  };

  const toggleQuickAdditive = (aid: string) => {
    setPendingQuickAdditives((prev) => {
      const next = new Set(prev);
      if (next.has(aid)) next.delete(aid); else next.add(aid);
      return next;
    });
  };

  const saveAdditives = async () => {
    const token = getAccessToken();
    if (!token) return;
    setAdditiveSaving(true);
    try {
      await updateGrow(token, growId, {
        settings: {
          ...(settings || {}),
          additive_ids: Array.from(pendingQuickAdditives),
        },
      });
      setAdditiveDialog(false);
      onRefresh();
    } catch { /* empty */ } finally {
      setAdditiveSaving(false);
    }
  };

  const removeAdditive = async (aid: string) => {
    const token = getAccessToken();
    if (!token) return;
    const next = additiveIds.filter((id) => id !== aid);
    await updateGrow(token, growId, {
      settings: { ...(settings || {}), additive_ids: next },
    });
    onRefresh();
  };

  // --- Phase helpers ---
  function phaseStatus(idx: number): "past" | "current" | "future" {
    if (idx < currentPhaseIdx) return "past";
    if (idx === currentPhaseIdx) return "current";
    return "future";
  }

  function phaseDate(phase: FeedChartPhase): string | null {
    const ms = milestones[phase.stage];
    if (ms) return new Date(ms).toLocaleDateString(undefined, { month: "short", day: "numeric" });
    return null;
  }

  function renderAdditiveRow(a: StandaloneAdditive, vol: number) {
    return (
      <span key={a.id} className="text-muted-foreground">
        {a.name}: <span className="text-foreground font-medium">{(a.ml_per_gallon * vol).toFixed(1)} ml</span>
      </span>
    );
  }

  function renderDosesPerBucket(phase: FeedChartPhase) {
    if (activeBuckets.length === 0) return null;
    return (
      <div className="mt-3 rounded-md border bg-muted/30 p-2">
        <p className="mb-1 text-xs font-medium text-muted-foreground">Per Bucket</p>
        <div className="space-y-1">
          {activeBuckets.map((b) => (
            <div key={b.id} className="flex flex-wrap items-baseline gap-x-3 text-xs">
              <span className="font-medium min-w-[5rem]">#{b.position} {b.label || "Unnamed"} ({b.volume_gallons}g)</span>
              {phase.products.map((p) => (
                <span key={p.productId} className="text-muted-foreground">
                  {productNameMap[p.productId] || p.productId}: <span className="text-foreground font-medium">{(p.ml_per_gallon * (b.volume_gallons || 0)).toFixed(1)} ml</span>
                </span>
              ))}
              {selectedAdditives.map((a) => renderAdditiveRow(a, b.volume_gallons || 0))}
            </div>
          ))}
        </div>
      </div>
    );
  }

  function renderAdditiveDialog() {
    return (
      <Dialog open={additiveDialog} onOpenChange={(o) => !o && setAdditiveDialog(false)}>
        <DialogContent className="max-w-lg max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Manage Additives</DialogTitle>
            <DialogDescription>
              Select the standalone additives you use alongside your nutrient line. The AI will factor these into dosing recommendations.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            {STANDALONE_ADDITIVES.map((a) => (
              <label key={a.id} className="flex cursor-pointer items-start gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                <input type="checkbox" className="mt-0.5 size-4 accent-primary" checked={pendingQuickAdditives.has(a.id)} onChange={() => toggleQuickAdditive(a.id)} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-medium">{a.name}</span>
                    <span className="text-xs text-muted-foreground">({a.brand})</span>
                    <span className="text-xs text-primary font-medium ml-auto shrink-0">{a.ml_per_gallon} ml/gal</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">{a.description}</p>
                  <p className="text-xs text-muted-foreground/60 mt-0.5 italic">{a.when}</p>
                </div>
              </label>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAdditiveDialog(false)}>Cancel</Button>
            <Button onClick={saveAdditives} disabled={additiveSaving}>
              {additiveSaving ? <Loader2 className="mr-1 size-4 animate-spin" /> : <Check className="mr-1 size-4" />}
              {additiveSaving ? "Saving..." : "Save Additives"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  function renderBrandDialog() {
    return (
      <Dialog open={brandDialog} onOpenChange={(o) => !o && setBrandDialog(false)}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          {brandStep === 1 && (
            <>
              <DialogHeader>
                <DialogTitle>Choose Nutrient Brand</DialogTitle>
                <DialogDescription>
                  Select the nutrient line you are using. Your feeding calendar will be generated from their recommended chart.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-3 sm:grid-cols-2">
                {NUTRIENT_BRANDS.map((b) => (
                  <Card key={b.id} className="cursor-pointer transition-colors hover:bg-accent" onClick={() => handleBrandPick(b)}>
                    <CardContent className="p-4">
                      <p className="font-semibold">{b.name}</p>
                      <p className="text-sm text-muted-foreground">{b.line}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{b.description}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {b.products.filter((p) => p.type === "base").map((p) => (
                          <Badge key={p.id} variant="secondary" className="text-xs">{p.name}</Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setBrandDialog(false)}>Cancel</Button>
              </DialogFooter>
            </>
          )}

          {brandStep === 2 && pendingBrand && (
            <>
              <DialogHeader>
                <DialogTitle>Select Your Products</DialogTitle>
                <DialogDescription>
                  Check the {pendingBrand.name} products you own. The feeding calendar will only include selected products.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">Base Nutrients</p>
                  <div className="space-y-2">
                    {pendingBrand.products.filter((p) => p.type === "base").map((p) => (
                      <label key={p.id} className="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                        <input type="checkbox" className="size-4 accent-primary" checked={pendingProducts.has(p.id)} onChange={() => togglePendingProduct(p.id)} />
                        <span className="text-sm font-medium">{p.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
                {pendingBrand.products.some((p) => p.type === "supplement") && (
                  <div>
                    <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">Supplements (optional)</p>
                    <div className="space-y-2">
                      {pendingBrand.products.filter((p) => p.type === "supplement").map((p) => (
                        <label key={p.id} className="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                          <input type="checkbox" className="size-4 accent-primary" checked={pendingProducts.has(p.id)} onChange={() => togglePendingProduct(p.id)} />
                          <span className="text-sm font-medium">{p.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              <DialogFooter className="flex-row justify-between sm:justify-between">
                <Button variant="outline" onClick={() => setBrandStep(1)}>
                  <ArrowLeft className="mr-1 size-4" /> Back
                </Button>
                <Button onClick={() => setBrandStep(3)} disabled={pendingProducts.size === 0}>
                  Additives <ChevronRight className="ml-1 size-4" />
                </Button>
              </DialogFooter>
            </>
          )}

          {brandStep === 3 && pendingBrand && (
            <>
              <DialogHeader>
                <DialogTitle>Add Standalone Additives</DialogTitle>
                <DialogDescription>
                  Optionally select additives you use alongside {pendingBrand.name}. The AI will factor these into your feeding plan.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-2">
                {STANDALONE_ADDITIVES.map((a) => (
                  <label key={a.id} className="flex cursor-pointer items-start gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                    <input type="checkbox" className="mt-0.5 size-4 accent-primary" checked={pendingAdditives.has(a.id)} onChange={() => togglePendingAdditive(a.id)} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-2">
                        <span className="text-sm font-medium">{a.name}</span>
                        <span className="text-xs text-muted-foreground">({a.brand})</span>
                        <span className="text-xs text-primary font-medium ml-auto shrink-0">{a.ml_per_gallon} ml/gal</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">{a.description}</p>
                    </div>
                  </label>
                ))}
              </div>
              <DialogFooter className="flex-row justify-between sm:justify-between">
                <Button variant="outline" onClick={() => setBrandStep(2)}>
                  <ArrowLeft className="mr-1 size-4" /> Back
                </Button>
                <Button onClick={saveBrandSelection} disabled={brandSaving}>
                  {brandSaving ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Check className="mr-1 size-4" />}
                  {brandSaving ? "Saving..." : "Save & Generate Calendar"}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    );
  }

  // --- No brand selected ---
  if (!brand) {
    return (
      <>
        <Card className="flex flex-col items-center justify-center py-16">
          <FlaskConical className="size-12 text-muted-foreground/40" />
          <p className="mt-4 text-sm font-medium">No Nutrient Brand Selected</p>
          <p className="mt-1 text-xs text-muted-foreground text-center max-w-sm">
            Select your nutrient line to auto-generate a feeding calendar with correct doses for every stage of your grow.
          </p>
          <Button className="mt-4" onClick={openBrandSelector}>
            <FlaskConical className="mr-2 size-4" /> Choose Nutrient Brand
          </Button>
        </Card>
        {renderBrandDialog()}
      </>
    );
  }

  // --- Main render ---
  return (
    <>
      {/* Brand info bar */}
      <div className="mb-4 flex items-center justify-between rounded-lg border bg-card px-4 py-2.5">
        <div className="flex items-center gap-3">
          <FlaskConical className="size-4 text-primary" />
          <div>
            <p className="text-sm font-medium">{brand.name} — {brand.line}</p>
            <p className="text-xs text-muted-foreground">
              {productIds.length > 0
                ? productIds.map((pid) => productNameMap[pid]).filter(Boolean).join(", ")
                : "All products"}
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" className="h-7 text-xs" onClick={openBrandSelector}>
          Change
        </Button>
      </div>

      {/* Additives bar */}
      <div className="mb-4 flex flex-wrap items-center gap-2 rounded-lg border bg-card px-4 py-2.5">
        <Droplets className="size-4 text-muted-foreground shrink-0" />
        <span className="text-xs font-medium text-muted-foreground mr-1">Additives:</span>
        {selectedAdditives.length > 0 ? (
          selectedAdditives.map((a) => (
            <Badge key={a.id} variant="secondary" className="text-xs gap-1 pr-1">
              {a.name} <span className="text-muted-foreground">({a.ml_per_gallon} ml/gal)</span>
              <button
                type="button"
                onClick={() => removeAdditive(a.id)}
                className="ml-0.5 rounded-sm p-0.5 hover:bg-muted-foreground/20"
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))
        ) : (
          <span className="text-xs text-muted-foreground italic">None selected</span>
        )}
        <Button variant="outline" size="sm" className="h-6 text-xs ml-auto" onClick={openAdditiveDialog}>
          <Plus className="mr-1 size-3" /> Add
        </Button>
      </div>

      {/* AI Adjustments */}
      <Card className="mb-4">
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="flex items-center gap-2 text-sm font-medium">
              <Sparkles className="size-4 text-primary" /> AI Adjustments
            </h3>
            <Button variant="outline" size="sm" className="h-7 text-xs" onClick={loadAdvice} disabled={adviceLoading}>
              {adviceLoading ? <Loader2 className="mr-1 size-3 animate-spin" /> : <RefreshCw className="mr-1 size-3" />}
              {adviceLoading ? "Analyzing..." : "Refresh"}
            </Button>
          </div>
          {adviceLoading && <p className="text-xs text-muted-foreground">Loading cached advice...</p>}
          {adviceError && <p className="text-xs text-muted-foreground italic">AI advice will appear after the next health check.</p>}
          {advice && !adviceLoading && (
            <div className="space-y-3">
              {advice.current_stage_advice && <p className="text-sm">{advice.current_stage_advice}</p>}
              {advice.alerts.length > 0 && (
                <div className="space-y-1">
                  {advice.alerts.map((a, i) => (
                    <div key={i} className={`flex items-start gap-2 rounded-md border px-3 py-2 text-xs ${
                      a.severity === "high" ? "border-destructive/40 bg-destructive/10 text-destructive" :
                      a.severity === "medium" ? "border-yellow-500/40 bg-yellow-500/10 text-yellow-700 dark:text-yellow-400" :
                      "border-muted bg-muted/30 text-muted-foreground"
                    }`}>
                      <AlertTriangle className="size-3 mt-0.5 shrink-0" />
                      <span>{a.message}</span>
                    </div>
                  ))}
                </div>
              )}
              {advice.adjustments.length > 0 && (
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">Recommended Adjustments</p>
                  {advice.adjustments.map((adj, i) => (
                    <div key={i} className="rounded-md border bg-background px-3 py-2 text-xs">
                      <span className="font-medium">{adj.schedule_name}</span>: {adj.change}
                      <span className="text-muted-foreground"> — {adj.reason}</span>
                    </div>
                  ))}
                </div>
              )}
              {advice.health_impact && (
                <div className="flex items-start gap-2 text-xs text-muted-foreground">
                  <Heart className="size-3 mt-0.5 shrink-0" />
                  <span>{advice.health_impact}</span>
                </div>
              )}
            </div>
          )}
          {!advice && !adviceLoading && !adviceError && (
            <p className="text-xs text-muted-foreground">AI adjustments are generated after each health check (every 12 hours) and cached until the next one.</p>
          )}
        </CardContent>
      </Card>

      {/* Next Feeding card */}
      {currentPhase && (
        <Card className="mb-4 border-primary/40 ring-1 ring-primary/20">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Sparkles className="size-4 text-primary" />
              Next Feeding — {currentPhase.phase}
              <Badge variant="default" className="capitalize text-xs ml-auto">{currentPhase.stage}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-1.5 sm:grid-cols-2">
              {currentPhase.products.map((p) => (
                <div key={p.productId} className="flex items-baseline justify-between rounded-md bg-muted/40 px-3 py-1.5 text-sm">
                  <span className="font-medium">{productNameMap[p.productId] || p.productId}</span>
                  <span className="text-muted-foreground">{p.ml_per_gallon} <span className="text-xs">ml/gal</span></span>
                </div>
              ))}
              {selectedAdditives.map((a) => (
                <div key={a.id} className="flex items-baseline justify-between rounded-md bg-blue-500/10 px-3 py-1.5 text-sm">
                  <span className="font-medium">{a.name} <span className="text-xs text-muted-foreground">({a.brand})</span></span>
                  <span className="text-muted-foreground">{a.ml_per_gallon} <span className="text-xs">ml/gal</span></span>
                </div>
              ))}
            </div>

            {currentPhase.notes && (
              <p className="mt-2 text-xs text-muted-foreground italic">{currentPhase.notes}</p>
            )}
            {selectedAdditives.length > 0 && (
              <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">
                + {selectedAdditives.map((a) => a.name).join(", ")} added every feeding
              </p>
            )}

            {renderDosesPerBucket(currentPhase)}

            {nextPhase && (
              <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                <ArrowRight className="size-3 shrink-0" />
                <span>Up next: <span className="font-medium capitalize text-foreground">{nextPhase.phase}</span> ({nextPhase.stage}, Wk {nextPhase.weekRange})</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Feeding Calendar */}
      <div className="mb-3 flex items-center gap-2">
        <CalendarDays className="size-4 text-muted-foreground" />
        <h3 className="text-sm font-medium">Feeding Calendar</h3>
        <span className="text-xs text-muted-foreground">({phases.length} phases)</span>
      </div>

      <div className="space-y-2">
        {phases.map((phase, idx) => {
          const status = phaseStatus(idx);
          const date = phaseDate(phase);
          const isCurrent = status === "current";
          return (
            <Card
              key={idx}
              className={
                isCurrent ? "border-primary/40 ring-1 ring-primary/20" :
                status === "past" ? "opacity-60" : undefined
              }
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-1">
                  {status === "past" && <Check className="size-4 text-green-500" />}
                  {isCurrent && <ChevronRight className="size-4 text-primary" />}
                  {status === "future" && <div className="size-4 rounded-full border-2 border-muted-foreground/30" />}
                  <span className="font-medium text-sm">{phase.phase}</span>
                  <Badge variant={isCurrent ? "default" : "secondary"} className="capitalize text-xs">{phase.stage}</Badge>
                  <span className="text-xs text-muted-foreground">Wk {phase.weekRange}</span>
                  {isCurrent && <Badge variant="outline" className="text-xs text-primary border-primary/40 ml-auto">Current</Badge>}
                  {date && !isCurrent && <span className="text-xs text-muted-foreground ml-auto">{date}</span>}
                </div>

                <div className="flex flex-wrap gap-x-4 gap-y-0.5 mt-1">
                  {phase.products.map((p) => (
                    <span key={p.productId} className="text-xs text-muted-foreground">
                      {productNameMap[p.productId] || p.productId}: <span className="font-medium text-foreground">{p.ml_per_gallon} ml/gal</span>
                    </span>
                  ))}
                  {selectedAdditives.map((a) => (
                    <span key={a.id} className="text-xs text-blue-600 dark:text-blue-400">
                      {a.name}: <span className="font-medium">{a.ml_per_gallon} ml/gal</span>
                    </span>
                  ))}
                </div>

                {phase.notes && <p className="mt-1 text-xs text-muted-foreground italic">{phase.notes}</p>}
                {isCurrent && renderDosesPerBucket(phase)}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Custom Feeding Schedules */}
      <div className="mt-6 mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ClipboardList className="size-4 text-muted-foreground" />
          <h3 className="text-sm font-medium">Custom Schedules</h3>
          <span className="text-xs text-muted-foreground">({schedules.length})</span>
        </div>
        <Button variant="outline" size="sm" onClick={openScheduleCreate}>
          <Plus className="mr-1 size-3" /> Add Schedule
        </Button>
      </div>

      {schedules.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <ClipboardList className="size-8 text-muted-foreground/40" />
            <p className="mt-2 text-sm text-muted-foreground">No custom schedules yet</p>
            <p className="text-xs text-muted-foreground">Create custom feeding schedules to track stage-specific nutrient targets</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {schedules.map((s) => (
            <Card key={s.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{s.name}</span>
                    <Badge variant="secondary" className="text-xs capitalize">{s.stage}</Badge>
                  </div>
                  <div className="flex gap-4 mt-1 text-xs text-muted-foreground">
                    {s.target_ppm != null && <span>Target PPM: <strong className="text-foreground">{s.target_ppm}</strong></span>}
                    {s.target_ec != null && <span>Target EC: <strong className="text-foreground">{s.target_ec}</strong></span>}
                  </div>
                  {s.notes && <p className="mt-1 text-xs text-muted-foreground">{s.notes}</p>}
                </div>
                <div className="flex gap-1 shrink-0 ml-2">
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openScheduleEdit(s)}>
                    <Pencil className="size-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => handleScheduleDelete(s.id)}>
                    <Trash2 className="size-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Schedule Create/Edit Dialog */}
      <Dialog open={scheduleDialog} onOpenChange={(o) => !o && setScheduleDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingSchedule ? "Edit Schedule" : "Create Schedule"}</DialogTitle>
            <DialogDescription>Define a custom feeding schedule for a specific growth stage</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Name</Label>
              <Input value={scheduleForm.name} onChange={(e) => setScheduleForm((p) => ({ ...p, name: e.target.value }))} placeholder="e.g. Week 3 Veg Heavy Feed" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Stage</Label>
              <Select value={scheduleForm.stage} onValueChange={(v) => setScheduleForm((p) => ({ ...p, stage: v || "" }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {STAGES.map((s) => <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Target PPM</Label>
                <Input type="number" value={scheduleForm.target_ppm} onChange={(e) => setScheduleForm((p) => ({ ...p, target_ppm: e.target.value }))} placeholder="e.g. 850" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Target EC (mS/cm)</Label>
                <Input type="number" step="0.1" value={scheduleForm.target_ec} onChange={(e) => setScheduleForm((p) => ({ ...p, target_ec: e.target.value }))} placeholder="e.g. 1.4" />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Textarea rows={2} value={scheduleForm.notes} onChange={(e) => setScheduleForm((p) => ({ ...p, notes: e.target.value }))} placeholder="Optional notes about this schedule..." />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setScheduleDialog(false)}>Cancel</Button>
            <Button onClick={handleScheduleSave} disabled={scheduleSaving || !scheduleForm.name.trim()}>
              {scheduleSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editingSchedule ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {renderBrandDialog()}
      {renderAdditiveDialog()}

      {/* ── Dose Profiles ─────────────────────────────────── */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Droplets className="size-4" /> Dose Profiles
            </CardTitle>
            <Button variant="outline" size="sm" className="h-7 text-xs" onClick={openDoseCreate}>
              <Plus className="mr-1 size-3" /> Add Dose
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {doseProfiles.length === 0 ? (
            <p className="text-xs text-muted-foreground">No dose profiles yet. Create one to track nutrient dosing amounts per product.</p>
          ) : (
            <div className="space-y-2">
              {doseProfiles.map((d) => (
                <div key={d.id} className="flex items-center justify-between rounded-lg border p-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className={cn("font-medium text-sm", !d.enabled && "text-muted-foreground line-through")}>{d.name}</span>
                      <Badge variant="secondary" className="text-xs capitalize">{d.dose_type}</Badge>
                      {!d.enabled && <Badge variant="outline" className="text-xs">Disabled</Badge>}
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{d.dose_ml} mL per gallon</p>
                  </div>
                  <div className="flex gap-1 shrink-0 ml-2">
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => handleDoseToggle(d)} title={d.enabled ? "Disable" : "Enable"}>
                      <Check className={cn("size-3", d.enabled ? "text-green-600" : "text-muted-foreground")} />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => openDoseEdit(d)}>
                      <Pencil className="size-3" />
                    </Button>
                    <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-destructive hover:text-destructive" onClick={() => handleDoseDelete(d.id)}>
                      <Trash2 className="size-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dose Profile Create/Edit Dialog */}
      <Dialog open={doseDialog} onOpenChange={(o) => !o && setDoseDialog(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingDose ? "Edit Dose Profile" : "New Dose Profile"}</DialogTitle>
            <DialogDescription>Track a specific nutrient product dosage for this grow</DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label className="text-xs">Product Name</Label>
              <Input value={doseForm.name} onChange={(e) => setDoseForm((p) => ({ ...p, name: e.target.value }))} placeholder="e.g. CalMag, FloraMicro, Big Bloom" />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Type</Label>
              <Select value={doseForm.dose_type} onValueChange={(v) => setDoseForm((p) => ({ ...p, dose_type: v || "" }))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="nutrient">Nutrient</SelectItem>
                  <SelectItem value="supplement">Supplement</SelectItem>
                  <SelectItem value="ph_up">pH Up</SelectItem>
                  <SelectItem value="ph_down">pH Down</SelectItem>
                  <SelectItem value="enzyme">Enzyme</SelectItem>
                  <SelectItem value="beneficial">Beneficial</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Dose (mL per gallon)</Label>
              <Input type="number" step="0.1" min="0" value={doseForm.dose_ml} onChange={(e) => setDoseForm((p) => ({ ...p, dose_ml: e.target.value }))} placeholder="e.g. 5" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDoseDialog(false)}>Cancel</Button>
            <Button onClick={handleDoseSave} disabled={doseSaving || !doseForm.name.trim() || !doseForm.dose_ml}>
              {doseSaving && <Loader2 className="mr-2 size-4 animate-spin" />}
              {editingDose ? "Save" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
