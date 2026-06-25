import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AiActionQueue } from "@/components/ai-action-queue";
import type { AgentActionResponse } from "@/lib/api";

function buildAction(overrides: Partial<AgentActionResponse> = {}): AgentActionResponse {
  return {
    action_type: "control_equipment",
    auto_approved: false,
    conversation_id: null,
    created_at: "2026-06-24T00:00:00Z",
    evidence_json: { recommended_action: "Turn on exhaust fan now", issue_count: 1 },
    execution_json: null,
    grow_cycle_id: "grow-1",
    id: "action-1",
    metadata_json: {
      phase: "health_check",
      health_score: 71,
      issues: ["High humidity"],
      safe_action: false,
    },
    pending_approval: {
      id: "approval-1",
      requested_by_user_id: "user-1",
      reason: "Needs review before sending a control command",
      expires_at: null,
      created_at: "2026-06-24T00:00:00Z",
    },
    proposal: {
      approval: {
        required: true,
        status: "pending",
        reason: "Needs review before sending a control command",
        expires_at: null,
      },
      confidence: null,
      context: {
        phase: "health_check",
        health_score: 71,
        issues: ["High humidity"],
        safe_action: false,
      },
      evidence: {
        recommended_action: "Turn on exhaust fan now",
        issue_count: 1,
      },
      headline: "Turn on exhaust fan now",
      phase: "health_check",
      steps: [
        { key: "observe", label: "Observe", status: "completed", description: "Observed" },
        { key: "plan", label: "Plan", status: "completed", description: "Planned" },
        { key: "approve", label: "Approve", status: "current", description: "Waiting", required: true },
        { key: "execute", label: "Execute", status: "pending", description: "Execute" },
        { key: "verify", label: "Verify", status: "pending", description: "Verify" },
      ],
      summary: "Vent the tent before humidity spikes further.",
      surface: "ai_side_panel",
    },
    requires_approval: true,
    risk_level: "high",
    source: "health_check",
    status: "pending_approval",
    summary: "Vent the tent before humidity spikes further.",
    title: "Turn on exhaust fan now",
    updated_at: "2026-06-24T00:05:00Z",
    verification_json: null,
    ...overrides,
  };
}

