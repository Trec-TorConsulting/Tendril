"use client";

import { useState } from "react";
import { Eye, EyeOff, Loader2, ScanSearch } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DetectionOverlay, colorForClass } from "@/components/vision/detection-overlay";
import { scanGrowPhoto, scanTentSnapshot, type VisionProfile, type VisionScanResponse } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";

export interface VisionScanPanelProps {
  source: "tent" | "photo";
  sourceId: string;
  /** Data URI or URL used for the preview image and overlay. */
  imageSrc: string;
  profile?: VisionProfile;
  className?: string;
}

/**
 * On-demand vision detection panel: runs a Coral/GPU/CPU-backed object-detection
 * scan on a tent snapshot or grow photo and renders the results as an overlay
 * plus a labeled detections list. Actionable findings are routed to the AI
 * approval queue on the backend — nothing is auto-applied.
 */
export function VisionScanPanel({ source, sourceId, imageSrc, profile, className }: VisionScanPanelProps) {
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<VisionScanResponse | null>(null);
  const [showBoxes, setShowBoxes] = useState(true);

  const detections = result?.detections ?? [];
  const unavailable = result !== null && !result.model_version;

  async function runScan() {
    const token = getAccessToken();
    if (!token) {
      toast.error("You need to sign in to run a scan.");
      return;
    }
    setScanning(true);
    try {
      const res =
        source === "tent"
          ? await scanTentSnapshot(token, sourceId, profile)
          : await scanGrowPhoto(token, sourceId, profile);
      setResult(res);
      if (!res.model_version) {
        toast.info(res.message ?? "Detection is not configured yet.");
      } else if (res.detections.length === 0) {
        toast.success("No issues detected.");
      } else {
        toast.success(`${res.detections.length} detection${res.detections.length === 1 ? "" : "s"} found.`);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Scan failed.");
    } finally {
      setScanning(false);
    }
  }

  return (
    <div className={cn("space-y-3", className)}>
      <DetectionOverlay src={imageSrc} detections={detections} show={showBoxes} />

      <div className="flex flex-wrap items-center gap-2">
        <Button onClick={runScan} disabled={scanning} size="sm">
          {scanning ? <Loader2 className="size-4 animate-spin" /> : <ScanSearch className="size-4" />}
          {scanning ? "Scanning…" : "Scan for issues"}
        </Button>
        {detections.length > 0 && (
          <Button variant="ghost" size="sm" onClick={() => setShowBoxes((s) => !s)}>
            {showBoxes ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
            {showBoxes ? "Hide boxes" : "Show boxes"}
          </Button>
        )}
        {result?.accelerator_tier && result.model_version && (
          <span className="text-xs text-muted-foreground">
            {result.accelerator_tier.toUpperCase()} · model {result.model_version}
          </span>
        )}
      </div>

      {result &&
        (unavailable ? (
          <p className="text-sm text-muted-foreground">
            Detection is not configured. Ask an operator to activate a vision model.
          </p>
        ) : detections.length === 0 ? (
          <p className="text-sm text-muted-foreground">No issues detected in this image.</p>
        ) : (
          <ul className="space-y-1.5" aria-label="Detections">
            {detections.map((det, index) => (
              <li
                key={`${det.class_name}-${index}`}
                className="flex items-center justify-between rounded-md border border-border px-2.5 py-1.5 text-sm"
              >
                <span className="flex items-center gap-2">
                  <span
                    className="inline-block size-2.5 rounded-full"
                    style={{ backgroundColor: colorForClass(det.class_name) }}
                    aria-hidden
                  />
                  {det.class_name}
                </span>
                <Badge variant="secondary">{Math.round(det.confidence * 100)}%</Badge>
              </li>
            ))}
          </ul>
        ))}

      {detections.length > 0 && (
        <p className="text-xs text-muted-foreground">
          Actionable findings are sent to the AI approval queue for your review — nothing is applied automatically.
        </p>
      )}
    </div>
  );
}
