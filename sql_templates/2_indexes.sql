-- Meals lookup by user+date (main screen)
CREATE INDEX IF NOT EXISTS idx_meals_user_date
  ON foodtracker_app.meals (user_id, meal_date);

-- Items by meal (meal modal)
CREATE INDEX IF NOT EXISTS idx_meal_items_meal_id
  ON foodtracker_app.meal_items (meal_id);

-- Product search: simple trigram (optional). If you want better search:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_products_name_trgm ON foodtracker_app.products USING gin (name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_products_name_lower
  ON foodtracker_app.products (lower(name));
