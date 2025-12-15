-- A1) Create dev user
INSERT INTO foodtracker_app.users (user_id)
VALUES ('00000000-0000-0000-0000-000000000001')
ON CONFLICT DO NOTHING;

-- A2) Default settings
INSERT INTO foodtracker_app.settings (
  user_id,
  calorie_target,
  calorie_tolerance,
  macro_mode,
  protein_target,
  fat_target,
  carbs_target
)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  1900,
  100,
  'percent',
  30,
  35,
  35
)
ON CONFLICT (user_id) DO UPDATE
SET
  calorie_target = EXCLUDED.calorie_target,
  calorie_tolerance = EXCLUDED.calorie_tolerance,
  macro_mode = EXCLUDED.macro_mode,
  protein_target = EXCLUDED.protein_target,
  fat_target = EXCLUDED.fat_target,
  carbs_target = EXCLUDED.carbs_target;

-- A3) Base products
INSERT INTO foodtracker_app.products (product_id, name, brand, is_custom)
VALUES
  ('10000000-0000-0000-0000-000000000001', 'Chicken Breast', NULL, false),
  ('10000000-0000-0000-0000-000000000002', 'Oatmeal', NULL, false),
  ('10000000-0000-0000-0000-000000000003', 'Banana', NULL, false),
  ('10000000-0000-0000-0000-000000000004', 'Olive Oil', NULL, false),
  ('10000000-0000-0000-0000-000000000005', 'Greek Yogurt', NULL, false)
ON CONFLICT DO NOTHING;

-- A4) Initial nutrition events
INSERT INTO foodtracker_app.product_nutrition_events (
  product_id, calories, protein, fat, carbs, source
)
VALUES
  ('10000000-0000-0000-0000-000000000001', 165, 31.0, 3.6, 0.0, 'seed'),
  ('10000000-0000-0000-0000-000000000002', 379, 13.0, 6.5, 67.0, 'seed'),
  ('10000000-0000-0000-0000-000000000003', 89, 1.1, 0.3, 23.0, 'seed'),
  ('10000000-0000-0000-0000-000000000004', 884, 0.0, 100.0, 0.0, 'seed'),
  ('10000000-0000-0000-0000-000000000005', 59, 10.0, 0.4, 3.6, 'seed');

-- A5) Meals for today
INSERT INTO foodtracker_app.meals (
  meal_id, user_id, meal_date, meal_type, meal_time
)
VALUES
  ('20000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', CURRENT_DATE, 'breakfast', '08:00'),
  ('20000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', CURRENT_DATE, 'lunch', '13:30'),
  ('20000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', CURRENT_DATE, 'dinner', '19:00')
ON CONFLICT DO NOTHING;

-- A6) Breakfast items
INSERT INTO foodtracker_app.meal_items (
  meal_id, product_id, grams, added_via
)
VALUES
  ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000002', 60, 'search'),
  ('20000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000003', 120, 'search');

-- A6.2) Lunch items
INSERT INTO foodtracker_app.meal_items (
  meal_id, product_id, grams, added_via
)
VALUES
  ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 200, 'search'),
  ('20000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000004', 10, 'manual');

-- A6.3) Dinner items
INSERT INTO foodtracker_app.meal_items (
  meal_id, product_id, grams, added_via
)
VALUES
  ('20000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000001', 180, 'search');


