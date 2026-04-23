"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Sprout, Warehouse, Cpu, CheckCircle2, ArrowRight } from "lucide-react";

interface OnboardingProps {
  hasTents: boolean;
  hasGrows: boolean;
  hasDevices: boolean;
}

const steps = [
  {
    key: "tent",
    title: "Create a grow space",
    description: "Set up a tent or room where you'll grow.",
    icon: Warehouse,
    href: "/dashboard/tents",
    cta: "Add Space",
    check: (p: OnboardingProps) => p.hasTents,
  },
  {
    key: "grow",
    title: "Start your first grow",
    description: "Track a grow cycle from seed to harvest.",
    icon: Sprout,
    href: "/dashboard/grows",
    cta: "New Grow",
    check: (p: OnboardingProps) => p.hasGrows,
  },
  {
    key: "device",
    title: "Register a device",
    description: "Connect an ESP32 or sensor to monitor conditions.",
    icon: Cpu,
    href: "/dashboard/devices",
    cta: "Add Device",
    check: (p: OnboardingProps) => p.hasDevices,
  },
];

export function OnboardingChecklist(props: OnboardingProps) {
  const completedCount = steps.filter((s) => s.check(props)).length;

  if (completedCount === steps.length) return null; // fully onboarded

  return (
    <Card className="border-primary/20">
      <CardContent className="p-5">
        <div className="flex items-center gap-3 mb-4">
          <Sprout className="size-6 text-primary" />
          <div>
            <h3 className="font-semibold">Welcome to Tendril</h3>
            <p className="text-sm text-muted-foreground">
              {completedCount} of {steps.length} steps complete — let&apos;s get growing.
            </p>
          </div>
        </div>
        <div className="space-y-3">
          {steps.map((step, i) => {
            const done = step.check(props);
            const Icon = step.icon;
            return (
              <motion.div
                key={step.key}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
              >
                <div className={`flex items-center gap-3 rounded-lg border p-3 ${done ? "border-green-500/30 bg-green-500/5" : "border-border"}`}>
                  {done ? (
                    <CheckCircle2 className="size-5 shrink-0 text-green-500" />
                  ) : (
                    <Icon className="size-5 shrink-0 text-muted-foreground" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className={`text-sm font-medium ${done ? "line-through text-muted-foreground" : ""}`}>
                      {step.title}
                    </p>
                    {!done && (
                      <p className="text-xs text-muted-foreground">{step.description}</p>
                    )}
                  </div>
                  {!done && (
                    <Button size="sm" variant="outline" render={<Link href={step.href} />}>
                      {step.cta}
                      <ArrowRight className="ml-1 size-3" />
                    </Button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
