"""Regression guard for the bug class fixed by PR #196.

Background
----------
PR #194 added migration 0047 which bulk-inserted into ``automation_rules``
via ``sa.table(...).insert()``. That bypasses the ORM model's Python-side
``default=uuid.uuid4`` on the ``id`` column. The ``automation_rules`` table
has no ``server_default`` for its UUID id column \u2014 the insert produced
``NotNullViolationError`` and rolled back, leaving the deploy half-complete
(old pods kept serving, new pods stuck in ``Init:CrashLoopBackOff``).

PR #196 hotfixed by adding ``"id": uuid.uuid4()`` to each row dict.

What this guard does
--------------------
Re-scans every migration in ``api/migrations/versions/`` for the same
pattern:

* Build a corpus of every ``op.create_table`` call across the entire
  migration history, recording which ``UUID`` PK columns lack
  ``server_default``.
* For each migration, find:
  * Raw ``INSERT INTO X (cols) VALUES`` statements that omit ``id``
  * ``sa.table(...)`` + ``.insert()`` calls that omit ``id``
  * ``op.bulk_insert(...)`` calls whose row dicts omit ``id``
* Cross-reference: if the target table has UUID PK without
  ``server_default``, **fail the test**.

Add a new migration that needs bulk-insert? Either:
  1. Add ``"id": uuid.uuid4()`` to each row dict (preferred \u2014 explicit), OR
  2. Add ``server_default=sa.text("gen_random_uuid()")`` to the table's
     ``id`` column DDL.

Either fix passes this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "migrations" / "versions"


def _find_matching_paren(content: str, open_idx: int) -> int:
    """Return index of the ``)`` matching the ``(`` at ``open_idx``."""
    assert content[open_idx] == "("
    depth = 1
    j = open_idx + 1
    while j < len(content) and depth:
        if content[j] == "(":
            depth += 1
        elif content[j] == ")":
            depth -= 1
        if depth == 0:
            return j
        j += 1
    return -1


def _parse_tables(content: str) -> dict[str, dict[str, bool]]:
    """Parse ``op.create_table`` calls, returning info about each table's id column."""
    out: dict[str, dict[str, bool]] = {}
    for m in re.finditer(r'op\.create_table\(\s*"(\w+)"', content):
        table = m.group(1)
        open_paren = content.find("(", m.start())
        close_paren = _find_matching_paren(content, open_paren)
        if close_paren < 0:
            continue
        body = content[open_paren + 1 : close_paren]

        id_col_match = re.search(r'sa\.Column\(\s*"id"\s*,', body)
        if not id_col_match:
            continue
        col_open = body.find("(", id_col_match.start())
        col_close = _find_matching_paren(body, col_open)
        if col_close < 0:
            continue
        col_def = body[col_open + 1 : col_close]

        out[table] = {
            "has_server_default": "server_default" in col_def,
            "is_uuid": "UUID" in col_def,
            "is_pk": "primary_key=True" in col_def,
        }
    return out


def _build_corpus() -> dict[str, dict[str, bool]]:
    """Aggregate table info across the entire migration history."""
    corpus: dict[str, dict[str, bool]] = {}
    for path in sorted(MIGRATIONS_DIR.glob("*.py")):
        corpus.update(_parse_tables(path.read_text()))
    return corpus


def _check_raw_inserts(content: str, file: str, tables: dict) -> list[str]:
    """Flag raw ``INSERT INTO X (cols) VALUES`` that omit 'id' on dangerous tables."""
    bugs: list[str] = []
    for m in re.finditer(r"INSERT INTO\s+(\w+)\s*\(([^)]+)\)", content):
        table = m.group(1)
        cols = [c.strip().strip("'\"") for c in m.group(2).split(",")]
        info = tables.get(table)
        if not info or not (info["is_uuid"] and info["is_pk"]):
            continue
        if "id" not in cols and not info["has_server_default"]:
            bugs.append(
                f"{file}: raw INSERT INTO {table} omits 'id' column; "
                f"table has UUID primary key WITHOUT server_default. "
                f"Either add an explicit id or add server_default to the table DDL."
            )
    return bugs


def _check_sa_table_inserts(content: str, file: str, tables: dict) -> list[str]:
    """Flag ``sa.table(X).insert()`` calls that omit 'id' on dangerous tables.

    The same variable may be re-bound to different ``sa.table(...)`` calls
    inside the same file (typical pattern: ``upgrade()`` declares the full
    column set, ``downgrade()`` declares only the columns needed for a
    DELETE filter). We pair each ``.insert()`` with the most recently
    declared ``sa.table(...)`` that appears BEFORE it in source order, so
    a column-stripped downgrade declaration does not falsely flag the
    upgrade's insert.
    """
    bugs: list[str] = []

    # Gather all sa.table declarations in source order:
    #   [(decl_pos, var, table_name, cols_block), ...]
    declarations: list[tuple[int, str, str, str]] = []
    for m in re.finditer(r'(\w+)\s*=\s*sa\.table\(\s*"(\w+)"', content):
        var, tbl = m.group(1), m.group(2)
        open_paren = content.find("(", m.start())
        close_paren = _find_matching_paren(content, open_paren)
        if close_paren < 0:
            continue
        cols_block = content[open_paren + 1 : close_paren]
        declarations.append((m.start(), var, tbl, cols_block))

    # For each .insert() in source order, find the most recent matching declaration.
    for ins in re.finditer(r"(\w+)\.insert\(\)", content):
        var = ins.group(1)
        # Find latest declaration of this var that precedes the insert.
        match: tuple[int, str, str, str] | None = None
        for decl in declarations:
            if decl[1] != var:
                continue
            if decl[0] >= ins.start():
                break
            match = decl
        if match is None:
            continue
        _decl_pos, _var, tbl, cols_block = match
        info = tables.get(tbl)
        if not info or not (info["is_uuid"] and info["is_pk"]):
            continue
        has_id_col = re.search(r'sa\.column\(\s*"id"', cols_block) is not None
        if not has_id_col and not info["has_server_default"]:
            bugs.append(
                f"{file}: {var}=sa.table('{tbl}') has NO 'id' column declared, "
                f"and the table has no server_default for its UUID id. "
                f"This is the PR #196 bug class — add 'id' to the sa.table() column "
                f"list and populate it with uuid.uuid4() per row."
            )
            continue
        if has_id_col:
            after = content[ins.end() : ins.end() + 4000]
            row_dicts = re.findall(r'\{(\s*"\w+"\s*:[^{}]*)\}', after)
            for rd in row_dicts[:5]:
                if '"id"' not in rd and not info["has_server_default"]:
                    bugs.append(
                        f"{file}: {var}.insert() row dict missing 'id' — "
                        f"table '{tbl}' has no server_default. Populate id explicitly."
                    )
                    break
    return bugs


def _check_bulk_insert(content: str, file: str, tables: dict) -> list[str]:
    """Flag ``op.bulk_insert(...)`` rows that omit 'id' on dangerous tables."""
    bugs: list[str] = []
    for m in re.finditer(r"op\.bulk_insert\(\s*(\w+)\s*,", content):
        var = m.group(1)
        defm = re.search(rf'{re.escape(var)}\s*=\s*sa\.table\(\s*"(\w+)"', content)
        if not defm:
            continue
        tbl = defm.group(1)
        info = tables.get(tbl)
        if not info or not (info["is_uuid"] and info["is_pk"]):
            continue
        after = content[m.end() : m.end() + 5000]
        first = re.search(r"\{([^{}]*)\}", after)
        if first and '"id"' not in first.group(1) and not info["has_server_default"]:
            bugs.append(
                f"{file}: op.bulk_insert({var}) row missing 'id' — "
                f"table '{tbl}' has no server_default. Populate id explicitly."
            )
    return bugs


def test_no_migrations_bypass_uuid_default() -> None:
    """Regression guard for the bug class fixed by PR #196.

    Scans every migration in ``api/migrations/versions/`` for INSERTs
    that bypass the ORM's Python-side ``default=uuid.uuid4`` on tables
    whose DDL has no server-side equivalent. See module docstring for
    background and remediation.
    """
    tables = _build_corpus()
    findings: list[str] = []
    for path in sorted(MIGRATIONS_DIR.glob("*.py")):
        content = path.read_text()
        file = path.name
        findings.extend(_check_raw_inserts(content, file, tables))
        findings.extend(_check_sa_table_inserts(content, file, tables))
        findings.extend(_check_bulk_insert(content, file, tables))

    assert not findings, "Migration(s) bypass UUID id defaults (PR #196 bug class):\n  - " + "\n  - ".join(findings)