describe("AiActionQueue", () => {
  it("renders pending approvals and forwards approve/reject clicks", async () => {
    const user = userEvent.setup();
    const onApprove = vi.fn();
    const onReject = vi.fn();

    render(
      <AiActionQueue
        actions={[buildAction()]}
        liveEvents={[]}
        growName="Flower Tent"
        isLoading={false}
        isRefreshing={false}
        decisionActionId={null}
        onApprove={onApprove}
        onReject={onReject}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Action queue")).toBeInTheDocument();
    expect(screen.getByText("1 awaiting review")).toBeInTheDocument();
    expect(screen.getByText("Needs approval")).toBeInTheDocument();
    expect(screen.getByText("Observed issues")).toBeInTheDocument();
    expect(screen.getByText("High humidity")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Approve" }));
    expect(screen.getByRole("heading", { name: "Approve action" })).toBeInTheDocument();
    await user.type(screen.getByLabelText("Approval note"), "Operator checked the fan plan.");
    await user.click(screen.getByRole("button", { name: "Approve action" }));

    await user.click(screen.getByRole("button", { name: "Reject" }));
    expect(screen.getByRole("heading", { name: "Reject action" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reject action" })).toBeDisabled();
    await user.type(screen.getByLabelText("Reason for rejection"), "Needs a safer airflow target.");
    await user.click(screen.getByRole("button", { name: "Reject action" }));

    expect(onApprove).toHaveBeenCalledWith("action-1", "Operator checked the fan plan.");
    expect(onReject).toHaveBeenCalledWith("action-1", "Needs a safer airflow target.");
  });

  it("shows the empty approval state when no actions are pending", () => {
    const baseProposal = buildAction().proposal;

    render(
      <AiActionQueue
        actions={[
          buildAction({
            id: "action-2",
            execution_json: {
              target: "task",
              tasks_created: 1,
            },
            pending_approval: null,
            proposal: {
              ...baseProposal,
              approval: {
                required: false,
                status: "not_required",
                reason: null,
                expires_at: null,
              },
              evidence: {
                recommended_action: "Adjust pH down",
                issue_count: 1,
              },
              headline: "Adjust pH down",
              steps: [
                { key: "observe", label: "Observe", status: "completed", description: "Observed" },
                { key: "plan", label: "Plan", status: "completed", description: "Planned" },
                { key: "approve", label: "Approve", status: "completed", description: "Auto-approved" },
                { key: "execute", label: "Execute", status: "completed", description: "Executed" },
                { key: "verify", label: "Verify", status: "completed", description: "Verified" },
              ],
              summary: "Create a task to nudge pH back into range.",
            },
            requires_approval: false,
            auto_approved: true,
            action_type: "create_task",
            risk_level: "low",
            status: "verified",
            title: "Adjust pH down",
            summary: "Create a task to nudge pH back into range.",
            verification_json: {
              result: "task_created",
            },
          }),
        ]}
        liveEvents={[]}
        growName="Veg Tent"
        isLoading={false}
        isRefreshing={false}
        decisionActionId={null}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("No approvals waiting right now")).toBeInTheDocument();
    expect(screen.getByText("Recent activity")).toBeInTheDocument();
    expect(screen.getByText("Adjust pH down")).toBeInTheDocument();
    expect(screen.getByText("Verified")).toBeInTheDocument();
    expect(screen.getByText("Execution target:")).toBeInTheDocument();
    expect(screen.getByText("task")).toBeInTheDocument();
    expect(screen.getByText("Verification:")).toBeInTheDocument();
    expect(screen.getByText("task created")).toBeInTheDocument();
    expect(screen.getByText(/Last update /)).toBeInTheDocument();
  });

  it("shows live lifecycle websocket updates", () => {
    render(
      <AiActionQueue
        actions={[]}
        liveEvents={[
          {
            id: "evt-1",
            actionId: "action-1",
            phase: "executing",
            tool: "update_grow_stage",
            message: "Running tool: update grow stage",
            ts: "2026-06-24T00:12:00Z",
          },
          {
            id: "evt-2",
            correlationId: "corr-22",
            phase: "blocked",
            tool: "integration_trigger_sync",
            message: "Tool blocked by policy: integration trigger sync",
            ts: "2026-06-24T00:13:00Z",
            isError: true,
            policy: {
              integration_type: "tuya",
              risk_level: "high",
              requires_simulation: true,
              reason: "Unsupported integration connector: tuya",
            },
          },
        ]}
        growName="Veg Tent"
        isLoading={false}
        isRefreshing={false}
        decisionActionId={null}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Live lifecycle")).toBeInTheDocument();
    expect(screen.getByText("Running tool: update grow stage")).toBeInTheDocument();
    expect(screen.getByText("Tool blocked by policy: integration trigger sync")).toBeInTheDocument();
    expect(screen.getByText("Action action-1")).toBeInTheDocument();
    expect(screen.getByText("Action linked")).toBeInTheDocument();
    expect(screen.getByText("Correlation only")).toBeInTheDocument();
    expect(screen.getByText("Correlation corr-22")).toBeInTheDocument();
    expect(screen.getByText("tuya")).toBeInTheDocument();
    expect(screen.getByText("high risk")).toBeInTheDocument();
    expect(screen.getByText("Simulation required")).toBeInTheDocument();
    expect(screen.getByText("Policy: Unsupported integration connector: tuya")).toBeInTheDocument();
  });

  it("highlights recent activity when live event matches action id", () => {
    render(
      <AiActionQueue
        actions={[buildAction({ status: "executing" })]}
        liveEvents={[
          {
            id: "evt-3",
            actionId: "action-1",
            phase: "executing",
            tool: "update_grow_stage",
            message: "Execution in progress",
            ts: "2026-06-24T00:14:00Z",
          },
        ]}
        growName="Veg Tent"
        isLoading={false}
        isRefreshing={false}
        decisionActionId={null}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Live Executing")).toBeInTheDocument();
    expect(screen.getAllByText("Execution in progress")).toHaveLength(2);
  });

  it("surfaces pending approval live lifecycle events distinctly", () => {
    render(
      <AiActionQueue
        actions={[]}
        liveEvents={[
          {
            id: "evt-4",
            actionId: "action-99",
            phase: "pending_approval",
            tool: "integration_control_command",
            message: "Tool queued for approval: integration control command",
            ts: "2026-06-24T00:15:00Z",
            policy: {
              integration_type: "pulse",
              risk_level: "high",
              requires_simulation: true,
              reason: "High-risk integration control command requires approval and simulation before execution",
            },
          },
        ]}
        growName="Veg Tent"
        isLoading={false}
        isRefreshing={false}
        decisionActionId={null}
        onApprove={vi.fn()}
        onReject={vi.fn()}
        onRefresh={vi.fn()}
      />,
    );

    expect(screen.getByText("Tool queued for approval: integration control command")).toBeInTheDocument();
    expect(screen.getByText("Awaiting approval")).toBeInTheDocument();
    expect(screen.getByText("Pending approval")).toBeInTheDocument();
    expect(screen.getByText("pulse")).toBeInTheDocument();
  });
});
