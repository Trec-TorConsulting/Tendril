"""Companion planting reference data — used only by seed scripts."""

from __future__ import annotations

# Format: {plant: {beneficial: [...], harmful: [...], notes: str}}
COMPANION_DB: dict[str, dict] = {
    "cannabis": {
        "beneficial": [
            "basil",
            "marigold",
            "lavender",
            "chamomile",
            "dill",
            "peppermint",
            "sunflower",
            "clover",
            "alfalfa",
            "yarrow",
            "lemon_balm",
            "chives",
            "garlic",
            "beans",
            "cerastium",
        ],
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
        "notes": (
            "Repels nematodes, whiteflies, and aphids. Root exudates kill soil nematodes."
            " French marigolds are most effective."
        ),
    },
    "lavender": {
        "beneficial": ["cannabis", "rosemary"],
        "harmful": [],
        "notes": "Attracts pollinators, repels fleas, moths, and mice. Excellent aromatic pest deterrent.",
    },
    "chamomile": {
        "beneficial": ["cannabis", "basil", "wheat"],
        "harmful": [],
        "notes": (
            "Accumulates calcium, potassium, and sulfur. Improves soil when composted. Attracts beneficial insects."
        ),
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
