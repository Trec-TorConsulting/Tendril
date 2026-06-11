"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

type GrowStage = "seed" | "seedling" | "vegetative" | "flowering" | "harvest";

interface GrowStageIndicatorProps {
  stage: string;
  dayInStage?: number;
  className?: string;
  size?: "sm" | "md" | "lg";
}

const STAGE_MAP: Record<string, GrowStage> = {
  germination: "seed",
  seed: "seed",
  seedling: "seedling",
  clone: "seedling",
  early_veg: "vegetative",
  late_veg: "vegetative",
  vegetative: "vegetative",
  transition: "flowering",
  early_flower: "flowering",
  mid_flower: "flowering",
  late_flower: "flowering",
  flowering: "flowering",
  ripening: "harvest",
  drying: "harvest",
  curing: "harvest",
  harvest: "harvest",
};

const STAGE_COLORS: Record<GrowStage, string> = {
  seed: "text-amber-600 dark:text-amber-400",
  seedling: "text-lime-500 dark:text-lime-400",
  vegetative: "text-emerald-500 dark:text-emerald-400",
  flowering: "text-purple-500 dark:text-purple-400",
  harvest: "text-orange-500 dark:text-orange-400",
};

const SIZE_MAP = { sm: "w-10 h-10", md: "w-16 h-16", lg: "w-24 h-24" };

function SeedSvg() {
  return (
    <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
      <ellipse cx="12" cy="14" rx="4" ry="6" fill="currentColor" opacity={0.8} />
      <path d="M12 8 C12 6 13 4 14 3" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
    </motion.g>
  );
}

function SeedlingSvg() {
  return (
    <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
      {/* Stem */}
      <motion.path
        d="M12 20 L12 12"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.6 }}
      />
      {/* Two small leaves */}
      <motion.path
        d="M12 14 C10 12 8 12 7 13 C8 14 10 14 12 14"
        fill="currentColor"
        opacity={0.8}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.3, duration: 0.4 }}
      />
      <motion.path
        d="M12 14 C14 12 16 12 17 13 C16 14 14 14 12 14"
        fill="currentColor"
        opacity={0.8}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.4, duration: 0.4 }}
      />
      {/* Soil */}
      <path d="M7 20 Q12 21 17 20" stroke="currentColor" strokeWidth="1" fill="none" opacity={0.4} />
    </motion.g>
  );
}

function VegetativeSvg() {
  return (
    <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
      {/* Main stem */}
      <path d="M12 22 L12 8" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      {/* Fan leaves */}
      <motion.path
        d="M12 10 C9 8 6 8 5 10 C7 11 9 11 12 10"
        fill="currentColor"
        opacity={0.7}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2 }}
      />
      <motion.path
        d="M12 10 C15 8 18 8 19 10 C17 11 15 11 12 10"
        fill="currentColor"
        opacity={0.7}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.3 }}
      />
      <motion.path
        d="M12 14 C10 12 7 12 6 14 C8 15 10 15 12 14"
        fill="currentColor"
        opacity={0.6}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.4 }}
      />
      <motion.path
        d="M12 14 C14 12 17 12 18 14 C16 15 14 15 12 14"
        fill="currentColor"
        opacity={0.6}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.5 }}
      />
      {/* Top growth */}
      <motion.path
        d="M12 8 C11 6 10 5 11 4 C12 5 13 5 12 8"
        fill="currentColor"
        opacity={0.8}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1 }}
      />
    </motion.g>
  );
}

function FloweringSvg() {
  return (
    <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
      {/* Main stem */}
      <path d="M12 22 L12 7" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
      {/* Buds/colas */}
      <motion.ellipse
        cx="12" cy="5" rx="3" ry="4"
        fill="currentColor"
        opacity={0.8}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: "spring" }}
      />
      <motion.ellipse
        cx="8" cy="11" rx="2" ry="3"
        fill="currentColor"
        opacity={0.6}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.3, type: "spring" }}
      />
      <motion.ellipse
        cx="16" cy="11" rx="2" ry="3"
        fill="currentColor"
        opacity={0.6}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.4, type: "spring" }}
      />
      {/* Sugar leaves */}
      <path d="M10 13 C8 14 7 16 8 17" stroke="currentColor" strokeWidth="0.8" fill="none" opacity={0.4} />
      <path d="M14 13 C16 14 17 16 16 17" stroke="currentColor" strokeWidth="0.8" fill="none" opacity={0.4} />
    </motion.g>
  );
}

function HarvestSvg() {
  return (
    <motion.g initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5 }}>
      {/* Jar shape */}
      <rect x="7" y="10" width="10" height="11" rx="2" stroke="currentColor" strokeWidth="1.2" fill="none" opacity={0.7} />
      {/* Lid */}
      <rect x="8" y="8" width="8" height="2.5" rx="1" fill="currentColor" opacity={0.6} />
      {/* Buds inside */}
      <circle cx="10" cy="15" r="1.5" fill="currentColor" opacity={0.5} />
      <circle cx="14" cy="14" r="1.5" fill="currentColor" opacity={0.5} />
      <circle cx="12" cy="17" r="1.5" fill="currentColor" opacity={0.5} />
    </motion.g>
  );
}

const STAGE_SVG: Record<GrowStage, () => React.ReactElement> = {
  seed: SeedSvg,
  seedling: SeedlingSvg,
  vegetative: VegetativeSvg,
  flowering: FloweringSvg,
  harvest: HarvestSvg,
};

export function GrowStageIndicator({ stage, dayInStage, className, size = "md" }: GrowStageIndicatorProps) {
  const normalizedStage = STAGE_MAP[stage] || "vegetative";
  const StageSvg = STAGE_SVG[normalizedStage];
  const colorClass = STAGE_COLORS[normalizedStage];

  return (
    <div className={cn("flex flex-col items-center gap-0.5", className)}>
      <div className={cn(SIZE_MAP[size], colorClass)}>
        <svg viewBox="0 0 24 24" className="w-full h-full">
          <StageSvg />
        </svg>
      </div>
      {dayInStage != null && (
        <span className="text-[10px] text-muted-foreground tabular-nums">Day {dayInStage}</span>
      )}
    </div>
  );
}
