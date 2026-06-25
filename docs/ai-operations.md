# AI Operations Runbook

This runbook covers Tendril's AI action lifecycle rollout, approval operations, and the current Phase 1 limits for integration control actions.

## 1. Current Behavior Summary

Tendril AI actions move through these lifecycle phases:

| Phase | Meaning |
|------|---------|
| `proposed` | Action record has been created. |
| `pending_approval` | Action is waiting for human review. |
| `approved` | Action was approved and may proceed. |
| `executing` | Action is actively running. |
| `completed` | Execution finished. |
| `verified` | Postcondition was confirmed. |
| `blocked` | Policy or safety rule prevented execution. |
| `failed` | Execution ran but did not succeed. |
| `rejected` | Human reviewer denied the action. |
| `expired` | Approval window elapsed. |
| `cancelled` | Action was explicitly cancelled. |

### Phase 1 integration control constraint

For the current Phase 1 connector set (`pulse`, `openweather`, `ecowitt`):

- integration sync actions can be proposed and lifecycle-tracked
- high-risk outbound control actions can be proposed and queued for approval
- simulation/execution support is **not** implemented yet
- approval for simulation-required integration control commands is intentionally blocked

This is expected behavior, not an outage.

---

## 2. Rollout Checklist

Use this checklist before enabling or upgrading AI lifecycle + integration control flows in an environment.

### Preflight

- Confirm database migrations are applied successfully.
- Confirm `/metrics` is reachable and Prometheus scraping remains healthy.
- Confirm structured JSON logs are enabled in the target environment.
- Confirm the web deployment and API deployment are both on the same release train.
- Confirm AI websocket chat connects and stays alive during long-running responses.
- Confirm at least one tenant admin account exists for approval testing.

### Functional smoke test

- Create a safe AI action and verify it reaches `verified`.
- Create a high-risk integration control action and verify it reaches `pending_approval`.
- Verify the side panel shows `Awaiting approval` for that action.
- Attempt approval and verify the API returns `409` with a simulation/execution support message.
- Verify blocked or pending integration actions appear in action history with connector and operation context.

### Observability checks

- Confirm structured lifecycle logs contain `ai_action_id`, `conversation_id`, `grow_cycle_id`, and `risk_level`.
- Confirm AI lifecycle metrics increment for:
  - proposal creation
  - approval decisions
  - execution success/failure
  - policy blocks
- Confirm no unexpected increase in websocket error events after rollout.

### Release guardrails

- Roll out API before web only if payload changes are additive.
- Roll out web before API only if UI changes tolerate missing lifecycle fields.
- Keep at least one prior API image available for rollback.
- Do not enable any connector execution path until simulation support is implemented for the targeted connector.

---

## 3. Migration Safety Checks

These changes are safe to deploy only if the following conditions hold:

- New action lifecycle fields are additive and existing consumers ignore unknown payload keys.
- Action status transitions remain validated server-side.
- Connectors without control support are never treated as executable.
- Approval routes fail closed when a control action still requires simulation.

### Deployment order

1. Apply database migrations.
2. Deploy API.
3. Verify `/health` and `/metrics`.
4. Deploy web.
5. Run the functional smoke test above.

### What to watch immediately after deploy

- spikes in `blocked` or `failed` action outcomes
- repeated websocket reconnects
- `409` approval errors for actions that should be auto-approved
- missing action cards in the side panel

---

## 4. Backout Procedure

If rollout causes regressions, use this sequence.

### API rollback

1. Roll back the API deployment to the previous image.
2. Keep the database schema in place if the rollback target is compatible with additive fields.
3. Verify `/health`, `/metrics`, and websocket chat startup.

### Web rollback

1. Roll back the web deployment to the previous image.
2. Clear CDN or edge caches if applicable.
3. Verify the side panel still opens and renders action history.

### If approvals are stuck

- Check whether the action is an `integration_control_command` with `requires_simulation=true`.
- If yes, the current `409` approval failure is expected in Phase 1.
- Reject the action with a reviewer note instead of retrying approval.

### If logs or metrics regress

- Confirm `LOG_FORMAT=json` is still set in the API environment.
- Confirm Prometheus still scrapes `/metrics` successfully.
- If logs are malformed, roll back API first; logging is service-side.

---

## 5. Operator Guide

### Reviewing approvals

Use the AI side panel to review pending actions.

#### Safe actions

These may complete without review and appear in recent activity:

- task creation
- journal entry creation
- other safe auto-approved flows already allowed by policy

#### High-risk integration control actions

These appear as pending approvals with integration context:

- connector name/type
- operation (`outbound_control`)
- requested command
- approval reason

In Phase 1, these actions are **informational and reviewable but not executable**.

### Recommended reviewer workflow

1. Confirm the command and connector context make sense.
2. Confirm the action is not a duplicate.
3. If the action is simulation-gated, reject it with a note explaining that connector execution is not enabled yet.
4. If the action is a normal non-control approval, proceed with approve/reject as usual.

---

## 6. Troubleshooting

### "Approve" button is disabled

Expected for integration control actions that still require simulation support.

Check the action card for the message:

> Simulation support is required before this command can be approved.

### Approval API returns 409

This is expected when:

- the action has no pending approval
- the action was already reviewed
- the action is an integration control command that cannot be approved until execution support exists

### Action is blocked immediately

Likely causes:

- unsupported connector type
- policy deny for the requested operation
- high-risk command routed through a non-executable connector path

Inspect:

- action history in the side panel
- structured API logs for `ai_action_lifecycle`
- metrics for policy block increments

### Action never appears in the queue

Check:

- websocket connectivity
- API action list response
- tenant scoping and current grow selection
- browser console for side-panel fetch failures

### Metrics do not move

Check:

- `/metrics` exposure on the API service
- Prometheus target health
- whether the tested flow actually crossed the expected lifecycle edge

---

## 7. When to Escalate

Escalate to engineering when:

- a safe non-control action is incorrectly blocked
- an integration control action executes despite the Phase 1 non-execution rule
- action lifecycle records are missing IDs or correlation fields
- websocket lifecycle events disagree with persisted action status
- approval actions succeed but no audit trail, logs, or metrics are emitted
