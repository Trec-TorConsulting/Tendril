"use client";

import { useState } from "react";
import { ReferenceStrainSearch, NutrientSearch } from "@/components/reference-search";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dna, FlaskConical, Search } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import type { ReferenceStrainResult } from "@/lib/api";

type StrainResult = ReferenceStrainResult;

const STRAIN_DATA_CAVEAT =
  "Cannabinoid, terpene, flowering-time and yield figures are typical ranges aggregated from public strain " +
  "databases and breeder listings. Actual results vary by phenotype, cultivation, and testing lab.";

function fmtRange(min: number | null | undefined, max: number | null | undefined, unit: string): string | null {
  if (min == null && max == null) return null;
  if (min != null && max != null && min !== max) return `${min}-${max}${unit}`;
  return `${min ?? max}${unit}`;
}

interface NutrientResult {
  id: string;
  barcode: string;
  name: string;
  brand: string | null;
  npk: string | null;
  nutrients: Record<string, unknown> | null;
}

export default function ReferencePage() {
  const [strainResults, setStrainResults] = useState<StrainResult[]>([]);
  const [nutrientResults, setNutrientResults] = useState<NutrientResult[]>([]);

  return (
    <>
      <PageHeader
        title="Reference Database"
        breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Reference" }]}
      />
      <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">

      <Tabs defaultValue="strains">
        <TabsList>
          <TabsTrigger value="strains" className="gap-1.5">
            <Dna className="size-4" /> Strains
          </TabsTrigger>
          <TabsTrigger value="nutrients" className="gap-1.5">
            <FlaskConical className="size-4" /> Nutrients
          </TabsTrigger>
        </TabsList>

        <TabsContent value="strains" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="size-4" /> Strain Search
              </CardTitle>
              <CardDescription>
                Search by name, breeder, or genetics across the global strain library
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ReferenceStrainSearch
                placeholder="Search strains (e.g. Blue Dream, OG Kush)..."
                onSelect={(s) => {
                  setStrainResults((prev) => {
                    if (prev.some((r) => r.id === s.id)) return prev;
                    return [s, ...prev];
                  });
                }}
              />
            </CardContent>
          </Card>

          {strainResults.length > 0 && (
            <div className="space-y-3">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {strainResults.map((s) => {
                  const thc = fmtRange(s.thc_min, s.thc_max, "%") ?? (s.thc_pct != null ? `~${s.thc_pct}%` : null);
                  const cbd = fmtRange(s.cbd_min, s.cbd_max, "%") ?? (s.cbd_pct != null ? `~${s.cbd_pct}%` : null);
                  const flower = fmtRange(s.flowering_min_weeks, s.flowering_max_weeks, " wk");
                  return (
                    <Card key={s.id}>
                      <CardContent className="space-y-2 p-4">
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium">{s.name}</p>
                            {s.breeder && <p className="text-xs text-muted-foreground">{s.breeder}</p>}
                          </div>
                          <Dna className="size-4 text-muted-foreground" />
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {s.strain_type && <Badge className="text-xs">{s.strain_type}</Badge>}
                          {s.genetics && (
                            <Badge variant="secondary" className="text-xs">
                              {s.genetics}
                            </Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-x-3 text-xs text-muted-foreground">
                          {thc && <span>THC: {thc}</span>}
                          {cbd && <span>CBD: {cbd}</span>}
                          {flower && <span>Flower: {flower}</span>}
                          {s.yield_indoor && <span>Indoor: {s.yield_indoor}</span>}
                        </div>
                        {s.terpenes?.length ? (
                          <p className="text-xs">
                            <span className="text-muted-foreground">Terpenes:</span> {s.terpenes.join(", ")}
                          </p>
                        ) : null}
                        {s.effects?.length ? (
                          <p className="text-xs">
                            <span className="text-muted-foreground">Effects:</span> {s.effects.join(", ")}
                          </p>
                        ) : null}
                        {s.flavors?.length ? (
                          <p className="text-xs">
                            <span className="text-muted-foreground">Flavors:</span> {s.flavors.join(", ")}
                          </p>
                        ) : null}
                        {s.sources?.length ? (
                          <p className="text-[11px] text-muted-foreground">
                            Sources: {s.sources.join(", ")}
                            {s.last_verified ? ` · verified ${s.last_verified}` : ""}
                          </p>
                        ) : null}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
              <p className="text-xs text-muted-foreground">{STRAIN_DATA_CAVEAT}</p>
            </div>
          )}

          {strainResults.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Dna className="mb-2 size-8 opacity-50" />
              <p className="text-sm">Search above to find strains in the global database</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="nutrients" className="mt-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Search className="size-4" /> Nutrient Search
              </CardTitle>
              <CardDescription>
                Search by name, brand, or barcode across the nutrient reference database
              </CardDescription>
            </CardHeader>
            <CardContent>
              <NutrientSearch
                placeholder="Search nutrients (e.g. General Hydroponics, Fox Farm)..."
                onSelect={(n) => {
                  setNutrientResults((prev) => {
                    if (prev.some((r) => r.id === n.id)) return prev;
                    return [n, ...prev];
                  });
                }}
              />
            </CardContent>
          </Card>

          {nutrientResults.length > 0 && (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {nutrientResults.map((n) => (
                <Card key={n.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{n.name}</p>
                        {n.brand && (
                          <p className="text-xs text-muted-foreground">{n.brand}</p>
                        )}
                      </div>
                      <FlaskConical className="size-4 text-muted-foreground" />
                    </div>
                    {typeof n.nutrients?.description === "string" && (
                      <p className="mt-1.5 text-xs text-muted-foreground">
                        {n.nutrients.description}
                      </p>
                    )}
                    <div className="mt-2 flex flex-wrap gap-2">
                      {n.npk && (
                        <Badge variant="secondary" className="text-xs">
                          NPK: {n.npk}
                        </Badge>
                      )}
                      {typeof n.nutrients?.type === "string" && (
                        <Badge variant="secondary" className="text-xs">
                          {n.nutrients.type}
                        </Badge>
                      )}
                      {n.nutrients?.dosage_ml_per_gal != null && typeof n.nutrients.dosage_ml_per_gal === "object" ? (
                        <Badge variant="outline" className="text-xs">
                          {Object.entries(n.nutrients.dosage_ml_per_gal as Record<string, number>).map(([stage, ml]) => `${stage}: ${ml} ml/gal`).join(", ")}
                        </Badge>
                      ) : null}
                      {n.nutrients?.dosage_g_per_gal != null && typeof n.nutrients.dosage_g_per_gal === "object" ? (
                        <Badge variant="outline" className="text-xs">
                          {Object.entries(n.nutrients.dosage_g_per_gal as Record<string, number>).map(([stage, g]) => `${stage}: ${g} g/gal`).join(", ")}
                        </Badge>
                      ) : null}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {nutrientResults.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <FlaskConical className="mb-2 size-8 opacity-50" />
              <p className="text-sm">Search above to find nutrients in the reference database</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
    </>
  );
}
