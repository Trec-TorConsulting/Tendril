# Tendril — Agent Guide

AI assistants working in this repo should use **Cursor** (rules, skills, and slash commands). GitHub Copilot project config has been removed.

## OpenSpec (spec-driven changes)

Tendril uses [OpenSpec](https://github.com/Fission-AI/OpenSpec). Prefer Cursor slash commands / skills over hand-editing scaffolding:

| Command | Skill | When |
|---|---|---|
| `/opsx-propose` | `openspec-propose` | Scaffold a new change |
| `/opsx-apply` | `openspec-apply-change` | Implement approved tasks |
| `/opsx-archive` | `openspec-archive-change` | Archive after deploy |
| `/opsx-explore` | `openspec-explore` | Explore without implementing |
| `/opsx-sync` | `openspec-sync-specs` | Sync specs |

```bash
openspec list                  # Active changes
openspec list --specs          # Specs
openspec validate <id> --strict --no-interactive
openspec archive <id> --yes
```

### Layout

```
openspec/
  config.yaml     # Schema + planning context for AI
  project.md      # Full project conventions (prefer config.yaml context for new work)
  specs/          # Current truth
  changes/        # Proposals in flight (+ archive/)
```

### When to propose

Create a change for new capabilities, breaking changes, architecture shifts, or security/performance work that changes behavior. Skip for bug fixes that restore intended behavior, typos, dependency bumps, and config-only edits.

Do not implement until the proposal is approved.

## Package guides

- [`api/AGENTS.md`](api/AGENTS.md) — FastAPI + SQLAlchemy
- [`web/AGENTS.md`](web/AGENTS.md) — Next.js dashboard
- [`esp32/AGENTS.md`](esp32/AGENTS.md) — firmware
- [`manifests/AGENTS.md`](manifests/AGENTS.md) — k3s deploy

## Cursor rules & skills

- Rules (auto-attached by glob): `.cursor/rules/` (`web-react`, `api-python`)
- Workflow skills: `.cursor/skills/` (`add-migration`, `regen-api-types`, OpenSpec skills)
- Slash commands: `.cursor/commands/` (`opsx-*`)
