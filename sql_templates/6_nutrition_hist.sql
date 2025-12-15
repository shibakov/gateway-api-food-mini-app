-- 6.1) Nutrition history (append-only)
CREATE TABLE IF NOT EXISTS foodtracker_app.product_nutrition_events (
  event_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id  UUID NOT NULL REFERENCES foodtracker_app.products(product_id) ON DELETE CASCADE,

  calories    INT NOT NULL,
  protein     NUMERIC(6,1) NOT NULL,
  fat         NUMERIC(6,1) NOT NULL,
  carbs       NUMERIC(6,1) NOT NULL,

  source      TEXT NOT NULL, -- 'manual', 'label', 'photo', 'correction'
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT nutrition_event_non_negative CHECK (
    calories >= 0 AND protein >= 0 AND fat >= 0 AND carbs >= 0
  )
);
