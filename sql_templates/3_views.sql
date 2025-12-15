CREATE OR REPLACE VIEW foodtracker_app.v_meal_items_computed AS
SELECT
  mi.item_id,
  mi.meal_id,
  mi.product_id,
  mi.grams,
  mi.added_via,
  p.name,
  p.brand,
  p.is_custom,

  -- computed per item
  ROUND((n.calories * mi.grams) / 100.0)::INT AS calories,
  ROUND((n.protein  * mi.grams) / 100.0, 1) AS protein,
  ROUND((n.fat      * mi.grams) / 100.0, 1) AS fat,
  ROUND((n.carbs    * mi.grams) / 100.0, 1) AS carbs

FROM foodtracker_app.meal_items mi
JOIN foodtracker_app.products p
  ON p.product_id = mi.product_id
JOIN foodtracker_app.product_nutrition_per_100g n
  ON n.product_id = mi.product_id;

CREATE OR REPLACE VIEW foodtracker_app.v_meal_totals AS
SELECT
  m.meal_id,
  m.user_id,
  m.meal_date,
  m.meal_type,
  m.meal_time,

  COALESCE(SUM(v.calories), 0)::INT AS calories,
  COALESCE(ROUND(SUM(v.protein), 1), 0.0) AS protein,
  COALESCE(ROUND(SUM(v.fat), 1), 0.0) AS fat,
  COALESCE(ROUND(SUM(v.carbs), 1), 0.0) AS carbs,

  COUNT(v.item_id)::INT AS items_count

FROM foodtracker_app.meals m
LEFT JOIN foodtracker_app.v_meal_items_computed v
  ON v.meal_id = m.meal_id
GROUP BY m.meal_id, m.user_id, m.meal_date, m.meal_type, m.meal_time;

CREATE OR REPLACE VIEW foodtracker_app.v_day_totals AS
SELECT
  m.user_id,
  m.meal_date AS day_date,

  COALESCE(SUM(t.calories), 0)::INT AS calories,
  COALESCE(ROUND(SUM(t.protein), 1), 0.0) AS protein,
  COALESCE(ROUND(SUM(t.fat), 1), 0.0) AS fat,
  COALESCE(ROUND(SUM(t.carbs), 1), 0.0) AS carbs

FROM foodtracker_app.meals m
JOIN foodtracker_app.v_meal_totals t
  ON t.meal_id = m.meal_id
GROUP BY m.user_id, m.meal_date;

