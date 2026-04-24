"use client";

import { useCallback, useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  listSoilTests,
  createSoilTest,
  deleteSoilTest,
  listAmendments,
  createAmendment,
  deleteAmendment,
  type SoilTestResponse,
  type AmendmentResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FlaskConical, Leaf, Trash2, Plus, TrendingUp, TrendingDown } from "lucide-react";

const AMENDMENT_TYPES = [
  "compost", "worm_castings", "bone_meal", "blood_meal", "kelp",
  "lime", "sulfur", "gypsum", "cover_crop", "mulch", "fish_emulsion",
  "bat_guano", "rock_phosphate", "greensand", "mycorrhizae", "custom",
];

interface Props {
  growId: string;
}

export function SoilDashboard({ growId }: Props) {
  const [tests, setTests] = useState<SoilTestResponse[]>([]);
  const [amendments, setAmendments] = useState<AmendmentResponse[]>([]);
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [showAmendmentDialog, setShowAmendmentDialog] = useState(false);
  const [loading, setLoading] = useState(true);

  // Test form
  const [testForm, setTestForm] = useState({
    ph: "", nitrogen_ppm: "", phosphorus_ppm: "", potassium_ppm: "",
    organic_matter_pct: "", cec: "", calcium_ppm: "", magnesium_ppm: "",
    sulfur_ppm: "", source: "home_kit", notes: "",
  });

  // Amendment form
  const [amendForm, setAmendForm] = useState({
    amendment_type: "compost", product_name: "", quantity: "",
    area_applied: "", cost: "", notes: "",
  });

  const refresh = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) return;
    try {
      const [t, a] = await Promise.all([
        listSoilTests(token, growId),
        listAmendments(token, growId),
      ]);
      setTests(t);
      setAmendments(a);
    } finally {
      setLoading(false);
    }
  }, [growId]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleCreateTest = async () => {
    const token = await getAccessToken();
    if (!token) return;
    const data: Record<string, unknown> = { source: testForm.source };
    if (testForm.ph) data.ph = +testForm.ph;
    if (testForm.nitrogen_ppm) data.nitrogen_ppm = +testForm.nitrogen_ppm;
    if (testForm.phosphorus_ppm) data.phosphorus_ppm = +testForm.phosphorus_ppm;
    if (testForm.potassium_ppm) data.potassium_ppm = +testForm.potassium_ppm;
    if (testForm.organic_matter_pct) data.organic_matter_pct = +testForm.organic_matter_pct;
    if (testForm.cec) data.cec = +testForm.cec;
    if (testForm.calcium_ppm) data.calcium_ppm = +testForm.calcium_ppm;
    if (testForm.magnesium_ppm) data.magnesium_ppm = +testForm.magnesium_ppm;
    if (testForm.sulfur_ppm) data.sulfur_ppm = +testForm.sulfur_ppm;
    if (testForm.notes) data.notes = testForm.notes;

    await createSoilTest(token, growId, data);
    setShowTestDialog(false);
    setTestForm({ ph: "", nitrogen_ppm: "", phosphorus_ppm: "", potassium_ppm: "", organic_matter_pct: "", cec: "", calcium_ppm: "", magnesium_ppm: "", sulfur_ppm: "", source: "home_kit", notes: "" });
    refresh();
  };

  const handleCreateAmendment = async () => {
    const token = await getAccessToken();
    if (!token) return;
    const data: Record<string, unknown> = {
      amendment_type: amendForm.amendment_type,
      product_name: amendForm.product_name,
    };
    if (amendForm.quantity) data.quantity = amendForm.quantity;
    if (amendForm.area_applied) data.area_applied = amendForm.area_applied;
    if (amendForm.cost) data.cost = +amendForm.cost;
    if (amendForm.notes) data.notes = amendForm.notes;

    await createAmendment(token, growId, data);
    setShowAmendmentDialog(false);
    setAmendForm({ amendment_type: "compost", product_name: "", quantity: "", area_applied: "", cost: "", notes: "" });
    refresh();
  };

  const handleDeleteTest = async (id: string) => {
    const token = await getAccessToken();
    if (!token) return;
    await deleteSoilTest(token, growId, id);
    refresh();
  };

  const handleDeleteAmendment = async (id: string) => {
    const token = await getAccessToken();
    if (!token) return;
    await deleteAmendment(token, growId, id);
    refresh();
  };

  const latest = tests[0];
  const totalCost = amendments.reduce((s, a) => s + (a.cost ?? 0), 0);

  // Soil health score (simplified: based on pH in range + NPK presence)
  let healthScore: number | null = null;
  if (latest) {
    let score = 50; // base
    if (latest.ph !== null && latest.ph >= 6.0 && latest.ph <= 7.0) score += 20;
    else if (latest.ph !== null && latest.ph >= 5.5 && latest.ph <= 7.5) score += 10;
    if (latest.nitrogen_ppm !== null && latest.nitrogen_ppm > 20) score += 10;
    if (latest.phosphorus_ppm !== null && latest.phosphorus_ppm > 10) score += 10;
    if (latest.potassium_ppm !== null && latest.potassium_ppm > 50) score += 10;
    healthScore = Math.min(100, score);
  }

  if (loading) return <div className="flex justify-center py-8"><div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" /></div>;

  return (
    <div className="space-y-4">
      <Tabs defaultValue="tests">
        <TabsList>
          <TabsTrigger value="tests">Soil Tests</TabsTrigger>
          <TabsTrigger value="amendments">Amendments</TabsTrigger>
        </TabsList>

        <TabsContent value="tests" className="space-y-4">
          {/* Health score card */}
          {healthScore !== null && (
            <Card>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <p className="text-sm text-muted-foreground">Soil Health Score</p>
                  <p className="text-3xl font-bold">{healthScore}</p>
                </div>
                <div className={`flex size-16 items-center justify-center rounded-full text-2xl font-bold ${
                  healthScore >= 80 ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400" :
                  healthScore >= 50 ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-400" :
                  "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400"
                }`}>
                  {healthScore >= 80 ? <TrendingUp /> : healthScore >= 50 ? "—" : <TrendingDown />}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Latest test summary */}
          {latest && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Latest Test — {new Date(latest.tested_at).toLocaleDateString()}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-2 text-sm sm:grid-cols-5">
                  {latest.ph !== null && <div><span className="text-muted-foreground">pH</span><br /><strong>{latest.ph}</strong></div>}
                  {latest.nitrogen_ppm !== null && <div><span className="text-muted-foreground">N</span><br /><strong>{latest.nitrogen_ppm}</strong></div>}
                  {latest.phosphorus_ppm !== null && <div><span className="text-muted-foreground">P</span><br /><strong>{latest.phosphorus_ppm}</strong></div>}
                  {latest.potassium_ppm !== null && <div><span className="text-muted-foreground">K</span><br /><strong>{latest.potassium_ppm}</strong></div>}
                  {latest.organic_matter_pct !== null && <div><span className="text-muted-foreground">OM%</span><br /><strong>{latest.organic_matter_pct}%</strong></div>}
                  {latest.cec !== null && <div><span className="text-muted-foreground">CEC</span><br /><strong>{latest.cec}</strong></div>}
                  {latest.calcium_ppm !== null && <div><span className="text-muted-foreground">Ca</span><br /><strong>{latest.calcium_ppm}</strong></div>}
                  {latest.magnesium_ppm !== null && <div><span className="text-muted-foreground">Mg</span><br /><strong>{latest.magnesium_ppm}</strong></div>}
                  {latest.sulfur_ppm !== null && <div><span className="text-muted-foreground">S</span><br /><strong>{latest.sulfur_ppm}</strong></div>}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-between">
            <h3 className="text-sm font-medium">Test History ({tests.length})</h3>
            <Button size="sm" onClick={() => setShowTestDialog(true)}><Plus className="mr-1 size-3" /> Log Test</Button>
          </div>

          {tests.length === 0 ? (
            <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">
              <FlaskConical className="mx-auto mb-2 size-8 text-muted-foreground/50" />
              No soil tests yet. Log your first test to start tracking soil health.
            </CardContent></Card>
          ) : (
            <div className="space-y-2">
              {tests.map((t) => (
                <Card key={t.id} className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="text-sm">
                      <p className="font-medium">{new Date(t.tested_at).toLocaleDateString()}</p>
                      <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                        {t.ph !== null && <span>pH: {t.ph}</span>}
                        {t.nitrogen_ppm !== null && <span>N: {t.nitrogen_ppm}</span>}
                        {t.phosphorus_ppm !== null && <span>P: {t.phosphorus_ppm}</span>}
                        {t.potassium_ppm !== null && <span>K: {t.potassium_ppm}</span>}
                      </div>
                      <Badge variant="outline" className="mt-1 text-xs">{t.source}</Badge>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteTest(t.id)}><Trash2 className="size-3" /></Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="amendments" className="space-y-4">
          {totalCost > 0 && (
            <Card>
              <CardContent className="flex items-center justify-between p-4">
                <div><p className="text-sm text-muted-foreground">Total Amendment Cost</p></div>
                <p className="text-2xl font-bold">${totalCost.toFixed(2)}</p>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-between">
            <h3 className="text-sm font-medium">Amendment Log ({amendments.length})</h3>
            <Button size="sm" onClick={() => setShowAmendmentDialog(true)}><Plus className="mr-1 size-3" /> Log Amendment</Button>
          </div>

          {amendments.length === 0 ? (
            <Card><CardContent className="py-8 text-center text-sm text-muted-foreground">
              <Leaf className="mx-auto mb-2 size-8 text-muted-foreground/50" />
              No amendments logged yet. Track your soil amendments for better grow analytics.
            </CardContent></Card>
          ) : (
            <div className="space-y-2">
              {amendments.map((a) => (
                <Card key={a.id} className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="text-sm">
                      <p className="font-medium">{a.product_name}</p>
                      <div className="mt-1 flex flex-wrap gap-2 text-xs text-muted-foreground">
                        <Badge variant="outline">{a.amendment_type.replace(/_/g, " ")}</Badge>
                        <span>{new Date(a.applied_at).toLocaleDateString()}</span>
                        {a.quantity && <span>{a.quantity}</span>}
                        {a.cost !== null && <span>${a.cost.toFixed(2)}</span>}
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => handleDeleteAmendment(a.id)}><Trash2 className="size-3" /></Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Soil test dialog */}
      <Dialog open={showTestDialog} onOpenChange={setShowTestDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Soil Test</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>pH</Label><Input type="number" step="0.1" value={testForm.ph} onChange={(e) => setTestForm({ ...testForm, ph: e.target.value })} /></div>
            <div><Label>Source</Label>
              <Select value={testForm.source} onValueChange={(v) => setTestForm({ ...testForm, source: v ?? "home_kit" })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="home_kit">Home Kit</SelectItem>
                  <SelectItem value="lab">Lab Test</SelectItem>
                  <SelectItem value="sensor">Sensor</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div><Label>Nitrogen (ppm)</Label><Input type="number" value={testForm.nitrogen_ppm} onChange={(e) => setTestForm({ ...testForm, nitrogen_ppm: e.target.value })} /></div>
            <div><Label>Phosphorus (ppm)</Label><Input type="number" value={testForm.phosphorus_ppm} onChange={(e) => setTestForm({ ...testForm, phosphorus_ppm: e.target.value })} /></div>
            <div><Label>Potassium (ppm)</Label><Input type="number" value={testForm.potassium_ppm} onChange={(e) => setTestForm({ ...testForm, potassium_ppm: e.target.value })} /></div>
            <div><Label>Organic Matter %</Label><Input type="number" step="0.1" value={testForm.organic_matter_pct} onChange={(e) => setTestForm({ ...testForm, organic_matter_pct: e.target.value })} /></div>
            <div><Label>CEC</Label><Input type="number" step="0.1" value={testForm.cec} onChange={(e) => setTestForm({ ...testForm, cec: e.target.value })} /></div>
            <div><Label>Calcium (ppm)</Label><Input type="number" value={testForm.calcium_ppm} onChange={(e) => setTestForm({ ...testForm, calcium_ppm: e.target.value })} /></div>
            <div><Label>Magnesium (ppm)</Label><Input type="number" value={testForm.magnesium_ppm} onChange={(e) => setTestForm({ ...testForm, magnesium_ppm: e.target.value })} /></div>
            <div><Label>Sulfur (ppm)</Label><Input type="number" value={testForm.sulfur_ppm} onChange={(e) => setTestForm({ ...testForm, sulfur_ppm: e.target.value })} /></div>
          </div>
          <div><Label>Notes</Label><Textarea value={testForm.notes} onChange={(e) => setTestForm({ ...testForm, notes: e.target.value })} /></div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTestDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateTest}>Save Test</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Amendment dialog */}
      <Dialog open={showAmendmentDialog} onOpenChange={setShowAmendmentDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Log Soil Amendment</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div><Label>Amendment Type</Label>
              <Select value={amendForm.amendment_type} onValueChange={(v) => setAmendForm({ ...amendForm, amendment_type: v ?? "compost" })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {AMENDMENT_TYPES.map((t) => <SelectItem key={t} value={t}>{t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div><Label>Product Name</Label><Input value={amendForm.product_name} onChange={(e) => setAmendForm({ ...amendForm, product_name: e.target.value })} placeholder="e.g., Espoma Garden Tone" /></div>
            <div><Label>Quantity</Label><Input value={amendForm.quantity} onChange={(e) => setAmendForm({ ...amendForm, quantity: e.target.value })} placeholder="e.g., 2 cups per plant" /></div>
            <div><Label>Area Applied</Label><Input value={amendForm.area_applied} onChange={(e) => setAmendForm({ ...amendForm, area_applied: e.target.value })} placeholder="e.g., Beds 1-3" /></div>
            <div><Label>Cost ($)</Label><Input type="number" step="0.01" value={amendForm.cost} onChange={(e) => setAmendForm({ ...amendForm, cost: e.target.value })} /></div>
            <div><Label>Notes</Label><Textarea value={amendForm.notes} onChange={(e) => setAmendForm({ ...amendForm, notes: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAmendmentDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateAmendment} disabled={!amendForm.product_name}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
