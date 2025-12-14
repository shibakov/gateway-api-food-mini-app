# FoodTracker — Gateway API Implementation Guide

This document provides a step-by-step implementation guide for the FoodTracker Gateway API.
It MUST be used together with `GATEWAY_API_SPEC.md`.

The goal is to implement a backend service that fully satisfies frontend needs,
acts as a single source of truth, and encapsulates all business logic.

--------------------------------------------------
GENERAL PRINCIPLES
--------------------------------------------------

- Gateway API is the ONLY interface used by frontend.
- Frontend never computes calories, macros, or totals.
- All computed values come from database views.
- All nutrition changes are append-only events.
- All logic must be deterministic and reproducible.

--------------------------------------------------
TECH STACK (RECOMMENDED)
--------------------------------------------------

- Language: Python 3.11+
- Framework: FastAPI
- DB access: asyncpg or SQLAlchemy Core (no ORM models)
- Migrations: optional (DDL already defined)
- Auth: single-user dev mode OR injected user_id middleware

--------------------------------------------------
COMMON CONTEXT
--------------------------------------------------

- DB schema: foodtracker_app
- User (dev): user_id = '00000000-0000-0000-0000-000000000001'
- All dates: ISO format YYYY-MM-DD

--------------------------------------------------
ENDPOINT IMPLEMENTATION DETAILS
--------------------------------------------------

==================================================
1. GET /v1/day/{date}
==================================================

PURPOSE:
Return full Main screen data for a specific date.

INPUT:
- date (path): ISO date

STEPS:
1. Validate date format.
2. Fetch day totals from foodtracker_app.v_day_totals.
3. Fetch meals list from foodtracker_app.v_meal_totals.
4. Fetch optional insight from foodtracker_app.day_insights.
5. Fetch user settings from foodtracker_app.settings.
6. Determine calorie status:
   - under / ok / over based on target ± tolerance.
7. Assemble response.

SQL:
- v_day_totals
- v_meal_totals
- day_insights
- settings

OUTPUT STRUCTURE:
{
  date,
  summary: { calories, protein, fat, carbs, status },
  meals: [
    { meal_id, meal_type, meal_time, calories, protein, fat, carbs, items_count }
  ],
  insight: { text, severity } | null
}

==================================================
2. POST /v1/meals
==================================================

PURPOSE:
Create a new empty meal.

INPUT:
{
  date,
  meal_type,
  meal_time
}

STEPS:
1. Validate meal_type enum.
2. Insert into foodtracker_app.meals.
3. Return meal_id.

==================================================
3. GET /v1/meals/{meal_id}
==================================================

PURPOSE:
Return full meal modal data.

STEPS:
1. Fetch meal totals from v_meal_totals.
2. Fetch items from v_meal_items_computed.
3. Order items by created_at.
4. Assemble response.

OUTPUT:
{
  meal: { meal_id, meal_type, meal_time, totals },
  items: [ { item_id, name, grams, calories, protein, fat, carbs, added_via } ]
}

==================================================
4. DELETE /v1/meals/{meal_id}
==================================================

PURPOSE:
Delete meal and all items.

STEPS:
1. Delete from foodtracker_app.meals.
2. Rely on ON DELETE CASCADE.
3. Return ok.

==================================================
5. POST /v1/meals/{meal_id}/items
==================================================

PURPOSE:
Add product to meal.

INPUT:
{
  product_id,
  grams,
  added_via
}

STEPS:
1. Validate grams > 0.
2. Insert into foodtracker_app.meal_items.
3. Fetch computed item from v_meal_items_computed.
4. Return item payload.

==================================================
6. PATCH /v1/meals/{meal_id}/items/{item_id}
==================================================

PURPOSE:
Update grams of existing item.

STEPS:
1. Validate grams > 0.
2. Update foodtracker_app.meal_items.
3. Fetch updated computed item.
4. Return updated payload.

==================================================
7. DELETE /v1/meals/{meal_id}/items/{item_id}
==================================================

PURPOSE:
Remove product from meal.

STEPS:
1. Delete from foodtracker_app.meal_items.
2. Return ok.

==================================================
8. GET /v1/products/search
==================================================

PURPOSE:
Search products by name.

INPUT:
- q (query string)

STEPS:
1. Lowercase search.
2. Query foodtracker_app.products joined with product_nutrition_per_100g.
3. Return top N results.

==================================================
9. POST /v1/products
==================================================

PURPOSE:
Create custom product.

INPUT:
{
  name,
  brand,
  nutrition_per_100g
}

STEPS:
1. Insert into products (is_custom=true).
2. Insert nutrition into product_nutrition_events (source='manual').
3. Trigger updates snapshot table.
4. Return product_id.

==================================================
10. PATCH /v1/products/{product_id}/nutrition
==================================================

PURPOSE:
Correct nutrition values.

IMPORTANT:
- NEVER update snapshot directly.

STEPS:
1. Insert new row into product_nutrition_events.
2. Trigger updates snapshot.
3. Return ok.

==================================================
11. POST /v1/products/recognize-photo
==================================================

PURPOSE:
Proxy photo recognition.

STEPS:
1. Accept image(s).
2. Forward to recognition service.
3. Receive detected products + estimates.
4. Return structured result.
5. Do NOT persist automatically.

==================================================
12. GET /v1/settings
==================================================

PURPOSE:
Return user settings.

STEPS:
1. Fetch from foodtracker_app.settings.
2. Return as-is.

==================================================
13. PATCH /v1/settings
==================================================

PURPOSE:
Update user settings.

VALIDATION:
- calorie_target % 50 = 0
- tolerance % 50 = 0
- macro targets % 5 = 0
- if macro_mode=percent → sum = 100

STEPS:
1. Validate input.
2. Update settings.
3. Return ok.

==================================================
14. GET /v1/stats
==================================================

PURPOSE:
Return stats for period.

INPUT:
- range = 7d | 14d | 30d

STEPS:
1. Compute date_from.
2. Query v_day_totals.
3. For each day:
   - compute status using tolerance.
4. Return list for chart rendering.

--------------------------------------------------
ERROR FORMAT (MANDATORY)
--------------------------------------------------

All errors must be returned as:

{
  "error": {
    "code": "VALIDATION_ERROR | NOT_FOUND | INTERNAL",
    "message": "Human readable message"
  }
}

--------------------------------------------------
NON-GOALS
--------------------------------------------------

- No frontend computation
- No caching layer
- No direct DB exposure
- No optimistic updates
- No business logic in frontend

--------------------------------------------------
EXPECTED RESULT
--------------------------------------------------

A clean, deterministic Gateway API that:
- fully supports frontend UX
- guarantees data integrity
- enables analytics and future growth
