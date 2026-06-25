import { test, expect, login, TEST_USERS } from "./helpers";

function paginated<T>(items: T[]) {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: items.length || 1,
    total_pages: 1,
  };
}

function buildAction(overrides: Record<string, unknown> = {}) {
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

test.describe("AI lifecycle browser coverage", () => {
  test("AI drawer shows safe task and checklist lifecycle details", async ({ page }) => {
    await page.route("**/v1/grows**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          paginated([
            {
              id: "grow-1",
              tent_id: "tent-1",
              name: "QA Flower Tent",
              grow_type: "DWC",
              status: "active",
              stage: "flowering",
              started_at: "2026-06-01T00:00:00Z",
              ended_at: null,
              notes: null,
              milestones: null,
              settings: null,
              auto_health_check: false,
            },
          ]),
        ),
      });
    });

    await page.route("**/v1/ai/actions**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          paginated([
            buildAction({
              id: "action-task",
              action_type: "create_task",
              auto_approved: true,
              requires_approval: false,
              risk_level: "low",
              status: "verified",
              title: "Adjust pH down",
              summary: "Create a task to nudge pH back into range.",
              pending_approval: null,
              execution_json: {
                target: "task",
                task_id: "task-42",
                tasks_created: 1,
              },
              verification_json: {
                result: "task_created",
              },
              proposal: {
                ...buildAction().proposal,
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
            }),
            buildAction({
              id: "action-checklist",
              action_type: "generate_checklist",
              auto_approved: true,
              requires_approval: false,
              risk_level: "low",
              status: "verified",
              title: "Generate checklist: Pre-flip prep",
              summary: "Pre-flip prep (3 items)",
              pending_approval: null,
              evidence_json: {
                checklist_title: "Pre-flip prep",
                items: ["Inspect trellis anchors", "Top off reservoir", "Document canopy height"],
              },
              execution_json: {
                target: "checklist",
                task_count: 3,
              },
              verification_json: {
                result: "checklist_created",
                checklist_title: "Pre-flip prep",
                task_count: 3,
              },
              proposal: {
                ...buildAction().proposal,
                approval: {
                  required: false,
                  status: "not_required",
                  reason: null,
                  expires_at: null,
                },
                headline: "Generate checklist: Pre-flip prep",
                summary: "Turn a prep checklist into actionable tasks.",
                steps: [
                  { key: "observe", label: "Observe", status: "completed", description: "Observed" },
                  { key: "plan", label: "Plan", status: "completed", description: "Planned" },
                  { key: "approve", label: "Approve", status: "completed", description: "Auto-approved" },
                  { key: "execute", label: "Execute", status: "completed", description: "Executed" },
                  { key: "verify", label: "Verify", status: "completed", description: "Verified" },
                ],
              },
            }),
          ]),
        ),
      });
    });

    await page.route("**/v1/conversations**", async (route) => {
      const url = new URL(route.request().url());
      const isDetail = /\/v1\/conversations\/[A-Za-z0-9-]+$/.test(url.pathname);
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          isDetail
            ? {
                id: "conversation-1",
                grow_cycle_id: "grow-1",
                title: "QA conversation",
                message_count: 0,
                created_at: "2026-06-24T00:00:00Z",
                updated_at: "2026-06-24T00:00:00Z",
                messages: [],
              }
            : paginated([]),
        ),
      });
    });

    await page.addInitScript(() => {
      window.localStorage.setItem("tendril_onboarding_seen", "true");
    });

    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/ai");
    await expect(page).toHaveURL(/\/dashboard\/ai/);

    await expect(page.getByText("Action queue")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("No approvals waiting right now")).toBeVisible();
    await expect(page.getByText("Recent activity")).toBeVisible();
    await expect(page.getByText("Adjust pH down")).toBeVisible();
    await expect(page.getByText("Task created:")).toBeVisible();
    await expect(page.getByText("task-42")).toBeVisible();
    await expect(page.getByText("task created", { exact: true })).toBeVisible();
    await expect(page.getByText("Generate checklist: Pre-flip prep")).toBeVisible();
    await expect(page.getByText("Checklist:", { exact: true })).toBeVisible();
    await expect(page.getByText("Pre-flip prep • 3 tasks")).toBeVisible();
    await expect(page.getByText("checklist created", { exact: true })).toBeVisible();
  });

  test("notifications page renders AI lifecycle feed entries", async ({ page }) => {
    await page.route("**/v1/notifications/channels**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(paginated([])),
      });
    });

    await page.route("**/v1/notifications/preferences**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(paginated([])),
      });
    });

    await page.route("**/v1/notifications/logs**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          paginated([
            {
              id: "log-verified",
              channel_type: "in_app",
              event_type: "ai_action_lifecycle",
              severity: "info",
              subject: "AI verified reservoir correction checklist",
              body: "Checklist completed and verified for Flower Tent.",
              status: "sent",
              error: null,
              created_at: "2026-06-24T00:22:00Z",
            },
            {
              id: "log-blocked",
              channel_type: "in_app",
              event_type: "ai_action_lifecycle",
              severity: "warning",
              subject: "AI blocked dosing command",
              body: "Simulation required before sending nutrient dose.",
              status: "sent",
              error: null,
              created_at: "2026-06-24T00:20:00Z",
            },
          ]),
        ),
      });
    });

    await page.addInitScript(() => {
      window.localStorage.setItem("tendril_onboarding_seen", "true");
    });

    await login(page, TEST_USERS.standard.email, TEST_USERS.standard.password);
    await page.goto("/dashboard/notifications");
    await expect(page).toHaveURL(/\/dashboard\/notifications/);

    await expect(page.getByText("AI Lifecycle Feed")).toBeVisible({ timeout: 15000 });
    await expect(page.getByText("AI verified reservoir correction checklist")).toBeVisible();
    await expect(page.getByText("Checklist completed and verified for Flower Tent.")).toBeVisible();
    await expect(page.getByText("AI blocked dosing command")).toBeVisible();
    await expect(page.getByText("Simulation required before sending nutrient dose.")).toBeVisible();
  });
});
