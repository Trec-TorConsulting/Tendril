# Change: Upgrade Python 3.12 → 3.13 → 3.14

## Why
Python 3.12 reaches security-only status in Oct 2027. Python 3.14 (released Oct 2025) brings significant performance improvements and features directly relevant to Tendril's async-heavy architecture:

- **10-20% asyncio performance gain** from new per-thread task linked list
- **Asyncio introspection** (`python -m asyncio pstree PID`) for debugging stuck scheduler tasks
- **Deferred annotation evaluation** (PEP 649) — reduces import time, eliminates `from __future__ import annotations`
- **Template strings** (PEP 750) — safe SQL/HTML templating without injection risk
- **Tail-call interpreter** — 3-5% general performance improvement on ARM64
- **`uuid.uuid7()`** — time-ordered UUIDs for better DB index performance
- **`compression.zstd`** — stdlib Zstandard for data exports/backups

## Upgrade Strategy
Two-phase upgrade stepping through 3.13 first to catch deprecation warnings before hitting removals in 3.14:

### Phase 1: Python 3.12 → 3.13
- Update base image: `python:3.13-slim-bookworm`
- Update ruff `target-version = "py313"`
- Update CI setup-python to `3.13`
- Fix any deprecation warnings surfaced
- Verify all dependencies work (especially `weasyprint`, `bcrypt`, native extensions)
- Deploy and soak for stability

### Phase 2: Python 3.13 → 3.14
- Update base image: `python:3.14-slim-bookworm`
- Update ruff `target-version = "py314"`
- Remove `from __future__ import annotations` (PEP 649 makes it unnecessary)
- Adopt new features where beneficial (uuid7, t-strings, asyncio introspection)
- Deploy final version

## What Changes
- `api/Dockerfile`: Base image tag update (twice)
- `api/pyproject.toml`: `target-version` update
- `.github/workflows/ci.yml`: `python-version` in lint job
- `.github/workflows/mirror-base-images.yml`: New mirror target
- `openspec/project.md`: Python version reference
- Various source files: Remove `from __future__ import annotations`, adopt new features

## Impact
- **Runtime**: 10-20% faster async operations, 3-5% general speedup
- **Developer experience**: Better error messages, asyncio debugging tools
- **Security**: Latest security patches, ahead of 3.12 EOL
- **Breaking risk**: Low — Tendril uses `asyncio.run()` (not deprecated `get_event_loop()`), no child watchers

## Features We Can Adopt

### From Python 3.13
| Feature | Use Case in Tendril |
|---------|-------------------|
| `typing.TypeIs` | Better type narrowing in permission checks |
| `typing.ReadOnly` TypedDict | Immutable config/settings types |
| `warnings.deprecated()` | Mark deprecated API endpoints for v2 migration |
| `asyncio.Queue.shutdown` | Clean MQTT worker shutdown |
| `asyncio.TaskGroup` fixes | More reliable scheduler task group cancellation |
| Color tracebacks | Better log readability in dev |

### From Python 3.14
| Feature | Use Case in Tendril |
|---------|-------------------|
| Deferred annotations (PEP 649) | Eliminate `from __future__ import annotations` everywhere |
| Template strings (PEP 750) | Safe SQL query building, HTML email templates |
| `asyncio` introspection | Debug stuck scheduler tasks via `python -m asyncio pstree` |
| `uuid.uuid7()` | Time-ordered primary keys for better B-tree locality |
| `compression.zstd` | Compress data exports, backup archives |
| `InterpreterPoolExecutor` | CPU-bound AI prompt building (future) |
| Tail-call interpreter | Free 3-5% perf on ARM64 (our arch) |
| `except` without parens | Cleaner exception handling syntax |

## Breaking Changes to Watch

### 3.13 Removals (from 3.12 deprecations)
- `asyncio` child watcher classes → **Not used** (we use `asyncio.run()`)
- Dead batteries (19 stdlib modules) → **Not used** (removed in 3.13)

### 3.14 Removals (from 3.13 deprecations)
- `asyncio.get_event_loop()` raises `RuntimeError` without loop → **Not used** (we use `asyncio.run()`)
- `asyncio.iscoroutinefunction()` deprecated → Replace with `inspect.iscoroutinefunction()` if used
- Itertools copy/pickle support removed → **Not used**

### 3.14 Behavioral Changes
- Incremental GC reverted in 3.14.5 (back to generational) → **No action needed**
- `typing.Union` and `types.UnionType` unified → **No action needed** (we use `X | Y` syntax)

## Risks / Trade-offs
- Native extension compatibility (`bcrypt`, `weasyprint`, `Pillow`, `asyncpg`) — mitigate with 3.13 soak period
- `weasyprint` is the highest-risk dep (C dependencies) — verify in Docker build
- Two deploys required (3.13 then 3.14) — adds time but reduces blast radius
