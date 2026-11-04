"""Transparent roll-up: weighted mean of the six sub-scores, N/A weights redistributed.
Same bands as Signum: red >= 65 highly concerning, amber >= 40 worth checking, green low concern."""
from __future__ import annotations

DIMENSIONS = [
    {"key": "visual", "label": "Visual similarity", "weight": 0.30},
    {"key": "aural", "label": "Aural similarity", "weight": 0.10},
    {"key": "conceptual", "label": "Conceptual similarity", "weight": 0.15},
    {"key": "goods_services", "label": "Goods and services proximity", "weight": 0.15},
    {"key": "distinctiveness", "label": "Distinctiveness of the client mark", "weight": 0.15},
    {"key": "bad_faith", "label": "Imitation signals", "weight": 0.15},
]
RED, AMBER = 65.0, 40.0
BAND_LABELS = {"red": "Highly concerning", "amber": "Worth checking", "green": "Low concern", "unscored": "Not assessed"}


def band_for(score: float) -> str:
    return "red" if score >= RED else "amber" if score >= AMBER else "green"


def roll_up(breakdown: list[dict]) -> float:
    active = [d for d in breakdown if not d.get("na")]
    total = sum(d["weight"] for d in active) or 1.0
    return round(sum(d["score"] * d["weight"] / total for d in active), 1)
