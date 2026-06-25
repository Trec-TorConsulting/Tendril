"use client";

import { useMemo, useState } from "react";

import { AlertTriangle, CheckCircle2, Clock3, Loader2, RefreshCw, ShieldAlert, ShieldCheck } from "lucide-react";

import type { AgentActionResponse } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { cn, formatShortDateTime, formatTime } from "@/lib/utils";

export interface ActionLifecycleEvent {
  id: string;
  actionId?: string;
  correlationId?: string;
  phase: string;
  tool?: string;
  message: string;
  ts: string;
  isError?: boolean;
  policy?: {
    integration_type?: string;
    operation?: string;
    supported?: boolean;
    allowed?: boolean;
    risk_level?: string;
    requires_approval?: boolean;
    requires_simulation?: boolean;
    reason?: string | null;
  };
}

interface AiActionQueueProps {
  actions: AgentActionResponse[];
  liveEvents: ActionLifecycleEvent[];
  growName?: string;
  isLoading: boolean;
  isRefreshing: boolean;
  decisionActionId: string | null;
  onApprove: (actionId: string, reason?: string) => void;
  onReject: (actionId: string, reason?: string) => void;
  onRefresh: () => void;
}

type DecisionMode = "approve" | "reject";

interface DecisionDialogState {
  actionId: string;
  mode: DecisionMode;
}

const STATUS_LABELS: Record<string, string> = {
  pending_approval: "Pending approval",
  approved: "Approved",
  executing: "Executing",
  completed: "Completed",
  verified: "Verified",
  rejected: "Rejected",
  failed: "Failed",
  blocked: "Blocked",
  proposed: "Proposed",
};

const STEP_STATUS_STYLES: Record<string, string> = {
  completed: "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  current: "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300",
  pending: "border-border bg-background text-muted-foreground",
  skipped: "border-border bg-muted/40 text-muted-foreground",
  blocked: "border-destructive/30 bg-destructive/10 text-destructive",
  failed: "border-destructive/30 bg-destructive/10 text-destructive",
};

function statusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  if (status === "verified") return "default";
  if (status === "pending_approval" || status === "executing" || status === "approved") return "secondary";
  if (status === "rejected" || status === "failed" || status === "blocked") return "destructive";
  return "outline";
}

function liveEventContainerClass(event: ActionLifecycleEvent) {
  if (event.phase === "pending_approval") {
    return "border-amber-500/30 bg-amber-500/10";
  }
  if (event.isError) {
    return "border-destructive/30 bg-destructive/10";
  }
  return "border-border/70 bg-background/80";
}

function statusLabel(status: string) {
  return STATUS_LABELS[status] ?? status.replace(/_/g, " ");
}

function formatContextIssues(action: AgentActionResponse) {
  const issues = action.proposal.context?.issues;
  if (!Array.isArray(issues)) {
    return [];
  }
  return issues.filter((value): value is string => typeof value === "string");
}

function formatEvidence(action: AgentActionResponse) {
  const recommended = action.proposal.evidence?.recommended_action;
  return typeof recommended === "string" && recommended.trim() ? recommended : action.title;
}

function readProposalString(record: Record<string, unknown> | null | undefined, key: string) {
  const value = record?.[key];
  return typeof value === "string" && value.trim() ? value : null;
}

function readProposalBoolean(record: Record<string, unknown> | null | undefined, key: string) {
  const value = record?.[key];
  return typeof value === "boolean" ? value : false;
}

function buildIntegrationSummary(action: AgentActionResponse) {
  const context = action.proposal.context;
  const integrationName = readProposalString(context, "integration_name");
  const integrationType = readProposalString(context, "integration_type");
  const operation = readProposalString(context, "operation");
  const command = readProposalString(context, "command");
  const parts = [integrationName ?? integrationType, operation?.replace(/_/g, " "), command].filter(
    (value): value is string => Boolean(value),
  );

  if (parts.length === 0) {
    return null;
  }
  return parts;
}

function readRecordString(record: Record<string, unknown> | null | undefined, key: string) {
  const value = record?.[key];
  return typeof value === "string" && value.trim() ? value : null;
}

function formatLifecycleValue(value: string) {
  return value.replace(/_/g, " ");
}

