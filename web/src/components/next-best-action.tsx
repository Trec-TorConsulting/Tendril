import Link from "next/link";
import type { ReactNode } from "react";
import { AlertTriangle, Bot, CheckCircle2, ClipboardCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { TaskItem } from "@/lib/api";

type NextAction = {
  title: string;
  detail: string;
  href: string;
  cta: string;
  tone: "critical" | "warning" | "normal";
  icon: ReactNode;
};

export function NextBestAction({
  growId,
  growStage,
  tasks,
  healthScore,
}: {
  growId: string;
  growStage?: string;
  tasks: TaskItem[];
  healthScore: number | null;
}) {
  const action = selectNextAction(growId, growStage, tasks, healthScore);

  const toneClass =
    action.tone === "critical"
      ? "border-destructive/40 bg-destructive/5"
      : action.tone === "warning"
        ? "border-amber-500/40 bg-amber-500/5"
        : "border-primary/30 bg-primary/5";

  return (
    <Card className={toneClass}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          {action.icon}
          Next Best Action
        </CardTitle>
      </CardHeader>
      <CardContent className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium">{action.title}</p>
          <p className="text-xs text-muted-foreground">{action.detail}</p>
        </div>
        <Button size="sm" render={<Link href={action.href} />}>
          {action.cta}
        </Button>
      </CardContent>
    </Card>
  );
}

function selectNextAction(
  growId: string,
  growStage: string | undefined,
  tasks: TaskItem[],
  healthScore: number | null,
): NextAction {
  const criticalTask = tasks.find(
    (task) => task.category === "alert_response" || task.priority === "urgent",
  );
  if (criticalTask) {
    return {
      title: criticalTask.title,
      detail: "An alert-driven task needs immediate attention.",
      href: "/dashboard/tasks",
      cta: "Resolve",
      tone: "critical",
      icon: <AlertTriangle className="size-4 text-destructive" />,
    };
  }

  if (healthScore != null && healthScore < 50) {
    return {
      title: "Run a new health check",
      detail: "Recent health score is low. Re-check and create targeted actions.",
      href: `/dashboard/grows/${growId}`,
      cta: "Open Health",
      tone: "warning",
      icon: <Bot className="size-4 text-amber-500" />,
    };
  }

  if (growStage && ["flowering", "ripening", "harvesting"].includes(growStage)) {
    return {
      title: "Review harvest guidance",
      detail: "You are in a harvest-relevant stage. Validate timing and nutrient strategy.",
      href: `/dashboard/grows/${growId}`,
      cta: "Review",
      tone: "normal",
      icon: <ClipboardCheck className="size-4 text-primary" />,
    };
  }

  return {
    title: "Log today's grow activity",
    detail: "A quick log keeps AI advice and trend analysis accurate.",
    href: "/dashboard/quick-log",
    cta: "Quick Log",
    tone: "normal",
    icon: <CheckCircle2 className="size-4 text-primary" />,
  };
}
