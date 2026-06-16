"""Dump the FastAPI app's OpenAPI schema to stdout (or a file).

Usage:
    python api/scripts/export_openapi.py             # write to stdout
    python api/scripts/export_openapi.py --out FILE  # write to FILE

This script intentionally sets dummy values for the secret-bearing env
vars that ``app.config`` requires at import time. No database connection
is made — OpenAPI generation only needs the route signatures and Pydantic
schemas, which are resolved purely from Python source.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Minimum env shim so app.config.get_settings() doesn't blow up.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://noop:noop@localhost/noop")
os.environ.setdefault("JWT_SECRET", "openapi-export-only-not-a-real-secret")

# Make ``app`` importable regardless of CWD.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from app.main import create_app  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="Output file (default: stdout)")
    args = parser.parse_args()

    app = create_app()
    schema = app.openapi()
    payload = json.dumps(schema, indent=2, sort_keys=True) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
