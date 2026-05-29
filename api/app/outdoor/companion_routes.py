"""Companion planting database — compatibility checks and suggestions."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.auth.middleware import CurrentUser, get_current_user
from app.database import async_session_factory
from app.reference.models import CompanionPlant

router = APIRouter()


class CompanionEntry(BaseModel):
    plant: str
    beneficial: list[str]
    harmful: list[str]
    notes: str


class CompatibilityResponse(BaseModel):
    plant: str
    neighbor: str
    compatibility: str
    reason: str


class CompanionSuggestion(BaseModel):
    plant: str
    notes: str


class SuggestResponse(BaseModel):
    plant: str
    suggestions: list[CompanionSuggestion]


@router.get("", response_model=list[CompanionEntry])
async def list_companions(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get the full companion planting database."""
    async with async_session_factory() as session:
        result = await session.execute(select(CompanionPlant))
        plants = result.scalars().all()
    return [
        {
            "plant": p.name,
            "beneficial": p.companions or [],
            "harmful": p.antagonists or [],
            "notes": p.notes or "",
        }
        for p in plants
    ]


@router.get("/check", response_model=CompatibilityResponse)
async def check_compatibility(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    plant: str = Query(description="Primary plant"),
    neighbor: str = Query(description="Neighboring plant to check"),
):
    """Check compatibility between two plants."""
    plant_slug = plant.lower().replace(" ", "_")
    neighbor_slug = neighbor.lower().replace(" ", "_")

    async with async_session_factory() as session:
        result = await session.execute(select(CompanionPlant).where(CompanionPlant.slug == plant_slug))
        plant_row = result.scalar_one_or_none()

    if plant_row is None:
        return {
            "plant": plant,
            "neighbor": neighbor,
            "compatibility": "unknown",
            "reason": f"'{plant}' not in database",
        }

    if neighbor_slug in (plant_row.companions or []):
        return {
            "plant": plant,
            "neighbor": neighbor,
            "compatibility": "beneficial",
            "reason": f"{neighbor} is beneficial for {plant}",
        }
    if neighbor_slug in (plant_row.antagonists or []):
        return {
            "plant": plant,
            "neighbor": neighbor,
            "compatibility": "harmful",
            "reason": f"{neighbor} is harmful to {plant}",
        }

    return {
        "plant": plant,
        "neighbor": neighbor,
        "compatibility": "neutral",
        "reason": "No known positive or negative interaction",
    }


@router.get("/suggest", response_model=SuggestResponse)
async def suggest_companions(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    plant: str = Query(description="Plant to get suggestions for"),
):
    """Suggest beneficial companion plants."""
    plant_slug = plant.lower().replace(" ", "_")

    async with async_session_factory() as session:
        result = await session.execute(select(CompanionPlant).where(CompanionPlant.slug == plant_slug))
        plant_row = result.scalar_one_or_none()

        if plant_row is None:
            # Default to cannabis companions
            result = await session.execute(select(CompanionPlant).where(CompanionPlant.slug == "cannabis"))
            plant_row = result.scalar_one_or_none()

        suggestions = []
        if plant_row and plant_row.companions:
            for companion_slug in plant_row.companions:
                comp_result = await session.execute(select(CompanionPlant).where(CompanionPlant.slug == companion_slug))
                comp_row = comp_result.scalar_one_or_none()
                suggestions.append(
                    {
                        "plant": companion_slug.replace("_", " ").title(),
                        "notes": comp_row.notes if comp_row else "",
                    }
                )

    return {"plant": plant, "suggestions": suggestions}
