"""Shared password utilities — strength validation and hashing."""

from __future__ import annotations

import re

import bcrypt
from fastapi import HTTPException


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def validate_password_strength(password: str) -> None:
    """Enforce enterprise-grade password policy.

    Requirements: min 12 chars, uppercase, lowercase, digit, special character.
    Raises HTTPException on failure.
    """
    errors: list[str] = []
    if len(password) < 12:
        errors.append("at least 12 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"\d", password):
        errors.append("a digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_=+\[\]\\;'/`~]", password):
        errors.append("a special character")
    if errors:
        raise HTTPException(
            status_code=400,
            detail=f"Password must contain {', '.join(errors)}",
        )
