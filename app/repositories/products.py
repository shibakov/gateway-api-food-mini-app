from __future__ import annotations

from typing import Sequence

import asyncpg

SEARCH_PRODUCTS_QUERY = """
SELECT p.product_id,
       p.name,
       p.brand,
       n.calories,
       n.protein,
       n.fat,
       n.carbs
FROM foodtracker_app.products AS p
JOIN foodtracker_app.product_nutrition_per_100g AS n ON n.product_id = p.product_id
WHERE LOWER(p.name) LIKE LOWER($1)
ORDER BY p.name
LIMIT 25
"""

CREATE_PRODUCT_QUERY = """
INSERT INTO foodtracker_app.products (product_id, name, brand, is_custom, created_by)
VALUES (gen_random_uuid(), $1, $2, true, $3)
RETURNING product_id
"""

INSERT_NUTRITION_EVENT_QUERY = """
INSERT INTO foodtracker_app.product_nutrition_events (event_id, product_id, calories, protein, fat, carbs, source)
VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6)
RETURNING event_id
"""


async def search_products(conn: asyncpg.Connection, query: str) -> Sequence[asyncpg.Record]:
    pattern = f"%{query.lower()}%"
    return await conn.fetch(SEARCH_PRODUCTS_QUERY, pattern)


async def create_product(conn: asyncpg.Connection, name: str, brand: str | None, user_id: str) -> str:
    record = await conn.fetchrow(CREATE_PRODUCT_QUERY, name, brand, user_id)
    return str(record["product_id"])


async def insert_nutrition_event(
    conn: asyncpg.Connection,
    product_id: str,
    calories: int,
    protein: float,
    fat: float,
    carbs: float,
    source: str,
) -> str:
    record = await conn.fetchrow(INSERT_NUTRITION_EVENT_QUERY, product_id, calories, protein, fat, carbs, source)
    return str(record["event_id"])
