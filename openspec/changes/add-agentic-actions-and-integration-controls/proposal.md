# Change: Add Agentic Actions and Integration Controls

## Why
Tendril already supports AI chat with tool calling, but it does not yet behave like a fully agentic control system with explicit planning, approval gates, and verifiable execution loops. As Tendril integrates more third-party systems and device controls, we need stronger action safety, tenant controls, and observability to prevent unintended mutations while improving operator trust.

## What Changes
- Add an explicit agent action lifecycle: observe, plan, propose, approve, execute, verify, and summarize.
- Add approval gates for mutating actions, including user/role-based approvals and expiration.
- Add integration control policies so each tenant can define allowed actions per integration, device map, and risk level.
- Add dry-run/simulation requirements for high-risk outbound control actions.
- Add execution idempotency and retries with deterministic action IDs.
- Add websocket conversation binding requirements so conversation threads are consistently resumed.
- Add agent observability and evaluation requirements (action success, safety blocks, tool failures, fallback rates).
- Phase 1 scope is health-check-driven actions with simple, low-friction UX in the existing AI side panel.
- Phase 1 auto-approval includes only 100%-safe actions: task creation, journal entry creation, and checklist generation.
- High-risk classification in Phase 1 is limited to outbound device control commands.
- Integration control framework applies to all supported connectors in this release (Pulse, OpenWeather, Ecowitt, and future connectors via the same policy model).
- Notifications for pending approvals and action state changes are delivered in-app, web push, and email.

## Impact
- Affected specs:
  - grow-assistant-core
  - integrations-framework
- Affected code (expected):
  - api/app/ai/routes.py
  - api/app/ai/tools.py
  - api/app/ai/service.py
  - api/app/integrations/**
  - web/src/components/chat-provider.tsx
  - web/src/app/dashboard/ai/**
- Data model impact (expected):
  - new agent action/audit entities for proposals, approvals, executions, and verification results
  - integration control policy entities scoped by tenant
- Security impact:
  - stronger least-privilege controls for integrated-system mutations
  - mandatory auditability for AI-triggered actions
- Breaking changes:
  - none required for initial rollout; behavior is additive and ships platform-wide
