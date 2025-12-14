# FoodTracker Gateway API — Implementation Specification

This service is the SINGLE ENTRY POINT for the frontend.
Frontend must never communicate with database or external services directly.

----------------------------------------
GENERAL RULES
----------------------------------------

- Gateway API is stateless.
- Backend is the single source of truth.
- Frontend never computes calories, macros, or totals.
- All numeric validation (steps, tolerance) is enforced here.
- All responses must match contracts in `contracts/api.v1.ts`.

----------------------------------------
SERVICE RESPONSIBILITIES
----------------------------------------

1. Core DB access (PostgreSQL, schema: foodtracker_app)
2. Product search aggregation
3. Nutrition correction handling (event-based)
4. Photo recognition proxying
5. Stats aggregation
6. Validation and business rules

----------------------------------------
DATABASE ACCESS
----------------------------------------

- Use Postgres as primary storage.
- Use SQL views:
  - foodtracker_app.v_meal_items_computed
  - foodtracker_app.v_meal_totals
  - foodtracker_app.v_day_totals

- NEVER store derived totals as table columns.
- NEVER update nutrition directly:
  - all nutrition changes go through INSERT into product_nutrition_events.

----------------------------------------
CORE ENDPOINTS (MUST IMPLEMENT)
----------------------------------------

GET /v1/day/{date}
- Input: ISO date (YYYY-MM-DD)
- Output:
  - day summary (calories + macros)
  - list of meals with computed totals
  - insight text (optional)

POST /v1/meals
- Create empty meal (date, type, time)

GET /v1/meals/{meal_id}
- Return full meal card:
  - items
  - computed totals

DELETE /v1/meals/{meal_id}
- Cascade delete meal + items

POST /v1/meals/{meal_id}/items
- Add product to meal
- Validate grams > 0
- Return computed nutrition for item

PATCH /v1/meals/{meal_id}/items/{item_id}
- Update grams
- Recompute nutrition

DELETE /v1/meals/{meal_id}/items/{item_id}

----------------------------------------
PRODUCTS
----------------------------------------

GET /v1/products/search?q=
- Search products (name-based, case-insensitive)
- Return nutrition_per_100g

POST /v1/products
- Create custom product
- Insert nutrition via product_nutrition_events (source=manual)

PATCH /v1/products/{product_id}/nutrition
- DO NOT update product_nutrition_per_100g directly
- Insert new product_nutrition_event (source=correction)

----------------------------------------
PHOTO RECOGNITION (PROXY)
----------------------------------------

POST /v1/products/recognize-photo
- Input: one or multiple images
- Gateway:
  - forwards images to recognition service
  - receives detected products + estimated nutrition
  - returns structured result to frontend
- Frontend decides what to add

----------------------------------------
SETTINGS
----------------------------------------

GET /v1/settings
PATCH /v1/settings

Validation rules:
- calorie_target step = 50
- calorie_tolerance step = 50
- macro targets step = 5
- if macro_mode = percent → sum must be 100

----------------------------------------
STATS
----------------------------------------

GET /v1/stats?range=7d|14d|30d
- Use v_day_totals
- Compute status per day:
  - under / ok / over based on tolerance

----------------------------------------
ERROR HANDLING
----------------------------------------

- All errors return JSON:
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Human-readable message"
    }
  }

- Never return raw SQL errors to frontend.

----------------------------------------
SECURITY / AUTH (V1 SIMPLIFICATION)
----------------------------------------

- Assume single user (dev mode) OR
- user_id injected via middleware

----------------------------------------
NON-GOALS (DO NOT IMPLEMENT)
----------------------------------------

- No caching layer
- No optimistic updates
- No frontend-side computation
- No direct DB exposure

----------------------------------------
EXPECTED RESULT
----------------------------------------

Frontend can:
- fully log food
- edit meals and products
- view stats
- rely on backend for all calculations

Gateway API encapsulates all business logic and integrations.
