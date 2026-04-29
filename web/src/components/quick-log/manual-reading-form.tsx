"use client";

import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useGrow } from "@/hooks/use-grow";
import { getAccessToken } from "@/lib/auth";
import { quickLogReading } from "@/lib/api";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface ManualReadingFormProps {
  onSuccess: () => void;
}

export function ManualReadingForm({ onSuccess }: ManualReadingFormProps) {
  const { selectedGrow } = useGrow();
  const [tempF, setTempF] = useState("");
  const [humidity, setHumidity] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Auto-calculate VPD from temp and humidity (derived state)
  const vpd = useMemo(() => {
    if (!tempF || !humidity) return "";
    const t = parseFloat(tempF);
    const h = parseFloat(humidity);
    if (isNaN(t) || isNaN(h)) return "";
    const tC = (t - 32) * 5 / 9;
    const svp = 0.6108 * Math.exp((17.27 * tC) / (tC + 237.3));
    return (svp * (1 - h / 100)).toFixed(2);
  }, [tempF, humidity]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedGrow) {
      toast.error("No active grow selected");
      return;
    }

    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await quickLogReading(token, {
        tent_id: selectedGrow.tent_id,
        temp_f: tempF ? parseFloat(tempF) : undefined,
        humidity: humidity ? parseFloat(humidity) : undefined,
        vpd: vpd ? parseFloat(vpd) : undefined,
      });
      toast.success("Environment reading logged");
      onSuccess();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to log reading");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <p className="text-sm text-muted-foreground">
        Log ambient environment for <strong>{selectedGrow?.name || "active grow"}</strong>
      </p>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label htmlFor="mr-temp" className="text-xs">Temp (°F)</Label>
          <Input
            id="mr-temp"
            type="number"
            step="0.1"
            placeholder="78"
            value={tempF}
            onChange={(e) => setTempF(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="mr-humidity" className="text-xs">Humidity (%)</Label>
          <Input
            id="mr-humidity"
            type="number"
            step="1"
            min="0"
            max="100"
            placeholder="55"
            value={humidity}
            onChange={(e) => setHumidity(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label htmlFor="mr-vpd" className="text-xs">VPD (kPa) — auto-calculated</Label>
        <Input
          id="mr-vpd"
          type="number"
          step="0.01"
          min="0"
          placeholder="1.05"
          value={vpd}
          readOnly
        />
      </div>

      <Button type="submit" className="w-full" disabled={submitting || (!tempF && !humidity)}>
        {submitting ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
        Log Reading
      </Button>
    </form>
  );
}