function buildRecentActivityDetails(action: AgentActionResponse) {
  const details: Array<{ label: string; value: string }> = [];
  const approvalReason = action.pending_approval?.reason || action.proposal.approval?.reason || null;
  const executionTarget = readRecordString(action.execution_json, "target");
  const executionError = readRecordString(action.execution_json, "error");
  const verificationResult =
    readRecordString(action.verification_json, "result") ||
    readRecordString(action.verification_json, "status") ||
    readRecordString(action.verification_json, "message");

  if ((action.status === "pending_approval" || action.status === "blocked") && approvalReason) {
    details.push({
      label: action.status === "blocked" ? "Blocked by" : "Approval gate",
      value: approvalReason,
    });
  }

  if (action.status === "rejected" && approvalReason) {
    details.push({ label: "Rejected because", value: approvalReason });
  }

  if (executionError) {
    details.push({ label: "Execution issue", value: executionError });
  } else if (executionTarget) {
    details.push({ label: "Execution target", value: formatLifecycleValue(executionTarget) });
  }

  if (verificationResult) {
    details.push({ label: "Verification", value: formatLifecycleValue(verificationResult) });
  } else if (action.status === "verified") {
    details.push({ label: "Verification", value: "Outcome confirmed" });
  }

  if (details.length === 0 && action.summary) {
    details.push({ label: "Summary", value: action.summary });
  }

  const integrationSummary = buildIntegrationSummary(action);
  if (integrationSummary) {
    details.unshift({ label: "Integration", value: integrationSummary.join(" • ") });
  }

  return details.slice(0, 3);
}

