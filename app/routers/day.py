from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_db_connection, get_user_id
from ..errors import ValidationError
from ..repositories import day as day_repo
from ..schemas.common import DayResponse, Insight, MealSummary, Settings, Summary
from ..services.utils import compute_status, ensure_valid_date

router = APIRouter(tags=["day"])


@router.get("/day/{date}", response_model=DayResponse)
async def get_day(date: str, conn=Depends(get_db_connection), user_id: str = Depends(get_user_id)) -> DayResponse:  # type: ignore[name-defined]
    try:
        target_date = ensure_valid_date(date)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc

    settings_record = await day_repo.fetch_settings(conn, user_id)
    settings = Settings(**dict(settings_record))

    totals_record = await day_repo.fetch_day_totals(conn, user_id, target_date)
    if totals_record:
        summary_totals = Summary(**dict(totals_record), status="ok")
    else:
        summary_totals = Summary(calories=0, protein=0, fat=0, carbs=0, status="ok")

    summary_totals.status = compute_status(summary_totals.calories, settings)

    meal_records = await day_repo.fetch_meal_totals(conn, user_id, target_date)
    meals = [MealSummary(**dict(record)) for record in meal_records]

    insight_record = await day_repo.fetch_insight(conn, user_id, target_date)
    insight = Insight(**dict(insight_record)) if insight_record else None

    return DayResponse(date=target_date, summary=summary_totals, meals=meals, insight=insight)
