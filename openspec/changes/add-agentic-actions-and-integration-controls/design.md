## Context
Tendril is evolving from conversational recommendations toward action-oriented automation across grow resources and integrations. This introduces higher risk: incorrect writes, unsafe external commands, and reduced user trust without explicit controls.

## Goals / Non-Goals
- Goals:
  - Introduce a consistent agent runtime contract for all actionable AI flows.
  - Require explicit approvals for mutating actions before execution.
  - Enforce tenant-scoped integration control policies.
  - Improve reliability through idempotency, retries, and verification.
  - Add measurable telemetry for agent quality and safety.
- Non-Goals:
  - Full autonomous operation of all integrations on day one.
  - Removal of existing chat features.
  - Replacing existing scheduler/automation engine behavior.

## Phase 1 Policy Defaults (Locked)
- Primary use case: health checks and health-check-derived actions.
- Approvers: tenant admins and tenant members with explicit approval permission.
- Auto-approved safe actions only:
  - create task
  - create journal entry
  - generate recommended checklist
- High-risk actions (must require approval + simulation): outbound device control commands.
- Connectors covered by policy model in release: Pulse, OpenWeather, Ecowitt, plus any connector integrated into the shared control plane.
- UX location for approvals: existing AI side panel (no separate approvals page in Phase 1).
- Notification channels: in-app, web push, and email.
- Rollout: platform-wide at launch (no tenant gating).

## Decisions
- Decision: Represent agent actions as first-class records with lifecycle state transitions.
  - Rationale: Enables clear auditability, retries, and UX timelines.
- Decision: Separate action proposal from execution via approval gates.
  - Rationale: Safety and operator trust for writes to core grow data and external systems.
- Decision: Restrict approvers to tenant admins and permissioned tenant members.
  - Rationale: Preserves RBAC intent while enabling delegated operations.
- Decision: Enforce integration controls through explicit policy checks before outbound execution.
  - Rationale: Tenant-specific risk posture and least privilege.
- Decision: Require dry-run/simulation for actions marked high risk.
  - Rationale: Reduce blast radius of unsafe commands.
- Decision: Add verification stage after execution.
  - Rationale: Agentic behavior must confirm outcomes, not just send commands.

## Architecture
- Agent Runtime:
  - Planner: creates stepwise action plan with confidence and evidence.
  - Policy Gate: validates tenant, role, integration scope, and risk profile.
  - Approval Gate: captures approve/reject with actor, time, and reason.
  - Executor: runs approved actions with idempotency key and bounded retries.
  - Verifier: checks expected postconditions and records outcome.
- Integration Control Plane:
  - Per-tenant allow/deny policy by integration type, mapped device, and operation class.
  - Risk tiers for operations (read-only, low-risk write, high-risk write).
  - Dry-run requirement for high-risk tiers.

## Risks / Trade-offs
- Additional latency from approval and verification stages.
  - Mitigation: async execution + websocket status events.
- Increased implementation complexity.
  - Mitigation: phased rollout with feature flags and narrow initial operation set.
- Potential user friction from too many approvals.
  - Mitigation: auto-approve only explicitly safe actions and keep approval UX in the side panel.

## Migration Plan
1. Introduce additive data models and APIs for platform-wide release.
2. Enable proposal/approval flow for a small set of mutating tools.
3. Expand to integration controls across Pulse, OpenWeather, Ecowitt, and shared connector abstractions.
4. Enable verification requirements and dashboards.
5. Iterate thresholds using observability data.

## Open Questions
- Which specific permission slug should gate action approvals for tenant members?
- Which outbound command families should remain proposal-only after Phase 1?
