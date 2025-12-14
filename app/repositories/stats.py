from __future__ import annotations

from datetime import date

import asyncpg

STATS_QUERY = """
SELECT date, calories, protein, fat, carbs
FROM foodtracker_app.v_day_totals
WHERE user_id = $1 AND date BETWEEN $2 AND $3
ORDER BY date
"""


async def fetch_stats(conn: asyncpg.Connection, user_id: str, start_date: date, end_date: date) -> list[asyncpg.Record]:
    return await conn.fetch(STATS_QUERY, user_id, start_date, end_date)
