"""Auth provider adapter interface.

Allows plugging in external identity providers (Auth0, Firebase, Supabase)
while keeping the core auth flow provider-agnostic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class ExternalUser:
    """Normalized user info from an external auth provider."""
    provider: str
    provider_user_id: str
    email: str
    display_name: str | None = None
    email_verified: bool = False


class AuthAdapter(ABC):
    """Base class for external auth provider adapters."""

    @abstractmethod
    async def verify_token(self, token: str) -> ExternalUser:
        """Verify an external provider token and return normalized user info."""
        ...

    @abstractmethod
    async def get_user(self, provider_user_id: str) -> ExternalUser | None:
        """Look up a user by provider-specific ID."""
        ...
