"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { getAccessToken } from "@/lib/auth";
import { updateProfile } from "@/lib/api";
import { useUser } from "@/hooks/use-user";
import type { LayoutMode } from "@/lib/layout-config";
import { LAYOUT_CONFIGS } from "@/lib/layout-config";
import { GuidedTentSetupDialog } from "@/components/guided-tent-setup-dialog";
import { Sprout, Sun, Home, Warehouse, ArrowRight, Check } from "lucide-react";

interface OnboardingWizardProps {
  onComplete: () => void;
}

type GrowingType = "indoor" | "outdoor" | "both";
type GrowCount = "1" | "2-5" | "6-20" | "20+";
type Experience = "first" | "hobbyist" | "experienced" | "professional" | "commercial";

function determineMode(growCount: GrowCount, experience: Experience): LayoutMode {
  if (experience === "first") return "beginner";
  if (experience === "commercial") return "commercial";
  if (experience === "professional") return "pro";
  if (experience === "experienced") {
    return growCount === "1" || growCount === "2-5" ? "standard" : "pro";
  }
  // hobbyist
  return growCount === "1" || growCount === "2-5" ? "home" : "standard";
}

export function OnboardingWizard({ onComplete }: OnboardingWizardProps) {
  const { refresh } = useUser();
  const [step, setStep] = useState(0);
  const [growingType, setGrowingType] = useState<GrowingType | null>(null);
  const [growCount, setGrowCount] = useState<GrowCount | null>(null);
  const [experience, setExperience] = useState<Experience | null>(null);
  const [saving, setSaving] = useState(false);
  const [showGuidedSetup, setShowGuidedSetup] = useState(false);

  const handleComplete = useCallback(async () => {
    if (!growCount || !experience) return;
    const mode = determineMode(growCount, experience);

    setSaving(true);
    try {
      const token = getAccessToken();
      if (token) {
        // Persist the chosen persona AND mark onboarding complete server-side so
        // it never re-triggers on another browser or device. Preferences merge
        // on the API, so this preserves any other preference keys.
        await updateProfile(token, { layout_mode: mode, preferences: { show_onboarding: false } });
        await refresh();
      }
    } catch {
      // Non-fatal: the local "seen" flag set by onComplete still prevents the
      // wizard from reappearing on this device.
    } finally {
      setSaving(false);
      // Always finish — never leave the user stuck on the wizard.
      onComplete();
    }
  }, [growCount, experience, refresh, onComplete]);

  const selectedMode = growCount && experience ? determineMode(growCount, experience) : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-8">
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className={cn(
                "size-2 rounded-full transition-colors",
                i <= step ? "bg-primary" : "bg-muted",
              )}
            />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 0 && (
            <WizardStep key="step0" title="What are you growing?">
              <div className="grid gap-3">
                <OptionCard
                  icon={<Warehouse className="size-6" />}
                  label="Indoor"
                  description="Tents, grow rooms, closets"
                  selected={growingType === "indoor"}
                  onClick={() => setGrowingType("indoor")}
                />
                <OptionCard
                  icon={<Sun className="size-6" />}
                  label="Outdoor"
                  description="Garden beds, greenhouses"
                  selected={growingType === "outdoor"}
                  onClick={() => setGrowingType("outdoor")}
                />
                <OptionCard
                  icon={<Home className="size-6" />}
                  label="Both"
                  description="Indoor and outdoor grows"
                  selected={growingType === "both"}
                  onClick={() => setGrowingType("both")}
                />
              </div>
              <Button
                className="w-full mt-6"
                disabled={!growingType}
                onClick={() => setStep(1)}
              >
                Next <ArrowRight className="size-4 ml-1" />
              </Button>
            </WizardStep>
          )}

          {step === 1 && (
            <WizardStep key="step1" title="How many grows do you run?">
              <div className="grid grid-cols-2 gap-3">
                {([
                  { value: "1" as const, label: "Just 1", desc: "Single tent or space" },
                  { value: "2-5" as const, label: "2–5", desc: "A few spaces" },
                  { value: "6-20" as const, label: "6–20", desc: "Multiple rooms" },
                  { value: "20+" as const, label: "20+", desc: "Commercial scale" },
                ]).map((opt) => (
                  <OptionCard
                    key={opt.value}
                    icon={<span className="text-xl font-bold">{opt.value}</span>}
                    label={opt.label}
                    description={opt.desc}
                    selected={growCount === opt.value}
                    onClick={() => setGrowCount(opt.value)}
                  />
                ))}
              </div>
              <div className="flex gap-3 mt-6">
                <Button variant="outline" className="flex-1" onClick={() => setStep(0)}>Back</Button>
                <Button className="flex-1" disabled={!growCount} onClick={() => setStep(2)}>
                  Next <ArrowRight className="size-4 ml-1" />
                </Button>
              </div>
            </WizardStep>
          )}

          {step === 2 && (
            <WizardStep key="step2" title="Experience level?">
              <div className="grid gap-3">
                {([
                  { value: "first" as const, label: "First grow", desc: "Never grown before" },
                  { value: "hobbyist" as const, label: "Hobbyist", desc: "A few grows under my belt" },
                  { value: "experienced" as const, label: "Experienced", desc: "I know my way around" },
                  { value: "professional" as const, label: "Professional", desc: "This is my livelihood" },
                  { value: "commercial" as const, label: "Commercial", desc: "Managing a team" },
                ]).map((opt) => (
                  <OptionCard
                    key={opt.value}
                    icon={<Sprout className="size-5" />}
                    label={opt.label}
                    description={opt.desc}
                    selected={experience === opt.value}
                    onClick={() => setExperience(opt.value)}
                    compact
                  />
                ))}
              </div>
              <div className="flex gap-3 mt-6">
                <Button variant="outline" className="flex-1" onClick={() => setStep(1)}>Back</Button>
                <Button className="flex-1" disabled={!experience} onClick={() => setStep(3)}>
                  Next <ArrowRight className="size-4 ml-1" />
                </Button>
              </div>
            </WizardStep>
          )}

          {step === 3 && selectedMode && (
            <WizardStep key="step3" title="You're all set!">
              <Card className="border-primary">
                <CardContent className="p-6 text-center space-y-2">
                  <div className="flex size-12 items-center justify-center rounded-full bg-primary/10 text-primary mx-auto">
                    <Check className="size-6" />
                  </div>
                  <h3 className="text-lg font-semibold">{LAYOUT_CONFIGS[selectedMode].label} Mode</h3>
                  <p className="text-sm text-muted-foreground">{LAYOUT_CONFIGS[selectedMode].description}</p>
                </CardContent>
              </Card>
              <p className="text-xs text-center text-muted-foreground mt-4">
                You can change your layout mode anytime in Settings.
              </p>
              <div className="flex gap-3 mt-6">
                <Button variant="outline" className="flex-1" onClick={() => setStep(2)}>Back</Button>
                <Button variant="outline" className="flex-1" onClick={() => setShowGuidedSetup(true)}>
                  Guided Setup
                </Button>
                <Button className="flex-1" disabled={saving} onClick={handleComplete}>
                  {saving ? "Saving..." : "Get Started"}
                </Button>
              </div>
            </WizardStep>
          )}
        </AnimatePresence>

        <GuidedTentSetupDialog
          open={showGuidedSetup}
          onOpenChange={setShowGuidedSetup}
          source="onboarding"
          onCompleted={() => {
            // No-op for onboarding; user can continue onboarding flow.
          }}
        />
      </div>
    </div>
  );
}

function WizardStep({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
    >
      <h2 className="text-xl font-semibold text-center mb-6">{title}</h2>
      {children}
    </motion.div>
  );
}

function OptionCard({
  icon,
  label,
  description,
  selected,
  onClick,
  compact,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  selected: boolean;
  onClick: () => void;
  compact?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 rounded-xl border p-4 text-left transition-all",
        compact && "p-3",
        selected
          ? "border-primary bg-primary/5 ring-1 ring-primary"
          : "border-border hover:border-primary/50 hover:bg-muted/50",
      )}
    >
      <div className={cn(
        "flex shrink-0 items-center justify-center rounded-lg",
        selected ? "text-primary" : "text-muted-foreground",
        compact ? "size-8" : "size-10 bg-muted",
      )}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium">{label}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </button>
  );
}
