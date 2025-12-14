from __future__ import annotations

import asyncpg

GET_SETTINGS_QUERY = """
SELECT calorie_target, calorie_tolerance, macro_mode, protein_target, fat_target, carbs_target
FROM foodtracker_app.settings
WHERE user_id = $1
"""

UPDATE_SETTINGS_QUERY = """
UPDATE foodtracker_app.settings
SET calorie_target = $2,
    calorie_tolerance = $3,
    macro_mode = $4,
    protein_target = $5,
    fat_target = $6,
    carbs_target = $7
WHERE user_id = $1
RETURNING user_id
"""


async def get_settings(conn: asyncpg.Connection, user_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow(GET_SETTINGS_QUERY, user_id)


async def update_settings(
    conn: asyncpg.Connection,
    user_id: str,
    calorie_target: int,
    calorie_tolerance: int,
    macro_mode: str,
    protein_target: int,
    fat_target: int,
    carbs_target: int,
) -> bool:
    record = await conn.fetchrow(
        UPDATE_SETTINGS_QUERY,
        user_id,
        calorie_target,
        calorie_tolerance,
        macro_mode,
        protein_target,
        fat_target,
        carbs_target,
    )
    return record is not None
