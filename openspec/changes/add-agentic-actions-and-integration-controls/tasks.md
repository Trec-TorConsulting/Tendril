## 1. Implementation
- [x] 1.1 Add agent action lifecycle models and persistence (proposal, approval, execution, verification states) for health-check action flows first.
- [x] 1.2 Add API and websocket events for action lifecycle updates.
- [x] 1.3 Add policy-gate checks before any mutating AI tool execution.
- [x] 1.4 Add approval-gate workflow with role-aware approver identity (tenant admin + permissioned member) and expiration.
- [x] 1.5 Add idempotent executor with bounded retries and deterministic action IDs.
- [x] 1.6 Add post-execution verification hooks and result recording.
- [x] 1.7 Add websocket keepalive support and conversation-thread binding in chat flow.
- [x] 1.8 Add web chat UI support for pending approvals, action timeline, and execution status in the existing AI side panel.
- [x] 1.9 Add integration control policy models and enforcement checks for outbound operations across Pulse, OpenWeather, and Ecowitt (extensible to all connectors).
- [x] 1.10 Add dry-run/simulation requirement for high-risk operations (outbound device control commands).
- [x] 1.11 Implement safe auto-approval path for create task, create journal entry, and checklist generation only.
- [x] 1.12 Add notification fanout for approval and lifecycle events: in-app, web push, email.

## 2. Testing
- [x] 2.1 Add unit tests for lifecycle state transitions and invalid transitions.
- [x] 2.2 Add policy and approval gate tests for allowed/blocked action cases.
- [x] 2.3 Add integration control tests across connectors and risk tiers.
- [x] 2.4 Add websocket tests for keepalive, reconnect, and conversation-thread resume.
- [x] 2.5 Add end-to-end tests for propose -> approve -> execute -> verify flows.

## 3. Observability and Rollout
- [x] 3.1 Emit metrics for proposal volume, approvals, execution success/failure, and policy blocks.
- [x] 3.2 Add structured logs for action lifecycle with tenant and conversation correlation IDs.
- [x] 3.3 Add platform-wide rollout checklist, migration safety checks, and backout procedure.
- [x] 3.4 Add operator documentation for approvals, controls, and troubleshooting.

## 4. PR Slicing Plan (Small, Verifiable Increments)

### PR1: Data Model + Lifecycle Skeleton (No UX changes)
- Scope:
	- Add agent action lifecycle persistence models (proposal, approval, execution, verification).
	- Add migration(s) and basic repository/service methods.
	- Add strict lifecycle transition rules and invalid transition guards.
- Includes tasks:
	- 1.1
	- 1.5 (id generation primitives only)
	- 2.1
- Acceptance:
	- Lifecycle records can be created and moved through valid states.
	- Invalid state transitions are rejected with deterministic errors.
	- No behavior change to existing chat endpoints.
- CI/Test gate:
	- API lint/type/tests pass; migration tests pass.

### PR2: Health-Check Agent Actions + Policy/Approval Backend
- Scope:
	- Wire health-check flow to emit lifecycle-tracked actions.
	- Add policy gate and approval gate APIs.
	- Enforce approver eligibility (tenant admin or permissioned member).
	- Implement safe auto-approval list (create task, create journal entry, checklist generation).
- Includes tasks:
	- 1.3
	- 1.4
	- 1.6 (health-check verification hooks)
	- 1.11
	- 2.2
	- 2.5 (health-check path only)
- Acceptance:
	- Health checks generate actionable plans in lifecycle records.
	- Safe actions auto-approve; all other mutating actions require approval.
	- Unauthorized approvers are blocked.
- CI/Test gate:
	- Unit + integration tests for policy and approval pass.

### PR3: Chat Session Reliability + Side Panel Lifecycle UX
- Scope:
	- Add websocket keepalive and robust conversation-thread binding.
	- Add side-panel visualization for pending approvals, action timeline, and status updates.
	- Preserve current chat usability and streaming behavior.
- Includes tasks:
	- 1.2 (websocket lifecycle events)
	- 1.7
	- 1.8
	- 2.4
- Acceptance:
	- Reconnect resumes existing conversation thread reliably.
	- Idle websocket remains healthy during long responses.
	- Users can approve/reject pending actions in the AI side panel.
- CI/Test gate:
	- Web lint/type/tests pass; API websocket tests pass.

### PR4: Integration Controls Across Connectors + High-Risk Simulation
- Scope:
	- Add integration control policies and enforcement across Pulse, OpenWeather, Ecowitt.
	- Mark outbound device control commands as high-risk by default.
	- Enforce dry-run/simulation before approval/execution for high-risk commands.
	- Keep framework extensible for additional connectors.
- Includes tasks:
	- 1.9
	- 1.10
	- 2.3
- Acceptance:
	- Connector actions are consistently evaluated by policy.
	- High-risk outbound control commands cannot execute without simulation + approval.
	- Idempotency and retry behavior prevents duplicate side effects where supported.
- CI/Test gate:
	- Connector integration tests pass for allow/deny/simulation paths.

### PR5: Notification Fanout + Observability + Production Readiness
- Scope:
	- Add notification fanout (in-app, web push, email) for approvals and lifecycle transitions.
	- Add metrics/logging dashboards and operational docs.
	- Add platform-wide rollout checklist + backout plan.
- Includes tasks:
	- 1.12
	- 3.1
	- 3.2
	- 3.3
	- 3.4
- Acceptance:
	- Lifecycle state changes trigger all three notification channels.
	- Operators can trace action lifecycle by tenant and conversation IDs.
	- Runbook exists for rollout and rollback.
- CI/Test gate:
	- Notification tests pass; no regression in existing alert pipelines.

## 5. Implementation Order and Guardrails
- [ ] 5.1 Merge PR1 before starting PR2 (schema and lifecycle base are required).
- [ ] 5.2 Keep each PR independently deployable with no hidden coupling.
- [ ] 5.3 No PR may change more than one primary surface area without explicit note (API, Web, Integrations).
- [ ] 5.4 After each PR: run strict OpenSpec validation and map completed checklist items.
- [x] 5.5 Preserve backward compatibility for existing chat consumers until PR3 lands.
