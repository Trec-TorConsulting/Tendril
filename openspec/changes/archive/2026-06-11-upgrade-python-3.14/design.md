# Design: Python 3.14 Upgrade

## Architecture Decisions

### AD-1: Stepping Strategy (3.12 → 3.13 → 3.14)

**Decision**: Upgrade in two phases rather than jumping directly to 3.14.

**Rationale**:
- Python 3.13 deprecated APIs that 3.14 removes (especially asyncio child watchers, `get_event_loop()` implicit creation)
- Running on 3.13 surfaces `DeprecationWarning` that become hard errors in 3.14
- If native deps (weasyprint, bcrypt, Pillow) have issues, we isolate which version broke them
- Smaller blast radius per deploy

**Alternative rejected**: Direct 3.12 → 3.14 jump. Risk is that multiple breaking changes stack up and are harder to diagnose.

---

### AD-2: PEP 649 Adoption (Deferred Annotations)

**Decision**: Remove `from __future__ import annotations` after upgrading to 3.14.

**Rationale**:
- PEP 649 makes deferred evaluation the default — no future import needed
- Removes a boilerplate line from every module
- Annotations are now lazily evaluated, reducing module import time
- Pydantic v2, SQLAlchemy 2.x, and FastAPI all support the new behavior

**Risk**: Libraries that call `get_type_hints()` at import time might behave differently. Need to verify with `pydantic>=2.0` and `sqlalchemy>=2.0`.

---

### AD-3: uuid7() Adoption

**Decision**: Use `uuid.uuid7()` for new models going forward; do NOT migrate existing IDs.

**Rationale**:
- UUIDv7 is time-ordered, improving B-tree insert performance for PostgreSQL indexes
- Existing UUIDv4 columns remain unchanged (no migration needed)
- New tables/models get UUIDv7 as the default
- `uuid7()` is now stdlib — no need for third-party `uuid6` package

**Implementation**:
```python
import uuid

# In model base or mixins
def generate_id() -> uuid.UUID:
    return uuid.uuid7()
```

---

### AD-4: Template Strings (t-strings) for SQL Safety

**Decision**: Evaluate but do NOT adopt immediately for production SQL. Use for HTML email templates first.

**Rationale**:
- SQLAlchemy already handles parameterized queries safely
- t-strings are brand new; library ecosystem is immature
- HTML email templates (WeasyPrint) could benefit from safe interpolation
- Revisit after ecosystem stabilizes

---

### AD-5: asyncio Introspection in Production

**Decision**: Enable and document `python -m asyncio pstree` for on-demand scheduler debugging.

**Rationale**:
- Tendril's scheduler uses TaskGroups with multiple concurrent tasks (sensor collection, pump scheduling, alert evaluation)
- When tasks hang, `pstree PID` shows exactly which coroutine is blocked
- Zero runtime overhead — introspection is on-demand from outside the process
- Works via `sys.remote_exec` (PEP 768) — doesn't require restarting the process

**Usage**:
```bash
# Find scheduler PID
kubectl exec -it deploy/scheduler -- pgrep -f "python -m app.scheduler"

# Inspect task tree
kubectl exec -it deploy/scheduler -- python -m asyncio pstree <PID>
```

---

### AD-6: Tail-Call Interpreter

**Decision**: Adopt if building from source; for `python:3.14-slim-bookworm` official images, accept whatever the default is.

**Rationale**:
- The tail-call interpreter gives 3-5% speedup on ARM64 (our cluster architecture)
- Official Docker images may or may not enable `--with-tail-call-interp`
- If they don't, we could build a custom image, but the maintenance cost isn't worth 3-5% for now
- Revisit if we move to a custom Python build

---

## Dependency Compatibility Matrix

| Package | Min Version | 3.13 Support | 3.14 Support | Notes |
|---------|-------------|:---:|:---:|-------|
| fastapi | >=0.115 | ✅ | ✅ | Confirmed in their CI |
| sqlalchemy[asyncio] | >=2.0 | ✅ | ✅ | Supports deferred annotations |
| asyncpg | >=0.30 | ✅ | ✅ | C extension, wheels available |
| pydantic | >=2.0 | ✅ | ✅ | PEP 649 aware since 2.5 |
| bcrypt | >=4.0 | ✅ | ⚠️ TBD | Rust-based, usually quick to support |
| Pillow | >=12.0 | ✅ | ⚠️ TBD | C extensions, verify wheels |
| weasyprint | >=62.0 | ✅ | ⚠️ TBD | Highest risk — cairo/pango deps |
| aiohttp | >=3.9 | ✅ | ✅ | C speedups, verify build |
| aiomqtt | >=2.0 | ✅ | ✅ | Pure Python |
| redis | >=5.0 | ✅ | ✅ | Pure Python |
| stripe | >=8.0 | ✅ | ✅ | Pure Python |
| boto3 | >=1.34 | ✅ | ✅ | Pure Python |

**Strategy**: Run `docker build` with 3.13 image first. If all deps install and tests pass, proceed. For 3.14, check PyPI for wheel availability before attempting.

---

## Rollback Plan

Each phase can be independently rolled back by:
1. Reverting the Dockerfile base image tag
2. Reverting `pyproject.toml` target-version
3. Running CI and redeploying

Git tags will be created at each stable point:
- `v-pre-3.13-upgrade` (current state)
- `v-post-3.13-upgrade` (after Phase 1 soak)
- `v-post-3.14-upgrade` (final state)
