"""Fernet symmetric encryption for integration credentials."""

from __future__ import annotations

import json
import os

from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    key = os.environ.get("INTEGRATION_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("INTEGRATION_ENCRYPTION_KEY environment variable is required")
    return Fernet(key.encode())


def encrypt_config(config: dict) -> str:
    """Encrypt a config dict to a Fernet token string."""
    payload = json.dumps(config, separators=(",", ":")).encode()
    return _get_fernet().encrypt(payload).decode()


def decrypt_config(token: str) -> dict:
    """Decrypt a Fernet token string back to a config dict."""
    payload = _get_fernet().decrypt(token.encode())
    return json.loads(payload)


def redact_config(config: dict) -> dict:
    """Return config with secret-looking values masked.

    Keys containing 'key', 'secret', 'token', 'password', or 'credential'
    are replaced with a masked string showing only the last 4 characters.
    """
    sensitive = {"key", "secret", "token", "password", "credential"}
    redacted: dict = {}
    for k, v in config.items():
        if any(s in k.lower() for s in sensitive) and isinstance(v, str) and len(v) > 4:
            redacted[k] = f"••••••••{v[-4:]}"
        else:
            redacted[k] = v
    return redacted
