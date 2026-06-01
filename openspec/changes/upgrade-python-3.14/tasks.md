## Phase 1: Upgrade to Python 3.13

### 1.1 Infrastructure
- [ ] Update `api/Dockerfile` base image to `python:3.13-slim-bookworm`
- [ ] Update `mirror-base-images.yml` to mirror `python:3.13-slim-bookworm`
- [ ] Push mirror image to local registry
- [ ] Update `.github/workflows/ci.yml` lint job to `python-version: "3.13"`

### 1.2 Configuration
- [ ] Update `api/pyproject.toml` `target-version = "py313"`
- [ ] Run `ruff check` and fix any new lint warnings
- [ ] Run `ruff format` to apply any 3.13-aware formatting

### 1.3 Dependency Validation
- [ ] Verify `bcrypt` builds on 3.13 (C extension)
- [ ] Verify `weasyprint` builds on 3.13 (cairo/pango bindings)
- [ ] Verify `Pillow` builds on 3.13 (C extension)
- [ ] Verify `asyncpg` builds on 3.13 (C extension)
- [ ] Verify `aiohttp` builds on 3.13
- [ ] Run full test suite: `pytest api/tests/`

### 1.4 Code Fixes
- [ ] Fix any `DeprecationWarning`s surfaced by 3.13
- [ ] Replace any usage of removed stdlib modules (unlikely)
- [ ] Verify `asyncio.TaskGroup` behavior matches expectations

### 1.5 Deploy & Soak
- [ ] Deploy 3.13 build to production
- [ ] Monitor for 24-48h: check logs for warnings, pod restarts, latency
- [ ] Confirm health checks passing, scheduler tasks running

---

## Phase 2: Upgrade to Python 3.14

### 2.1 Infrastructure
- [ ] Update `api/Dockerfile` base image to `python:3.14-slim-bookworm`
- [ ] Update `mirror-base-images.yml` to mirror `python:3.14-slim-bookworm`
- [ ] Push mirror image to local registry
- [ ] Update `.github/workflows/ci.yml` lint job to `python-version: "3.14"`

### 2.2 Configuration
- [ ] Update `api/pyproject.toml` `target-version = "py314"`
- [ ] Run `ruff check` and fix any new lint warnings

### 2.3 Adopt PEP 649 (Deferred Annotations)
- [ ] Remove all `from __future__ import annotations` statements
- [ ] Verify Pydantic models still validate correctly (Pydantic uses `get_type_hints()`)
- [ ] Verify SQLAlchemy model annotations resolve correctly
- [ ] Verify FastAPI dependency injection still works

### 2.4 Code Fixes
- [ ] Replace `asyncio.iscoroutinefunction()` with `inspect.iscoroutinefunction()` if used
- [ ] Fix any other 3.14 deprecation warnings

### 2.5 Feature Adoption (Optional, can be separate PRs)
- [ ] Adopt `uuid.uuid7()` for new model IDs (better index locality)
- [ ] Add asyncio introspection docs for debugging scheduler
- [ ] Evaluate t-strings for HTML email templates
- [ ] Evaluate `compression.zstd` for data export endpoints

### 2.6 Deploy & Validate
- [ ] Deploy 3.14 build to production
- [ ] Monitor for 24-48h
- [ ] Confirm all services healthy
- [ ] Update `openspec/project.md` to reflect Python 3.14+

---

## Phase 3: Finalize

### 3.1 Documentation
- [ ] Update `openspec/project.md` Python version to `3.14+`
- [ ] Update `README.md` if it references Python version
- [ ] Archive this OpenSpec change
