"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useGrow } from "@/hooks/use-grow";
import { getAccessToken } from "@/lib/auth";
import { listBuckets, quickLogFeeding, type BucketResponse } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { cn } from "@/lib/utils";
import { Check, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { usePreferences } from "@/hooks/use-preferences";
import { tempUnitLabel } from "@/lib/units";

interface FeedingLogFormProps {
  onSuccess: () => void;
}

const RECENT_VALUES_KEY = "tendril_recent_feeding";

function getRecentValues(): Partial<{ ph: string; ec: string; water_temp_f: string; volume_gal: string }> {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(RECENT_VALUES_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveRecentValues(values: Record<string, string>) {
  try {
    localStorage.setItem(RECENT_VALUES_KEY, JSON.stringify(values));
  } catch { /* ignore */ }
}

export function FeedingLogForm({ onSuccess }: FeedingLogFormProps) {
  const { selectedGrow } = useGrow();
  const { prefs } = usePreferences();
  const [selectedBucketIds, setSelectedBucketIds] = useState<string[]>([]);
  const [ph, setPh] = useState(() => getRecentValues().ph || "");
  const [ec, setEc] = useState(() => getRecentValues().ec || "");
  const [waterTemp, setWaterTemp] = useState(() => getRecentValues().water_temp_f || "");
  const [volume, setVolume] = useState(() => getRecentValues().volume_gal || "");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const {
    data: bucketData,
    isLoading: loadingBuckets,
  } = useApiSWR<BucketResponse[]>(
    selectedGrow ? ["quick-log", "feeding", "buckets", selectedGrow.id] : null,
    (token) => listBuckets(token, selectedGrow!.id),
  );
  const buckets = bucketData ?? [];

  // Load buckets for active grow
  useEffect(() => {
    setSelectedBucketIds(buckets.map((bucket) => bucket.id));
  }, [buckets]);

  const toggleBucket = (id: string) => {
    setSelectedBucketIds((prev) =>
      prev.includes(id) ? prev.filter((b) => b !== id) : [...prev, id],
    );
  };

  const selectAll = () => setSelectedBucketIds(buckets.map((b) => b.id));
  const selectNone = () => setSelectedBucketIds([]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selectedBucketIds.length === 0) {
      toast.error("Select at least one bucket");
      return;
    }

    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await quickLogFeeding(token, {
        bucket_ids: selectedBucketIds,
        ph: ph ? parseFloat(ph) : undefined,
        ec: ec ? parseFloat(ec) : undefined,
        water_temp_f: waterTemp ? parseFloat(waterTemp) : undefined,
        volume_gal: volume ? parseFloat(volume) : undefined,
        notes: notes || undefined,
      });

      // Save recent values
      saveRecentValues({ ph, ec, water_temp_f: waterTemp, volume_gal: volume });

      toast.success(`Logged feeding for ${selectedBucketIds.length} bucket(s)`);
      onSuccess();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to log feeding");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Bucket selector */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">Buckets</Label>
          <div className="flex gap-2 text-xs">
            <button type="button" onClick={selectAll} className="text-primary hover:underline">All</button>
            <button type="button" onClick={selectNone} className="text-muted-foreground hover:underline">None</button>
          </div>
        </div>
        {loadingBuckets ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="size-4 animate-spin" /> Loading buckets...
          </div>
        ) : buckets.length === 0 ? (
          <p className="text-sm text-muted-foreground">No buckets in active grow</p>
        ) : (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {buckets.map((bucket) => (
              <button
                key={bucket.id}
                type="button"
                onClick={() => toggleBucket(bucket.id)}
                className={cn(
                  "flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
                  selectedBucketIds.includes(bucket.id)
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:border-primary/50",
                )}
              >
                <div
                  className={cn(
                    "flex size-4 items-center justify-center rounded border transition-colors",
                    selectedBucketIds.includes(bucket.id)
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-muted-foreground/30",
                  )}
                >
                  {selectedBucketIds.includes(bucket.id) && <Check className="size-3" />}
                </div>
                <span className="truncate">{bucket.label || `#${bucket.position}`}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Reading inputs */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label htmlFor="ql-ph" className="text-xs">pH</Label>
          <Input
            id="ql-ph"
            type="number"
            step="0.1"
            min="0"
            max="14"
            placeholder="6.0"
            value={ph}
            onChange={(e) => setPh(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ql-ec" className="text-xs">EC (mS/cm)</Label>
          <Input
            id="ql-ec"
            type="number"
            step="0.1"
            min="0"
            placeholder="1.2"
            value={ec}
            onChange={(e) => setEc(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ql-temp" className="text-xs">Water Temp ({tempUnitLabel(prefs.temp_unit)})</Label>
          <Input
            id="ql-temp"
            type="number"
            step="0.1"
            placeholder="68"
            value={waterTemp}
            onChange={(e) => setWaterTemp(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ql-vol" className="text-xs">Volume (gal)</Label>
          <Input
            id="ql-vol"
            type="number"
            step="0.1"
            min="0"
            placeholder="5.0"
            value={volume}
            onChange={(e) => setVolume(e.target.value)}
          />
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-1">
        <Label htmlFor="ql-notes" className="text-xs">Notes (optional)</Label>
        <Textarea
          id="ql-notes"
          placeholder="Flush and fill, added CalMag..."
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>

      <Button type="submit" className="w-full" disabled={submitting || selectedBucketIds.length === 0}>
        {submitting ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
        Log Feeding ({selectedBucketIds.length} bucket{selectedBucketIds.length !== 1 ? "s" : ""})
      </Button>
    </form>
  );
}
