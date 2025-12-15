CREATE OR REPLACE FUNCTION foodtracker_app.apply_product_nutrition_event()
RETURNS TRIGGER AS $$
BEGIN
  -- upsert current nutrition snapshot
  INSERT INTO foodtracker_app.product_nutrition_per_100g (
    product_id, calories, protein, fat, carbs, updated_at
  )
  VALUES (
    NEW.product_id,
    NEW.calories,
    NEW.protein,
    NEW.fat,
    NEW.carbs,
    NEW.created_at
  )
  ON CONFLICT (product_id) DO UPDATE
  SET
    calories   = EXCLUDED.calories,
    protein    = EXCLUDED.protein,
    fat        = EXCLUDED.fat,
    carbs      = EXCLUDED.carbs,
    updated_at = EXCLUDED.updated_at;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
