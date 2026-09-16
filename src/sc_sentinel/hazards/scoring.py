"""Conservative heuristic scores; not certified meteorological warnings."""
from __future__ import annotations

def _level(score: float | None) -> str:
    if score is None: return "NOT_ASSESSED"
    if score >= .75: return "HIGH"
    if score >= .4: return "MEDIUM"
    return "LOW"

def score_cell(cell: dict, has_vertical_structure: bool = False, has_validated_rotation: bool = False) -> dict:
    dbzh, area = float(cell["max_dbzh"]), float(cell["area_km2"])
    rain = min(1.0, max(0.0, .55 * (dbzh - 35) / 30 + .45 * min(area / 100, 1)))
    hail_evidence = min(1.0, max(0.0, (dbzh - 50) / 25))
    hail = hail_evidence if has_vertical_structure else min(hail_evidence, .35)
    return {
        "heavy_rain": {"score": round(rain, 3), "level": _level(rain), "label": "heavy-rain potential", "confidence": "limited", "reason": ["CAPPI maximum DBZH", "CAPPI cell area"], "limitations": ["No locally calibrated QPE relationship used"]},
        "hail": {"score": round(hail, 3), "level": _level(hail), "label": "hail potential", "confidence": "limited" if not has_vertical_structure else "moderate", "reason": ["CAPPI maximum DBZH"], "limitations": ([] if has_vertical_structure else ["No validated vertical echo structure/freezing level used; score capped"])},
        "rotation": {"score": None, "level": _level(None), "label": "rotation candidate", "confidence": "not assessed", "reason": [], "limitations": ["No validated dealiased velocity-couplet analysis available"]} if not has_validated_rotation else {"score": 0.0, "level": "LOW", "label": "rotation candidate", "confidence": "limited", "reason": [], "limitations": []},
    }
