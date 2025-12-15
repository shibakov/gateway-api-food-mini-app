CREATE OR REPLACE FUNCTION foodtracker_app.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_settings_updated_at ON foodtracker_app.settings;
CREATE TRIGGER trg_settings_updated_at
BEFORE UPDATE ON foodtracker_app.settings
FOR EACH ROW EXECUTE FUNCTION foodtracker_app.set_updated_at();

DROP TRIGGER IF EXISTS trg_nutrition_updated_at ON foodtracker_app.product_nutrition_per_100g;
CREATE TRIGGER trg_nutrition_updated_at
BEFORE UPDATE ON foodtracker_app.product_nutrition_per_100g
FOR EACH ROW EXECUTE FUNCTION foodtracker_app.set_updated_at();

DROP TRIGGER IF EXISTS trg_day_insights_updated_at ON foodtracker_app.day_insights;
CREATE TRIGGER trg_day_insights_updated_at
BEFORE UPDATE ON foodtracker_app.day_insights
FOR EACH ROW EXECUTE FUNCTION foodtracker_app.set_updated_at();


-----------


CREATE OR REPLACE FUNCTION foodtracker_app.validate_settings()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.macro_mode = 'percent' THEN
    IF (NEW.protein_target + NEW.fat_target + NEW.carbs_target) <> 100 THEN
      RAISE EXCEPTION 'Macro percent targets must sum to 100. Got %',
        (NEW.protein_target + NEW.fat_target + NEW.carbs_target);
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_settings_validate ON foodtracker_app.settings;
CREATE TRIGGER trg_settings_validate
BEFORE INSERT OR UPDATE ON foodtracker_app.settings
FOR EACH ROW EXECUTE FUNCTION foodtracker_app.validate_settings();
