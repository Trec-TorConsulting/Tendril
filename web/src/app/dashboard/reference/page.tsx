"use client";

import { useState } from "react";
import { ReferenceStrainSearch, NutrientSearch } from "@/components/reference-search";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dna, FlaskConical, Search } from "lucide-react";
import { PageHeader } from "@/components/page-header";

interface StrainResult {
  id: string;
  name: string;
  breeder: string | null;
  genetics: string | null;
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
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {strainResults.map((s) => (
                <Card key={s.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium">{s.name}</p>
                        {s.breeder && (
                          <p className="text-xs text-muted-foreground">{s.breeder}</p>
                        )}
                      </div>
                      <Dna className="size-4 text-muted-foreground" />
                    </div>
                    {s.genetics && (
                      <Badge variant="secondary" className="mt-2 text-xs">
                        {s.genetics}
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              ))}
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
                    {n.nutrients?.description && (
                      <p className="mt-1.5 text-xs text-muted-foreground">
                        {n.nutrients.description as string}
                      </p>
                    )}
                    <div className="mt-2 flex flex-wrap gap-2">
                      {n.npk && (
                        <Badge variant="secondary" className="text-xs">
                          NPK: {n.npk}
                        </Badge>
                      )}
                      {n.nutrients?.type && (
                        <Badge variant="secondary" className="text-xs">
                          {n.nutrients.type as string}
                        </Badge>
                      )}
                      {n.nutrients?.dosage_ml_per_gal && (
                        <Badge variant="outline" className="text-xs">
                          {Object.entries(n.nutrients.dosage_ml_per_gal as Record<string, number>).map(([stage, ml]) => `${stage}: ${ml} ml/gal`).join(", ")}
                        </Badge>
                      )}
                      {n.nutrients?.dosage_g_per_gal && (
                        <Badge variant="outline" className="text-xs">
                          {Object.entries(n.nutrients.dosage_g_per_gal as Record<string, number>).map(([stage, g]) => `${stage}: ${g} g/gal`).join(", ")}
                        </Badge>
                      )}
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
