from __future__ import annotations

from datetime import time
from typing import Any

import asyncpg


CREATE_MEAL_QUERY = """
INSERT INTO foodtracker_app.meals (meal_id, user_id, meal_date, meal_type, meal_time)
VALUES (gen_random_uuid(), $1, $2, $3, $4)
RETURNING meal_id
"""

GET_MEAL_QUERY = """
SELECT meal_id, meal_type, meal_time, calories, protein, fat, carbs
FROM foodtracker_app.v_meal_totals
WHERE user_id = $1 AND meal_id = $2
"""

GET_MEAL_ITEMS_QUERY = """
SELECT v.item_id, v.name, v.grams, v.calories, v.protein, v.fat, v.carbs, v.added_via
FROM foodtracker_app.v_meal_items_computed AS v
JOIN foodtracker_app.meals AS m ON m.meal_id = v.meal_id
JOIN foodtracker_app.meal_items AS mi ON mi.item_id = v.item_id
WHERE m.user_id = $1 AND v.meal_id = $2
ORDER BY mi.created_at
"""

DELETE_MEAL_QUERY = """
DELETE FROM foodtracker_app.meals
WHERE user_id = $1 AND meal_id = $2
RETURNING meal_id
"""

CREATE_ITEM_QUERY = """
INSERT INTO foodtracker_app.meal_items (item_id, meal_id, product_id, grams, added_via)
VALUES (gen_random_uuid(), $1, $2, $3, $4)
RETURNING item_id
"""

GET_ITEM_QUERY = """
SELECT v.item_id, v.name, v.grams, v.calories, v.protein, v.fat, v.carbs, v.added_via
FROM foodtracker_app.v_meal_items_computed AS v
JOIN foodtracker_app.meals AS m ON m.meal_id = v.meal_id
WHERE m.user_id = $1 AND v.item_id = $2
"""

UPDATE_ITEM_QUERY = """
UPDATE foodtracker_app.meal_items
SET grams = $1
WHERE user_id = $2 AND meal_id = $3 AND item_id = $4
RETURNING item_id
"""

DELETE_ITEM_QUERY = """
DELETE FROM foodtracker_app.meal_items
WHERE user_id = $1 AND meal_id = $2 AND item_id = $3
RETURNING item_id
"""


async def create_meal(conn: asyncpg.Connection, user_id: str, meal_date: str, meal_type: str, meal_time: time) -> str:
    record = await conn.fetchrow(CREATE_MEAL_QUERY, user_id, meal_date, meal_type, meal_time)
    return str(record["meal_id"])


async def get_meal(conn: asyncpg.Connection, user_id: str, meal_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow(GET_MEAL_QUERY, user_id, meal_id)


async def get_meal_items(conn: asyncpg.Connection, user_id: str, meal_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(GET_MEAL_ITEMS_QUERY, user_id, meal_id)


async def delete_meal(conn: asyncpg.Connection, user_id: str, meal_id: str) -> bool:
    record = await conn.fetchrow(DELETE_MEAL_QUERY, user_id, meal_id)
    return record is not None


async def create_meal_item(
    conn: asyncpg.Connection, user_id: str, meal_id: str, product_id: str, grams: int, added_via: str | None
) -> str:
    record = await conn.fetchrow(CREATE_ITEM_QUERY, user_id, meal_id, product_id, grams, added_via)
    return str(record["item_id"])


async def get_meal_item(conn: asyncpg.Connection, user_id: str, item_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow(GET_ITEM_QUERY, user_id, item_id)


async def update_meal_item(conn: asyncpg.Connection, user_id: str, meal_id: str, item_id: str, grams: int) -> bool:
    record = await conn.fetchrow(UPDATE_ITEM_QUERY, grams, user_id, meal_id, item_id)
    return record is not None


async def delete_meal_item(conn: asyncpg.Connection, user_id: str, meal_id: str, item_id: str) -> bool:
    record = await conn.fetchrow(DELETE_ITEM_QUERY, user_id, meal_id, item_id)
    return record is not None
