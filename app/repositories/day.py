from __future__ import annotations

from datetime import date

import asyncpg


DAY_TOTAL_QUERY = """
SELECT date, calories, protein, fat, carbs
FROM foodtracker_app.v_day_totals
WHERE user_id = $1 AND date = $2
"""

MEAL_TOTALS_QUERY = """
SELECT meal_id, meal_type, meal_time, calories, protein, fat, carbs, items_count
FROM foodtracker_app.v_meal_totals
WHERE user_id = $1 AND meal_date = $2
ORDER BY meal_time, meal_type
"""

INSIGHT_QUERY = """
SELECT text, severity
FROM foodtracker_app.day_insights
WHERE user_id = $1 AND insight_date = $2
LIMIT 1
"""

SETTINGS_QUERY = """
SELECT calorie_target, calorie_tolerance, macro_mode, protein_target, fat_target, carbs_target
FROM foodtracker_app.settings
WHERE user_id = $1
LIMIT 1
"""


async def fetch_day_totals(conn: asyncpg.Connection, user_id: str, target_date: date) -> asyncpg.Record | None:
    return await conn.fetchrow(DAY_TOTAL_QUERY, user_id, target_date)


async def fetch_meal_totals(conn: asyncpg.Connection, user_id: str, target_date: date) -> list[asyncpg.Record]:
    return await conn.fetch(MEAL_TOTALS_QUERY, user_id, target_date)


async def fetch_insight(conn: asyncpg.Connection, user_id: str, target_date: date) -> asyncpg.Record | None:
    return await conn.fetchrow(INSIGHT_QUERY, user_id, target_date)


async def fetch_settings(conn: asyncpg.Connection, user_id: str) -> asyncpg.Record:
    record = await conn.fetchrow(SETTINGS_QUERY, user_id)
    if record is None:
        raise ValueError("User settings not found")
    return record
