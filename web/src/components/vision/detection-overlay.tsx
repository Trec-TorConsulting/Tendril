import { cn } from "@/lib/utils";

export interface OverlayDetection {
  class_name: string;
  confidence: number;
  /** Normalized `[x, y, w, h]` — top-left corner plus width/height in `[0, 1]`. */
  bbox: number[];
}

const CLASS_COLORS = [
  "#ef4444", // red
  "#f59e0b", // amber
  "#10b981", // emerald
  "#3b82f6", // blue
  "#a855f7", // purple
  "#ec4899", // pink
];

/** Deterministic color per class label so the same class is always the same color. */
export function colorForClass(className: string): string {
  let hash = 0;
  for (let i = 0; i < className.length; i++) {
    hash = (hash * 31 + className.charCodeAt(i)) >>> 0;
  }
  return CLASS_COLORS[hash % CLASS_COLORS.length];
}

export interface DetectionOverlayProps {
  src: string;
  alt?: string;
  detections: OverlayDetection[];
  show?: boolean;
  className?: string;
}

/**
 * Renders an image with color-coded, labeled detection bounding boxes overlaid.
 * Bounding boxes use normalized coordinates so they scale with any image size.
 */
export function DetectionOverlay({ src, alt, detections, show = true, className }: DetectionOverlayProps) {
  return (
    <div className={cn("relative inline-block w-full overflow-hidden rounded-md bg-muted", className)}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt ?? "Scanned image"} className="block h-auto w-full object-contain" />
      {show &&
        detections.map((det, index) => {
          const [x, y, w, h] = det.bbox;
          const color = colorForClass(det.class_name);
          return (
            <div
              key={`${det.class_name}-${index}`}
              data-testid="detection-box"
              className="absolute rounded-sm border-2"
              style={{
                left: `${x * 100}%`,
                top: `${y * 100}%`,
                width: `${w * 100}%`,
                height: `${h * 100}%`,
                borderColor: color,
                boxShadow: "0 0 0 1px rgba(0,0,0,0.35)",
              }}
            >
              <span
                className="absolute left-0 top-0 -translate-y-full whitespace-nowrap rounded-t-sm px-1 text-[10px] font-semibold leading-tight text-white"
                style={{ backgroundColor: color }}
              >
                {det.class_name} {Math.round(det.confidence * 100)}%
              </span>
            </div>
          );
        })}
    </div>
  );
}
