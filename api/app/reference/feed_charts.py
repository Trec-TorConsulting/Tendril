"""Nutrient brand feed charts — static reference data for popular nutrient lines."""

from __future__ import annotations

# Each chart is a brand/line with weekly dosing schedule by growth stage.
# ml_per_gallon values; stages: seedling, veg_early, veg_late, transition, flower_early, flower_mid, flower_late, flush

FEED_CHARTS: list[dict] = [
    {
        "brand": "General Hydroponics",
        "line": "Flora Series",
        "medium": ["hydro", "coco", "soil"],
        "products": ["FloraGro", "FloraMicro", "FloraBloom"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"FloraGro": 1.0, "FloraMicro": 1.0, "FloraBloom": 1.0}},
            {"stage": "veg_early", "week": 2, "doses": {"FloraGro": 2.5, "FloraMicro": 2.5, "FloraBloom": 0.5}},
            {"stage": "veg_early", "week": 3, "doses": {"FloraGro": 3.0, "FloraMicro": 2.5, "FloraBloom": 1.0}},
            {"stage": "veg_late", "week": 4, "doses": {"FloraGro": 3.0, "FloraMicro": 3.0, "FloraBloom": 1.0}},
            {"stage": "transition", "week": 5, "doses": {"FloraGro": 2.0, "FloraMicro": 2.5, "FloraBloom": 2.5}},
            {"stage": "flower_early", "week": 6, "doses": {"FloraGro": 1.0, "FloraMicro": 2.5, "FloraBloom": 3.0}},
            {"stage": "flower_mid", "week": 7, "doses": {"FloraGro": 0.5, "FloraMicro": 2.5, "FloraBloom": 3.5}},
            {"stage": "flower_mid", "week": 8, "doses": {"FloraGro": 0.0, "FloraMicro": 2.5, "FloraBloom": 3.5}},
            {"stage": "flower_late", "week": 9, "doses": {"FloraGro": 0.0, "FloraMicro": 2.0, "FloraBloom": 3.5}},
            {"stage": "flush", "week": 10, "doses": {"FloraGro": 0.0, "FloraMicro": 0.0, "FloraBloom": 0.0}},
        ],
        "notes": "pH target: 5.5-6.5 hydro, 6.0-6.8 soil. Always add Micro first.",
    },
    {
        "brand": "Advanced Nutrients",
        "line": "pH Perfect Sensi",
        "medium": ["hydro", "coco"],
        "products": ["Sensi Grow A", "Sensi Grow B", "Sensi Bloom A", "Sensi Bloom B"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"Sensi Grow A": 1.0, "Sensi Grow B": 1.0}},
            {"stage": "veg_early", "week": 2, "doses": {"Sensi Grow A": 2.0, "Sensi Grow B": 2.0}},
            {"stage": "veg_late", "week": 3, "doses": {"Sensi Grow A": 3.0, "Sensi Grow B": 3.0}},
            {"stage": "veg_late", "week": 4, "doses": {"Sensi Grow A": 4.0, "Sensi Grow B": 4.0}},
            {"stage": "transition", "week": 5, "doses": {"Sensi Bloom A": 2.0, "Sensi Bloom B": 2.0}},
            {"stage": "flower_early", "week": 6, "doses": {"Sensi Bloom A": 3.0, "Sensi Bloom B": 3.0}},
            {"stage": "flower_mid", "week": 7, "doses": {"Sensi Bloom A": 4.0, "Sensi Bloom B": 4.0}},
            {"stage": "flower_mid", "week": 8, "doses": {"Sensi Bloom A": 4.0, "Sensi Bloom B": 4.0}},
            {"stage": "flower_late", "week": 9, "doses": {"Sensi Bloom A": 3.0, "Sensi Bloom B": 3.0}},
            {"stage": "flush", "week": 10, "doses": {}},
        ],
        "notes": "pH Perfect auto-adjusts pH 5.5-6.3. No pH adjustment needed.",
    },
    {
        "brand": "Fox Farm",
        "line": "Dirty Dozen",
        "medium": ["soil", "coco"],
        "products": ["Grow Big", "Big Bloom", "Tiger Bloom"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"Big Bloom": 2.0}},
            {"stage": "seedling", "week": 2, "doses": {"Grow Big": 1.0, "Big Bloom": 3.0}},
            {"stage": "veg_early", "week": 3, "doses": {"Grow Big": 2.0, "Big Bloom": 3.0}},
            {"stage": "veg_late", "week": 4, "doses": {"Grow Big": 3.0, "Big Bloom": 4.0}},
            {"stage": "transition", "week": 5, "doses": {"Grow Big": 2.0, "Big Bloom": 4.0, "Tiger Bloom": 1.0}},
            {"stage": "flower_early", "week": 6, "doses": {"Big Bloom": 4.0, "Tiger Bloom": 2.0}},
            {"stage": "flower_mid", "week": 7, "doses": {"Big Bloom": 4.0, "Tiger Bloom": 3.0}},
            {"stage": "flower_mid", "week": 8, "doses": {"Big Bloom": 4.0, "Tiger Bloom": 3.0}},
            {"stage": "flower_late", "week": 9, "doses": {"Big Bloom": 4.0, "Tiger Bloom": 2.0}},
            {"stage": "flush", "week": 10, "doses": {}},
        ],
        "notes": "Flush every 2 weeks in soil. pH target: 6.3-6.8.",
    },
    {
        "brand": "Canna",
        "line": "Coco A+B",
        "medium": ["coco"],
        "products": ["Coco A", "Coco B", "PK 13/14", "Cannazym"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"Coco A": 1.5, "Coco B": 1.5}},
            {"stage": "veg_early", "week": 2, "doses": {"Coco A": 2.5, "Coco B": 2.5, "Cannazym": 2.5}},
            {"stage": "veg_late", "week": 3, "doses": {"Coco A": 3.0, "Coco B": 3.0, "Cannazym": 2.5}},
            {"stage": "veg_late", "week": 4, "doses": {"Coco A": 3.5, "Coco B": 3.5, "Cannazym": 2.5}},
            {"stage": "transition", "week": 5, "doses": {"Coco A": 3.5, "Coco B": 3.5, "Cannazym": 2.5}},
            {"stage": "flower_early", "week": 6, "doses": {"Coco A": 3.5, "Coco B": 3.5, "Cannazym": 2.5}},
            {
                "stage": "flower_mid",
                "week": 7,
                "doses": {
                    "Coco A": 3.0,
                    "Coco B": 3.0,
                    "PK 13/14": 1.5,
                    "Cannazym": 2.5,
                },
            },
            {
                "stage": "flower_mid",
                "week": 8,
                "doses": {
                    "Coco A": 2.5,
                    "Coco B": 2.5,
                    "PK 13/14": 1.5,
                    "Cannazym": 2.5,
                },
            },
            {"stage": "flower_late", "week": 9, "doses": {"Coco A": 2.0, "Coco B": 2.0, "Cannazym": 2.5}},
            {"stage": "flush", "week": 10, "doses": {"Cannazym": 2.5}},
        ],
        "notes": "Always use A+B in equal parts. pH target: 5.8-6.2. Run-off EC < 2.5.",
    },
    {
        "brand": "Athena",
        "line": "Pro Line",
        "medium": ["hydro", "coco"],
        "products": ["Core", "Grow", "Bloom", "PK", "Fade"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"Core": 1.5, "Grow": 2.0}},
            {"stage": "veg_early", "week": 2, "doses": {"Core": 2.5, "Grow": 4.0}},
            {"stage": "veg_late", "week": 3, "doses": {"Core": 3.0, "Grow": 5.0}},
            {"stage": "veg_late", "week": 4, "doses": {"Core": 3.5, "Grow": 6.0}},
            {"stage": "transition", "week": 5, "doses": {"Core": 3.5, "Bloom": 4.0}},
            {"stage": "flower_early", "week": 6, "doses": {"Core": 3.5, "Bloom": 5.0}},
            {"stage": "flower_mid", "week": 7, "doses": {"Core": 3.5, "Bloom": 6.0, "PK": 1.5}},
            {"stage": "flower_mid", "week": 8, "doses": {"Core": 3.5, "Bloom": 6.0, "PK": 2.0}},
            {"stage": "flower_late", "week": 9, "doses": {"Fade": 5.0}},
            {"stage": "flush", "week": 10, "doses": {"Fade": 5.0}},
        ],
        "notes": "Mix Core first. EC target: seedling 1.0, veg 2.0-2.5, flower 2.5-3.2.",
    },
    {
        "brand": "Jack's Nutrients",
        "line": "321",
        "medium": ["hydro", "coco", "soil"],
        "products": ["Part A (5-12-26)", "Calcium Nitrate", "Epsom Salt"],
        "schedule": [
            {"stage": "seedling", "week": 1, "doses": {"Part A": 1.2, "CalNit": 1.0, "Epsom": 0.5}},
            {"stage": "veg_early", "week": 2, "doses": {"Part A": 2.4, "CalNit": 1.9, "Epsom": 1.0}},
            {"stage": "veg_late", "week": 3, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "veg_late", "week": 4, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "transition", "week": 5, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "flower_early", "week": 6, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "flower_mid", "week": 7, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "flower_mid", "week": 8, "doses": {"Part A": 3.6, "CalNit": 2.4, "Epsom": 1.2}},
            {"stage": "flower_late", "week": 9, "doses": {"Part A": 2.4, "CalNit": 1.6, "Epsom": 0.8}},
            {"stage": "flush", "week": 10, "doses": {}},
        ],
        "notes": "3-2-1 ratio by weight (grams). Mix Part A first, then CalNit, then Epsom. pH 5.8-6.2.",
    },
]


def get_all_charts() -> list[dict]:
    """Return all feed charts."""
    return FEED_CHARTS


def get_chart_by_brand(brand: str) -> list[dict]:
    """Return feed charts for a specific brand (case-insensitive)."""
    return [c for c in FEED_CHARTS if c["brand"].lower() == brand.lower()]


def get_brands() -> list[str]:
    """Return list of all available brands."""
    return sorted({c["brand"] for c in FEED_CHARTS})
