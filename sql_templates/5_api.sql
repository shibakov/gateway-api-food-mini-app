-- 5.1 Main: получить meals + totals за дату
-- :user_id, :date
SELECT
  t.meal_id,
  t.meal_type,
  t.meal_time,
  t.calories,
  t.protein,
  t.fat,
  t.carbs,
  t.items_count
FROM foodtracker_app.v_meal_totals t
WHERE t.user_id = :user_id
  AND t.meal_date = :date
ORDER BY t.meal_time;

--5.2 Meal modal: items computed
-- :meal_id
SELECT *
FROM foodtracker_app.v_meal_items_computed
WHERE meal_id = :meal_id
ORDER BY created_at;

--5.3 Day summary totals + settings targets
-- :user_id, :date
SELECT
  s.calorie_target,
  s.calorie_tolerance,
  s.macro_mode,
  s.protein_target,
  s.fat_target,
  s.carbs_target,
  COALESCE(d.calories, 0) AS consumed_calories,
  COALESCE(d.protein, 0)  AS consumed_protein,
  COALESCE(d.fat, 0)      AS consumed_fat,
  COALESCE(d.carbs, 0)    AS consumed_carbs
FROM foodtracker_app.settings s
LEFT JOIN foodtracker_app.v_day_totals d
  ON d.user_id = s.user_id AND d.day_date = :date
WHERE s.user_id = :user_id;

--5.4 Stats range (7d/14d/30d)
-- :user_id, :date_from, :date_to
SELECT
  day_date AS date,
  calories
FROM foodtracker_app.v_day_totals
WHERE user_id = :user_id
  AND day_date BETWEEN :date_from AND :date_to
ORDER BY day_date;
