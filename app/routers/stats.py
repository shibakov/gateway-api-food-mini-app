from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Query

from ..dependencies import get_db_connection, get_user_id

from ..errors import ValidationError
from ..repositories import day as day_repo
from ..repositories import stats as stats_repo
from ..schemas.common import Settings, StatsDay, StatsResponse
from ..services.utils import compute_status


router = APIRouter(prefix="/stats", tags=["stats"])


_RANGE_MAP = {"7d": 7, "14d": 14, "30d": 30}


@router.get("", response_model=StatsResponse)
async def get_stats(
    range_: str = Query(..., alias="range"),
    conn=Depends(get_db_connection),
    user_id: str = Depends(get_user_id),
) -> StatsResponse:  # type: ignore[name-defined]
    if range_ not in _RANGE_MAP:
        raise ValidationError("range must be one of 7d, 14d, 30d")

    days = _RANGE_MAP[range_]

    end_date = await conn.fetchval("SELECT CURRENT_DATE")
    start_date = end_date - timedelta(days=days - 1)

    settings_record = await day_repo.fetch_settings(conn, user_id)
    settings = Settings(**dict(settings_record))

    records = await stats_repo.fetch_stats(conn, user_id, start_date, end_date)
    items = [
        StatsDay(
            date=record["date"],
            calories=record["calories"],
            protein=record["protein"],
            fat=record["fat"],
            carbs=record["carbs"],
            status=compute_status(record["calories"], settings),
        )
        for record in records
    ]

    return StatsResponse(range=range_, items=items)
