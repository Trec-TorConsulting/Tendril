"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { createFeedingSchedule } from "@/lib/api";
import { NUTRIENT_BRANDS, type NutrientBrand } from "@/lib/nutrient-brands";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ArrowLeft, ArrowRight, Check, Loader2, FlaskConical } from "lucide-react";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  growCycleId: string;
  onComplete: () => void;
}

export function BrandTemplateDialog({ open, onOpenChange, growCycleId, onComplete }: Props) {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedBrand, setSelectedBrand] = useState<NutrientBrand | null>(null);
  const [selectedProducts, setSelectedProducts] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setStep(1);
    setSelectedBrand(null);
    setSelectedProducts(new Set());
  };

  const handleClose = () => {
    onOpenChange(false);
    reset();
  };

  const handleBrandSelect = (brand: NutrientBrand) => {
    setSelectedBrand(brand);
    // Default: all products selected
    setSelectedProducts(new Set(brand.products.map((p) => p.id)));
    setStep(2);
  };

  const toggleProduct = (productId: string) => {
    setSelectedProducts((prev) => {
      const next = new Set(prev);
      if (next.has(productId)) next.delete(productId);
      else next.add(productId);
      return next;
    });
  };

  // Build preview: filter feed chart to only include selected products
  const preview = selectedBrand
    ? selectedBrand.feedChart.map((phase) => ({
        ...phase,
        products: phase.products.filter((p) => selectedProducts.has(p.productId) && p.ml_per_gallon > 0),
      })).filter((phase) => phase.products.length > 0)
    : [];

  const productNameMap: Record<string, string> = {};
  selectedBrand?.products.forEach((p) => {
    productNameMap[p.id] = p.name;
  });

  const handleApply = async () => {
    const token = getAccessToken();
    if (!token || !selectedBrand) return;
    setSaving(true);
    try {
      for (const phase of preview) {
        const nutrients = phase.products.map((p) => ({
          name: productNameMap[p.productId],
          brand: selectedBrand.name,
          ml_per_gallon: p.ml_per_gallon,
        }));
        await createFeedingSchedule(token, {
          grow_cycle_id: growCycleId,
          name: `${selectedBrand.line} — ${phase.phase} (Wk ${phase.weekRange})`,
          stage: phase.stage,
          nutrients,
          notes: phase.notes,
        });
      }
      handleClose();
      onComplete();
    } catch {
      /* empty */
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && handleClose()}>
      <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
        {/* Step 1: Pick Brand */}
        {step === 1 && (
          <>
            <DialogHeader>
              <DialogTitle>Choose Nutrient Brand</DialogTitle>
              <DialogDescription>
                Select the nutrient line you&apos;re using. We&apos;ll generate a full-cycle feeding schedule from their recommended chart.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-3 sm:grid-cols-2">
              {NUTRIENT_BRANDS.map((brand) => (
                <Card
                  key={brand.id}
                  className="cursor-pointer transition-colors hover:bg-accent"
                  onClick={() => handleBrandSelect(brand)}
                >
                  <CardContent className="p-4">
                    <p className="font-semibold">{brand.name}</p>
                    <p className="text-sm text-muted-foreground">{brand.line}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{brand.description}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {brand.products.filter((p) => p.type === "base").map((p) => (
                        <Badge key={p.id} variant="secondary" className="text-xs">{p.name}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={handleClose}>Cancel</Button>
            </DialogFooter>
          </>
        )}

        {/* Step 2: Select Products */}
        {step === 2 && selectedBrand && (
          <>
            <DialogHeader>
              <DialogTitle>Select Your Products</DialogTitle>
              <DialogDescription>
                Check the {selectedBrand.name} products you own. The feed chart will only include selected products.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">Base Nutrients</p>
                <div className="space-y-2">
                  {selectedBrand.products.filter((p) => p.type === "base").map((p) => (
                    <label key={p.id} className="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                      <input
                        type="checkbox"
                        className="size-4 accent-primary"
                        checked={selectedProducts.has(p.id)}
                        onChange={() => toggleProduct(p.id)}
                      />
                      <span className="text-sm font-medium">{p.name}</span>
                    </label>
                  ))}
                </div>
              </div>
              {selectedBrand.products.some((p) => p.type === "supplement") && (
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">Supplements (optional)</p>
                  <div className="space-y-2">
                    {selectedBrand.products.filter((p) => p.type === "supplement").map((p) => (
                      <label key={p.id} className="flex cursor-pointer items-center gap-3 rounded-md border p-3 transition-colors hover:bg-accent has-[:checked]:border-primary has-[:checked]:bg-primary/5">
                        <input
                          type="checkbox"
                          className="size-4 accent-primary"
                          checked={selectedProducts.has(p.id)}
                          onChange={() => toggleProduct(p.id)}
                        />
                        <span className="text-sm font-medium">{p.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <DialogFooter className="flex-row justify-between sm:justify-between">
              <Button variant="outline" onClick={() => setStep(1)}>
                <ArrowLeft className="mr-1 size-4" />
                Back
              </Button>
              <Button onClick={() => setStep(3)} disabled={selectedProducts.size === 0}>
                Preview
                <ArrowRight className="ml-1 size-4" />
              </Button>
            </DialogFooter>
          </>
        )}

        {/* Step 3: Preview & Confirm */}
        {step === 3 && selectedBrand && (
          <>
            <DialogHeader>
              <DialogTitle>Review Feeding Schedule</DialogTitle>
              <DialogDescription>
                {selectedBrand.name} {selectedBrand.line} — {preview.length} phases will be created covering the full grow cycle.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-2 max-h-[50vh] overflow-y-auto pr-1">
              {preview.map((phase, i) => (
                <Card key={i}>
                  <CardContent className="p-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">{phase.phase}</span>
                      <Badge variant="secondary" className="text-xs capitalize">{phase.stage}</Badge>
                      <span className="text-xs text-muted-foreground">Wk {phase.weekRange}</span>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-0.5">
                      {phase.products.map((p) => (
                        <span key={p.productId} className="text-xs text-muted-foreground">
                          {productNameMap[p.productId]}: <span className="font-medium text-foreground">{p.ml_per_gallon} ml/gal</span>
                        </span>
                      ))}
                    </div>
                    {phase.notes && <p className="mt-1 text-xs text-muted-foreground italic">{phase.notes}</p>}
                  </CardContent>
                </Card>
              ))}
            </div>
            <DialogFooter className="flex-row justify-between sm:justify-between">
              <Button variant="outline" onClick={() => setStep(2)}>
                <ArrowLeft className="mr-1 size-4" />
                Back
              </Button>
              <Button onClick={handleApply} disabled={saving}>
                {saving ? <Loader2 className="mr-2 size-4 animate-spin" /> : <Check className="mr-1 size-4" />}
                {saving ? "Creating..." : `Create ${preview.length} Schedules`}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
