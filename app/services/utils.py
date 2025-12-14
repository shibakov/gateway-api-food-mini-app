from __future__ import annotations

from datetime import date

from ..schemas.common import Settings


def compute_status(calories: int, settings: Settings) -> str:
    lower = settings.calorie_target - settings.calorie_tolerance
    upper = settings.calorie_target + settings.calorie_tolerance
    if calories < lower:
        return "under"
    if calories > upper:
        return "over"
    return "ok"


def ensure_valid_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Date must be in ISO format YYYY-MM-DD") from exc
