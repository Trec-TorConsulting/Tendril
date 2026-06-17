"use client";

import { useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { useApiSWR } from "@/lib/swr";
import {
  listExpenses,
  createExpense,
  deleteExpense,
  listHarvestValues,
  createHarvestValue,
  deleteHarvestValue,
  compareGrowsROI,
  listGrows,
  type Expense,
  type HarvestValueEntry,
  type ROISummary,
  type GrowResponse,
} from "@/lib/api";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { DollarSign, TrendingUp, Trash2, Plus } from "lucide-react";
import { toast } from "sonner";

const CATEGORIES = ["nutrients", "electricity", "water", "equipment", "labor", "rent", "supplies", "other"] as const;

function formatCents(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export default function CostROIPage() {
  const { data: rawData, isLoading: loading, mutate } = useApiSWR(
    ["cost-roi"],
    async (token) => {
      const [exp, hv, roi, activeGrows, closedGrows] = await Promise.all([
        listExpenses(token),
        listHarvestValues(token),
        compareGrowsROI(token, [], 10),
        listGrows(token, { status: "active" }),
        listGrows(token, { status: "completed" }),
      ]);
      return { expenses: exp, harvestValues: hv, roiComparison: roi.grows, grows: [...activeGrows, ...closedGrows] };
    },
  );
  const expenses = rawData?.expenses ?? [];
  const harvestValues = rawData?.harvestValues ?? [];
  const roiComparison = rawData?.roiComparison ?? [];
  const grows = rawData?.grows ?? [];
  const refresh = mutate;
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showHarvestForm, setShowHarvestForm] = useState(false);

  // Expense form state
  const [expGrowId, setExpGrowId] = useState("");
  const [expCategory, setExpCategory] = useState<string>("nutrients");
  const [expAmount, setExpAmount] = useState("");
  const [expDescription, setExpDescription] = useState("");
  const [expVendor, setExpVendor] = useState("");

  // Harvest value form state
  const [hvGrowId, setHvGrowId] = useState("");
  const [hvGrade, setHvGrade] = useState("A");
  const [hvWeight, setHvWeight] = useState("");
  const [hvPrice, setHvPrice] = useState("");

  async function handleCreateExpense(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    const amountCents = Math.round(parseFloat(expAmount) * 100);
    if (!expGrowId || isNaN(amountCents) || amountCents <= 0) {
      toast.error("Please fill in grow ID and a valid amount");
      return;
    }
    try {
      await createExpense(token, {
        grow_cycle_id: expGrowId,
        category: expCategory,
        amount_cents: amountCents,
        description: expDescription || undefined,
        vendor: expVendor || undefined,
      });
      toast.success("Expense logged");
      setShowExpenseForm(false);
      setExpAmount("");
      setExpDescription("");
      setExpVendor("");
      refresh();
    } catch {
      toast.error("Failed to create expense");
    }
  }

  async function handleCreateHarvestValue(e: React.FormEvent) {
    e.preventDefault();
    const token = getAccessToken();
    if (!token) return;
    const weightG = parseFloat(hvWeight);
    const priceCents = Math.round(parseFloat(hvPrice) * 100);
    if (!hvGrowId || isNaN(weightG) || isNaN(priceCents) || weightG <= 0 || priceCents <= 0) {
      toast.error("Please fill in all fields with valid values");
      return;
    }
    try {
      await createHarvestValue(token, {
        grow_cycle_id: hvGrowId,
        grade: hvGrade,
        weight_g: weightG,
        price_per_gram_cents: priceCents,
      });
      toast.success("Harvest value recorded");
      setShowHarvestForm(false);
      setHvWeight("");
      setHvPrice("");
      refresh();
    } catch {
      toast.error("Failed to record harvest value");
    }
  }

  async function handleDeleteExpense(id: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteExpense(token, id);
      toast.success("Expense deleted");
      refresh();
    } catch {
      toast.error("Failed to delete expense");
    }
  }

  async function handleDeleteHarvestValue(id: string) {
    const token = getAccessToken();
    if (!token) return;
    try {
      await deleteHarvestValue(token, id);
      toast.success("Harvest value deleted");
      refresh();
    } catch {
      toast.error("Failed to delete harvest value");
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Cost & ROI" description="Track expenses and calculate return on investment per grow" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  const totalExpenses = expenses.reduce((sum, e) => sum + e.amount_cents, 0);
  const totalHarvestValue = harvestValues.reduce((sum, h) => sum + Math.round(h.weight_g * h.price_per_gram_cents), 0);
  const overallROI = totalExpenses > 0 ? ((totalHarvestValue - totalExpenses) / totalExpenses * 100) : null;

  return (
    <div className="space-y-6">
      <PageHeader title="Cost & ROI" description="Track expenses and calculate return on investment per grow" />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Total Expenses</CardTitle>
            <DollarSign className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatCents(totalExpenses)}</p>
            <p className="text-xs text-neutral-500">{expenses.length} entries</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Total Harvest Value</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-400" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatCents(totalHarvestValue)}</p>
            <p className="text-xs text-neutral-500">{harvestValues.length} harvests graded</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-neutral-400">Overall ROI</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <p className={`text-2xl font-bold ${overallROI !== null && overallROI >= 0 ? "text-green-400" : "text-red-400"}`}>
              {overallROI !== null ? `${overallROI.toFixed(1)}%` : "—"}
            </p>
            <p className="text-xs text-neutral-500">across all grows</p>
          </CardContent>
        </Card>
      </div>

      {/* Grow-over-Grow ROI Comparison */}
      {roiComparison.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Grow Comparison</CardTitle>
            <CardDescription>ROI metrics across your completed grows</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-800 text-neutral-400">
                    <th className="text-left py-2 pr-4">Grow</th>
                    <th className="text-right py-2 px-4">Expenses</th>
                    <th className="text-right py-2 px-4">Harvest Value</th>
                    <th className="text-right py-2 px-4">Yield (g)</th>
                    <th className="text-right py-2 px-4">Cost/gram</th>
                    <th className="text-right py-2 pl-4">ROI</th>
                  </tr>
                </thead>
                <tbody>
                  {roiComparison.map((r) => (
                    <tr key={r.grow_cycle_id} className="border-b border-neutral-800/50">
                      <td className="py-2 pr-4 text-white">{r.grow_name}</td>
                      <td className="text-right py-2 px-4 text-red-400">{formatCents(r.total_expenses_cents)}</td>
                      <td className="text-right py-2 px-4 text-green-400">{formatCents(r.total_harvest_value_cents)}</td>
                      <td className="text-right py-2 px-4">{r.total_dry_weight_g.toFixed(1)}</td>
                      <td className="text-right py-2 px-4">{r.cost_per_gram_cents !== null ? formatCents(r.cost_per_gram_cents) : "—"}</td>
                      <td className={`text-right py-2 pl-4 font-medium ${r.roi_percentage !== null && r.roi_percentage >= 0 ? "text-green-400" : "text-red-400"}`}>
                        {r.roi_percentage !== null ? `${r.roi_percentage.toFixed(1)}%` : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Expenses Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Expenses</CardTitle>
            <CardDescription>Track costs per grow</CardDescription>
          </div>
          <Button size="sm" onClick={() => setShowExpenseForm(!showExpenseForm)}>
            <Plus className="h-4 w-4 mr-1" /> Log Expense
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {showExpenseForm && (
            <form onSubmit={handleCreateExpense} className="grid gap-3 rounded-lg border border-neutral-800 p-4 md:grid-cols-5">
              <select className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white" value={expGrowId} onChange={(e) => setExpGrowId(e.target.value)} required>
                <option value="">Select Grow</option>
                {grows.filter((g) => g.status === "active").length > 0 && (
                  <optgroup label="Active">
                    {grows.filter((g) => g.status === "active").map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </optgroup>
                )}
                {grows.filter((g) => g.status !== "active").length > 0 && (
                  <optgroup label="Closed">
                    {grows.filter((g) => g.status !== "active").map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </optgroup>
                )}
              </select>
              <select className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white" value={expCategory} onChange={(e) => setExpCategory(e.target.value)}>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <Input placeholder="Amount ($)" type="number" step="0.01" min="0.01" value={expAmount} onChange={(e) => setExpAmount(e.target.value)} required />
              <Input placeholder="Description" value={expDescription} onChange={(e) => setExpDescription(e.target.value)} />
              <div className="flex gap-2">
                <Input placeholder="Vendor" value={expVendor} onChange={(e) => setExpVendor(e.target.value)} />
                <Button type="submit" size="sm">Save</Button>
              </div>
            </form>
          )}
          {expenses.length === 0 ? (
            <p className="text-neutral-500 text-sm">No expenses logged yet. Start tracking to see your ROI.</p>
          ) : (
            <div className="space-y-2">
              {expenses.slice(0, 20).map((exp) => (
                <div key={exp.id} className="flex items-center justify-between rounded-md border border-neutral-800 px-4 py-2">
                  <div className="flex items-center gap-3">
                    <span className="rounded bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300">{exp.category}</span>
                    <span className="text-white font-medium">{formatCents(exp.amount_cents)}</span>
                    {exp.description && <span className="text-neutral-400 text-sm">{exp.description}</span>}
                    {exp.vendor && <span className="text-neutral-500 text-xs">({exp.vendor})</span>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-neutral-500">{new Date(exp.date).toLocaleDateString()}</span>
                    <button onClick={() => handleDeleteExpense(exp.id)} className="text-neutral-500 hover:text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Harvest Values Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Harvest Values</CardTitle>
            <CardDescription>Record market value by quality grade</CardDescription>
          </div>
          <Button size="sm" onClick={() => setShowHarvestForm(!showHarvestForm)}>
            <Plus className="h-4 w-4 mr-1" /> Record Value
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {showHarvestForm && (
            <form onSubmit={handleCreateHarvestValue} className="grid gap-3 rounded-lg border border-neutral-800 p-4 md:grid-cols-5">
              <select className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white" value={hvGrowId} onChange={(e) => setHvGrowId(e.target.value)} required>
                <option value="">Select Grow</option>
                {grows.filter((g) => g.status === "active").length > 0 && (
                  <optgroup label="Active">
                    {grows.filter((g) => g.status === "active").map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </optgroup>
                )}
                {grows.filter((g) => g.status !== "active").length > 0 && (
                  <optgroup label="Closed">
                    {grows.filter((g) => g.status !== "active").map((g) => <option key={g.id} value={g.id}>{g.name}</option>)}
                  </optgroup>
                )}
              </select>
              <select className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white" value={hvGrade} onChange={(e) => setHvGrade(e.target.value)}>
                <option value="A">Grade A</option>
                <option value="B">Grade B</option>
                <option value="trim">Trim</option>
                <option value="waste">Waste</option>
              </select>
              <Input placeholder="Weight (g)" type="number" step="0.1" min="0.1" value={hvWeight} onChange={(e) => setHvWeight(e.target.value)} required />
              <Input placeholder="Price per gram ($)" type="number" step="0.01" min="0.01" value={hvPrice} onChange={(e) => setHvPrice(e.target.value)} required />
              <Button type="submit" size="sm">Save</Button>
            </form>
          )}
          {harvestValues.length === 0 ? (
            <p className="text-neutral-500 text-sm">No harvest values recorded. Log after harvest to see ROI.</p>
          ) : (
            <div className="space-y-2">
              {harvestValues.slice(0, 20).map((hv) => (
                <div key={hv.id} className="flex items-center justify-between rounded-md border border-neutral-800 px-4 py-2">
                  <div className="flex items-center gap-3">
                    <span className="rounded bg-neutral-800 px-2 py-0.5 text-xs text-neutral-300">Grade {hv.grade}</span>
                    <span className="text-white font-medium">{hv.weight_g}g × {formatCents(hv.price_per_gram_cents)}/g</span>
                    <span className="text-green-400 text-sm">= {formatCents(Math.round(hv.weight_g * hv.price_per_gram_cents))}</span>
                  </div>
                  <button onClick={() => handleDeleteHarvestValue(hv.id)} className="text-neutral-500 hover:text-red-400">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
