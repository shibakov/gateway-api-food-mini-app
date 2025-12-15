DROP TRIGGER IF EXISTS trg_apply_nutrition_event
  ON foodtracker_app.product_nutrition_events;

CREATE TRIGGER trg_apply_nutrition_event
AFTER INSERT ON foodtracker_app.product_nutrition_events
FOR EACH ROW
EXECUTE FUNCTION foodtracker_app.apply_product_nutrition_event();
