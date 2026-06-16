"""Weather domain service.

Holds the business operations for tent-keyed weather lookups and stored
weather-reading history. Route handlers in ``app.weather.routes`` are
HTTP-only — path parsing, response shaping, and ``HTTPException``
raising — and delegate to this module.

Conventions match the project standard established by
``app.automation.service`` (PR #192):

* The first positional argument is always ``session: AsyncSession``.
* Functions return ORM model instances, dataclasses, or lists; they
  never raise ``HTTPException`` — lookup misses return ``None`` and
  validation failures raise typed errors that the route layer maps
  to 4xx.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.grows.models import Tent, WeatherReading


class WeatherUnavailableError(Exception):
    """Raised when a tent cannot have weather data (indoor) or lacks
    coordinates. The route layer maps this to HTTP 400."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True, slots=True)
class WeatherCapableTent:
    """A tent that has been validated as weather-capable.

    Carries the underlying ``Tent`` plus the non-null ``latitude`` and
    ``longitude`` so callers do not have to re-narrow the optional
    coordinate columns on the ORM model.
    """

    tent: Tent
    latitude: float
    longitude: float


async def get_tent(session: AsyncSession, tent_id: UUID) -> Tent | None:
    """Fetch a tent by id; route layer maps ``None`` to HTTP 404."""
    return await session.get(Tent, tent_id)


async def get_weather_capable_tent(session: AsyncSession, tent_id: UUID) -> WeatherCapableTent | None:
    """Fetch a tent and assert it can receive weather data.

    Returns a :class:`WeatherCapableTent` on success. Returns ``None``
    if the tent does not exist (route layer → 404). Raises
    :class:`WeatherUnavailableError` if the tent exists but is indoor
    or has no lat/lng (route layer → 400).
    """
    tent = await get_tent(session, tent_id)
    if tent is None:
        return None
    if tent.environment_type == "indoor":
        raise WeatherUnavailableError("Weather data only for outdoor/greenhouse tents")
    if tent.latitude is None or tent.longitude is None:
        raise WeatherUnavailableError("Tent location (lat/lng) not set")
    return WeatherCapableTent(tent=tent, latitude=tent.latitude, longitude=tent.longitude)


async def list_weather_history(
    session: AsyncSession,
    *,
    tent_id: UUID,
    limit: int,
) -> list[WeatherReading]:
    """Return up to ``limit`` most recent stored weather readings for a tent."""
    result = await session.execute(
        select(WeatherReading)
        .where(WeatherReading.tent_id == tent_id)
        .order_by(desc(WeatherReading.recorded_at))
        .limit(limit)
    )
    return list(result.scalars().all())