export function AiActionQueue({
  actions,
  liveEvents,
  growName,
  isLoading,
  isRefreshing,
  decisionActionId,
  onApprove,
  onReject,
  onRefresh,
}: AiActionQueueProps) {
  const [decisionDialog, setDecisionDialog] = useState<DecisionDialogState | null>(null);
  const [decisionReason, setDecisionReason] = useState("");
  const pendingActions = actions.filter((action) => action.status === "pending_approval");
  const recentActions = actions.slice(0, 6);
  const decisionAction = useMemo(
    () => pendingActions.find((action) => action.id === decisionDialog?.actionId) ?? null,
    [decisionDialog?.actionId, pendingActions],
  );
  const latestLiveByActionId = useMemo(() => {
    const map = new Map<string, ActionLifecycleEvent>();
    for (const event of liveEvents) {
      if (!event.actionId) {
        continue;
      }
      if (!map.has(event.actionId)) {
        map.set(event.actionId, event);
      }
    }
    return map;
  }, [liveEvents]);
  const isRejectDecision = decisionDialog?.mode === "reject";
  const decisionDialogBusy = decisionActionId === decisionDialog?.actionId;

  function openDecisionDialog(actionId: string, mode: DecisionMode) {
    setDecisionDialog({ actionId, mode });
    setDecisionReason("");
  }

  function closeDecisionDialog() {
    if (decisionDialogBusy) {
      return;
    }
    setDecisionDialog(null);
    setDecisionReason("");
  }

  function submitDecision() {
    if (!decisionDialog) {
      return;
    }

    const { actionId, mode } = decisionDialog;
    const trimmedReason = decisionReason.trim();
    setDecisionDialog(null);
    setDecisionReason("");

    if (mode === "reject") {
      onReject(actionId, trimmedReason);
      return;
    }
    onApprove(actionId, trimmedReason || undefined);
  }

  return (
    <>
      <div className="border-b bg-linear-to-b from-primary/5 via-background to-background px-4 py-3">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <ShieldCheck className="size-4 text-primary" />
              <p className="text-sm font-semibold">Action queue</p>
              <Badge variant={pendingActions.length > 0 ? "secondary" : "outline"}>
                {pendingActions.length} awaiting review
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {growName ? `Approvals and lifecycle history for ${growName}.` : "Approvals and lifecycle history."}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 px-2 text-xs"
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={cn("size-3.5", isRefreshing && "animate-spin")} />
            Refresh
          </Button>
        </div>

        <ScrollArea className="mt-3 max-h-72">
          <div className="space-y-3 pr-3">
            {isLoading ? (
              <Card size="sm" className="border border-dashed border-border/80 bg-background/70">
                <CardContent className="flex items-center gap-2 py-4 text-xs text-muted-foreground">
                  <Loader2 className="size-4 animate-spin" />
                  Loading action proposals...
                </CardContent>
              </Card>
            ) : null}

            {!isLoading && pendingActions.length === 0 ? (
              <Card size="sm" className="border border-dashed border-border/80 bg-background/70">
                <CardContent className="flex items-start gap-2 py-4 text-xs text-muted-foreground">
                  <CheckCircle2 className="mt-0.5 size-4 text-emerald-600 dark:text-emerald-400" />
                  <div>
                    <p className="font-medium text-foreground">No approvals waiting right now</p>
                    <p className="mt-1">Safe actions will auto-verify here, and higher-risk proposals will appear when review is needed.</p>
                  </div>
                </CardContent>
              </Card>
            ) : null}

            {pendingActions.length > 0 ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  <ShieldAlert className="size-3.5" />
                  Needs approval
                </div>
                {pendingActions.map((action) => {
                  const issues = formatContextIssues(action);
                  const integrationSummary = buildIntegrationSummary(action);
                  const requiresSimulation = readProposalBoolean(action.proposal.context, "requires_simulation");
                  const isBusy = decisionActionId === action.id;

                  return (
                    <Card key={action.id} size="sm" className="border border-amber-500/20 bg-amber-500/5">
                      <CardHeader className="pb-1">
                        <div className="flex items-start justify-between gap-3">
                          <div className="space-y-1">
                            <CardTitle className="text-sm">{action.proposal.headline}</CardTitle>
                            <p className="text-xs text-muted-foreground">{action.proposal.summary || formatEvidence(action)}</p>
                          </div>
                          <Badge variant="secondary">{statusLabel(action.status)}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3 pt-0">
                        <div className="flex flex-wrap gap-1.5 text-[11px]">
                          <Badge variant="outline">{action.action_type.replace(/_/g, " ")}</Badge>
                          <Badge variant={action.risk_level === "high" ? "destructive" : "outline"}>{action.risk_level} risk</Badge>
                          {action.proposal.phase ? <Badge variant="outline">{action.proposal.phase}</Badge> : null}
                        </div>

                        {issues.length > 0 ? (
                          <div className="rounded-lg bg-background/80 px-3 py-2 text-xs text-muted-foreground">
                            <p className="font-medium text-foreground">Observed issues</p>
                            <p className="mt-1">{issues.join(" • ")}</p>
                          </div>
                        ) : null}

                        {integrationSummary ? (
                          <div className="rounded-lg bg-background/80 px-3 py-2 text-xs text-muted-foreground">
                            <p className="font-medium text-foreground">Integration command</p>
                            <p className="mt-1">{integrationSummary.join(" • ")}</p>
                            {requiresSimulation ? (
                              <p className="mt-1 text-amber-700 dark:text-amber-300">
                                Simulation support is required before this command can be approved.
                              </p>
                            ) : null}
                          </div>
                        ) : null}

                        <div className="flex flex-wrap gap-1.5">
                          {action.proposal.steps.map((step) => (
                            <span
                              key={`${action.id}-${step.key}`}
                              className={cn(
                                "rounded-full border px-2 py-1 text-[10px] font-medium",
                                STEP_STATUS_STYLES[step.status] ?? STEP_STATUS_STYLES.pending,
                              )}
                            >
                              {step.label}
                            </span>
                          ))}
                        </div>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            className="flex-1"
                            disabled={isBusy || requiresSimulation}
                            onClick={() => openDecisionDialog(action.id, "approve")}
                          >
                            {isBusy ? <Loader2 className="size-3.5 animate-spin" /> : <ShieldCheck className="size-3.5" />}
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            className="flex-1"
                            disabled={isBusy}
                            onClick={() => openDecisionDialog(action.id, "reject")}
                          >
                            {isBusy ? <Loader2 className="size-3.5 animate-spin" /> : <AlertTriangle className="size-3.5" />}
                            Reject
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : null}

            {liveEvents.length > 0 ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  <Loader2 className="size-3.5" />
                  Live lifecycle
                </div>
                {liveEvents.map((event) => (
                  <div
                    key={event.id}
                    className={cn(
                      "rounded-xl border px-3 py-2",
                      liveEventContainerClass(event),
                    )}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs font-medium text-foreground">{event.message}</p>
                      <div className="flex items-center gap-1.5">
                        {event.phase === "pending_approval" ? <Badge variant="secondary">Awaiting approval</Badge> : null}
                        {event.actionId ? <Badge variant="secondary">Action linked</Badge> : null}
                        {!event.actionId && event.correlationId ? <Badge variant="outline">Correlation only</Badge> : null}
                        <Badge
                          variant={
                            event.phase === "pending_approval"
                              ? "secondary"
                              : event.isError
                                ? "destructive"
                                : "outline"
                          }
                        >
                          {statusLabel(event.phase)}
                        </Badge>
                      </div>
                    </div>
                    <p className="mt-1 text-[11px] text-muted-foreground">
                      {event.tool ? `${event.tool.replace(/_/g, " ")} • ` : ""}
                      {formatTime(event.ts)}
                    </p>
                    {event.policy ? (
                      <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-[11px]">
                        {event.policy.integration_type ? (
                          <Badge variant="outline">{event.policy.integration_type}</Badge>
                        ) : null}
                        {event.policy.risk_level ? (
                          <Badge variant={event.policy.risk_level === "high" ? "destructive" : "outline"}>
                            {event.policy.risk_level} risk
                          </Badge>
                        ) : null}
                        {event.policy.requires_simulation ? (
                          <Badge variant="secondary">Simulation required</Badge>
                        ) : null}
                      </div>
                    ) : null}
                    {event.policy?.reason ? (
                      <p className="mt-1 text-[11px] text-muted-foreground">Policy: {event.policy.reason}</p>
                    ) : null}
                    {event.actionId ? (
                      <p className="mt-1 text-[11px] text-muted-foreground">Action {event.actionId}</p>
                    ) : null}
                    {!event.actionId && event.correlationId ? (
                      <p className="mt-1 text-[11px] text-muted-foreground">Correlation {event.correlationId}</p>
                    ) : null}
                  </div>
                ))}
              </div>
            ) : null}

            {recentActions.length > 0 ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                  <Clock3 className="size-3.5" />
                  Recent activity
                </div>
                {recentActions.map((action) => {
                  const liveEvent = latestLiveByActionId.get(action.id);

                  return (
                    <div
                      key={`recent-${action.id}`}
                      className="rounded-xl border border-border/70 bg-background/80 px-3 py-3"
                    >
                      {liveEvent ? (
                        <div className="mb-2 flex items-center gap-2 text-[11px]">
                          <Badge variant="secondary">Live {statusLabel(liveEvent.phase)}</Badge>
                          <span className="text-muted-foreground">{liveEvent.message}</span>
                        </div>
                      ) : null}
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-xs font-medium text-foreground">{action.proposal.headline}</p>
                        <Badge variant={statusVariant(action.status)}>{statusLabel(action.status)}</Badge>
                      </div>
                      <p className="mt-1 text-[11px] text-muted-foreground">{action.proposal.summary || formatEvidence(action)}</p>

                      <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
                        <Badge variant="outline">{action.action_type.replace(/_/g, " ")}</Badge>
                        <Badge variant={action.risk_level === "high" ? "destructive" : "outline"}>{action.risk_level} risk</Badge>
                        <span className="rounded-full border border-border bg-muted/40 px-2 py-1 text-[10px] text-muted-foreground">
                          Last update {formatShortDateTime(action.updated_at)}
                        </span>
                      </div>

                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {action.proposal.steps.map((step) => (
                          <span
                            key={`recent-${action.id}-${step.key}`}
                            className={cn(
                              "rounded-full border px-2 py-1 text-[10px] font-medium",
                              STEP_STATUS_STYLES[step.status] ?? STEP_STATUS_STYLES.pending,
                            )}
                          >
                            {step.label}
                          </span>
                        ))}
                      </div>

                      <div className="mt-2 space-y-1.5">
                        {buildRecentActivityDetails(action).map((detail) => (
                          <div key={`${action.id}-${detail.label}`} className="flex flex-wrap items-start gap-1.5 text-[11px]">
                            <span className="font-medium text-foreground">{detail.label}:</span>
                            <span className="text-muted-foreground">{detail.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
        </ScrollArea>
      </div>

      <Dialog open={decisionDialog !== null} onOpenChange={(open) => !open && closeDecisionDialog()}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{isRejectDecision ? "Reject action" : "Approve action"}</DialogTitle>
            <DialogDescription>
              {isRejectDecision
                ? `Add a reason so the grow team understands why ${decisionAction?.proposal.headline ?? "this action"} was blocked.`
                : `Optionally add context for approving ${decisionAction?.proposal.headline ?? "this action"}.`}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-2">
            <label htmlFor="ai-action-reason" className="text-xs font-medium text-foreground">
              {isRejectDecision ? "Reason for rejection" : "Approval note"}
            </label>
            <Textarea
              id="ai-action-reason"
              value={decisionReason}
              onChange={(event) => setDecisionReason(event.target.value)}
              placeholder={
                isRejectDecision
                  ? "Explain what should change before this can run."
                  : "Optional note for the audit trail."
              }
              className="min-h-24"
              disabled={decisionDialogBusy}
            />
            {isRejectDecision ? (
              <p className="text-[11px] text-muted-foreground">A rejection reason is required so the action can be revised.</p>
            ) : (
              <p className="text-[11px] text-muted-foreground">Leave blank to approve without an extra note.</p>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={closeDecisionDialog} disabled={decisionDialogBusy}>
              Cancel
            </Button>
            <Button
              variant={isRejectDecision ? "destructive" : "default"}
              onClick={submitDecision}
              disabled={decisionDialogBusy || !decisionDialog || (isRejectDecision && !decisionReason.trim())}
            >
              {decisionDialogBusy ? <Loader2 className="size-3.5 animate-spin" /> : null}
              {isRejectDecision ? "Reject action" : "Approve action"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}