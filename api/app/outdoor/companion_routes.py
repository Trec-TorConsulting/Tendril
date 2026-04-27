"""Companion planting database — compatibility checks and suggestions."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.auth.middleware import CurrentUser, get_current_user

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

# Built-in companion planting database for cannabis
# Format: {plant: {beneficial: [...], harmful: [...], notes: str}}
COMPANION_DB: dict[str, dict] = {
    "cannabis": {
        "beneficial": ["basil", "marigold", "lavender", "chamomile", "dill", "peppermint", "sunflower", "clover", "alfalfa", "yarrow", "lemon_balm", "chives", "garlic", "beans", "cerastium"],
        "harmful": ["fennel", "corn", "walnut"],
        "notes": "Cannabis thrives with aromatic herbs that repel pests and nitrogen-fixing cover crops.",
    },
    "basil": {
        "beneficial": ["cannabis", "tomato", "marigold"],
        "harmful": ["sage", "rue"],
        "notes": "Repels aphids, spider mites, mosquitoes, and whiteflies. Aromatic oils may improve terpene profiles.",
    },
    "marigold": {
        "beneficial": ["cannabis", "tomato", "basil", "beans"],
        "harmful": [],
        "notes": "Repels nematodes, whiteflies, and aphids. Root exudates kill soil nematodes. French marigolds are most effective.",
    },
    "lavender": {
        "beneficial": ["cannabis", "rosemary"],
        "harmful": [],
        "notes": "Attracts pollinators, repels fleas, moths, and mice. Excellent aromatic pest deterrent.",
    },
    "chamomile": {
        "beneficial": ["cannabis", "basil", "wheat"],
        "harmful": [],
        "notes": "Accumulates calcium, potassium, and sulfur. Improves soil when composted. Attracts beneficial insects.",
    },
    "dill": {
        "beneficial": ["cannabis", "lettuce", "cabbage"],
        "harmful": ["carrot", "tomato"],
        "notes": "Attracts ladybugs, lacewings, and parasitic wasps that prey on aphids and caterpillars.",
    },
    "peppermint": {
        "beneficial": ["cannabis", "cabbage"],
        "harmful": [],
        "notes": "Strong scent deters aphids, flea beetles, and ants. Plant in containers to prevent spreading.",
    },
    "sunflower": {
        "beneficial": ["cannabis", "beans", "squash"],
        "harmful": [],
        "notes": "Provides windbreak, attracts pollinators. Acts as a 'trap crop' for aphids — they prefer sunflowers.",
    },
    "clover": {
        "beneficial": ["cannabis", "corn", "fruit_trees"],
        "harmful": [],
        "notes": "Nitrogen-fixing cover crop. Living mulch suppresses weeds, retains moisture. White clover is ideal.",
    },
    "alfalfa": {
        "beneficial": ["cannabis", "cotton", "corn"],
        "harmful": [],
        "notes": "Deep taproots break up compacted soil. Fixes nitrogen. Accumulates iron, magnesium, and phosphorus.",
    },
    "yarrow": {
        "beneficial": ["cannabis", "herbs"],
        "harmful": [],
        "notes": "Attracts ladybugs, hoverflies, and predatory wasps. Deep roots mine nutrients from subsoil.",
    },
    "lemon_balm": {
        "beneficial": ["cannabis", "fruit_trees"],
        "harmful": [],
        "notes": "Attracts bees and beneficial insects. Citrus scent deters mosquitoes and gnats.",
    },
    "chives": {
        "beneficial": ["cannabis", "carrot", "tomato"],
        "harmful": ["beans", "peas"],
        "notes": "Repels aphids and Japanese beetles. Allium compounds deter many pests.",
    },
    "garlic": {
        "beneficial": ["cannabis", "roses", "fruit_trees"],
        "harmful": ["beans", "peas"],
        "notes": "Strong pest deterrent. Garlic spray is a common organic pesticide. Plant around perimeter.",
    },
    "beans": {
        "beneficial": ["cannabis", "corn", "squash", "marigold"],
        "harmful": ["chives", "garlic", "onion", "fennel"],
        "notes": "Nitrogen-fixing legume. Excellent companion for heavy-feeding cannabis. Bush beans preferred.",
    },
    "cerastium": {
        "beneficial": ["cannabis"],
        "harmful": [],
        "notes": "Snow-in-summer ground cover. Living mulch that retains moisture and suppresses weeds.",
    },
    "fennel": {
        "beneficial": [],
        "harmful": ["cannabis", "tomato", "beans", "most_plants"],
        "notes": "Allelopathic — root exudates inhibit growth of most plants. Keep isolated.",
    },
}


@router.get("", response_model=list[CompanionEntry])
async def list_companions(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Get the full companion planting database."""
    return [
        {"plant": plant, **data}
        for plant, data in COMPANION_DB.items()
    ]


@router.get("/check", response_model=CompatibilityResponse)
async def check_compatibility(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    plant: str = Query(description="Primary plant"),
    neighbor: str = Query(description="Neighboring plant to check"),
):
    """Check compatibility between two plants."""
    plant_lower = plant.lower().replace(" ", "_")
    neighbor_lower = neighbor.lower().replace(" ", "_")

    plant_data = COMPANION_DB.get(plant_lower)
    if plant_data is None:
        return {"plant": plant, "neighbor": neighbor, "compatibility": "unknown", "reason": f"'{plant}' not in database"}

    if neighbor_lower in plant_data["beneficial"]:
        return {"plant": plant, "neighbor": neighbor, "compatibility": "beneficial", "reason": f"{neighbor} is beneficial for {plant}"}
    if neighbor_lower in plant_data["harmful"]:
        return {"plant": plant, "neighbor": neighbor, "compatibility": "harmful", "reason": f"{neighbor} is harmful to {plant}"}

    return {"plant": plant, "neighbor": neighbor, "compatibility": "neutral", "reason": "No known positive or negative interaction"}


@router.get("/suggest", response_model=SuggestResponse)
async def suggest_companions(
    _user: Annotated[CurrentUser, Depends(get_current_user)],
    plant: str = Query(description="Plant to get suggestions for"),
):
    """Suggest beneficial companion plants."""
    plant_lower = plant.lower().replace(" ", "_")
    plant_data = COMPANION_DB.get(plant_lower)

    if plant_data is None:
        # Default to cannabis companions
        plant_data = COMPANION_DB.get("cannabis", {"beneficial": [], "harmful": []})

    suggestions = []
    for companion in plant_data.get("beneficial", []):
        comp_data = COMPANION_DB.get(companion, {})
        suggestions.append({
            "plant": companion.replace("_", " ").title(),
            "notes": comp_data.get("notes", ""),
        })

    return {"plant": plant, "suggestions": suggestions}
