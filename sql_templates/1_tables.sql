-- 1.1) Users (минимально: auth позже)
CREATE TABLE IF NOT EXISTS foodtracker_app.users (
  user_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 1.2) Settings (шаги фиксируем здесь)
CREATE TABLE IF NOT EXISTS foodtracker_app.settings (
  user_id           UUID PRIMARY KEY REFERENCES foodtracker_app.users(user_id) ON DELETE CASCADE,

  calorie_target    INT NOT NULL,
  calorie_tolerance INT NOT NULL,

  macro_mode        foodtracker_app.macro_mode NOT NULL DEFAULT 'percent',

  -- targets stored as integers:
  -- if macro_mode='percent' => values are percentages (sum=100)
  -- if macro_mode='grams'   => values are grams targets (still step=5 by your rule)
  protein_target    INT NOT NULL,
  fat_target        INT NOT NULL,
  carbs_target      INT NOT NULL,

  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT settings_calorie_target_step CHECK (calorie_target % 50 = 0 AND calorie_target > 0),
  CONSTRAINT settings_tolerance_step      CHECK (calorie_tolerance % 50 = 0 AND calorie_tolerance BETWEEN 50 AND 250),

  CONSTRAINT settings_macro_step CHECK (
    protein_target % 5 = 0 AND fat_target % 5 = 0 AND carbs_target % 5 = 0
  )
);

-- 1.3) Products
CREATE TABLE IF NOT EXISTS foodtracker_app.products (
  product_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  brand       TEXT NULL,
  is_custom   BOOLEAN NOT NULL DEFAULT FALSE,
  created_by  UUID NULL REFERENCES foodtracker_app.users(user_id) ON DELETE SET NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- optional: prevent duplicates per user for custom products (soft constraint)
  -- you can add unique later if needed
  CONSTRAINT products_name_not_empty CHECK (length(trim(name)) > 0)
);

-- 1.4) Nutrition per 100g (source of truth for computations)
CREATE TABLE IF NOT EXISTS foodtracker_app.product_nutrition_per_100g (
  product_id UUID PRIMARY KEY REFERENCES foodtracker_app.products(product_id) ON DELETE CASCADE,

  calories   INT NOT NULL,
  protein    NUMERIC(6,1) NOT NULL,
  fat        NUMERIC(6,1) NOT NULL,
  carbs      NUMERIC(6,1) NOT NULL,

  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT nutrition_non_negative CHECK (
    calories >= 0 AND protein >= 0 AND fat >= 0 AND carbs >= 0
  )
);

-- 1.5) Meals (per user per date)
CREATE TABLE IF NOT EXISTS foodtracker_app.meals (
  meal_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES foodtracker_app.users(user_id) ON DELETE CASCADE,
  meal_date  DATE NOT NULL,
  meal_type  foodtracker_app.meal_type NOT NULL,
  meal_time  TIME NOT NULL, -- for display (HH:mm)

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- allow multiple meals of same type if you ever want? today we assume one meal per type per day
  CONSTRAINT meals_unique_per_type_day UNIQUE (user_id, meal_date, meal_type)
);

-- 1.6) Meal items (the actual log)
CREATE TABLE IF NOT EXISTS foodtracker_app.meal_items (
  item_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meal_id    UUID NOT NULL REFERENCES foodtracker_app.meals(meal_id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES foodtracker_app.products(product_id) ON DELETE RESTRICT,

  grams      INT NOT NULL,
  added_via  foodtracker_app.added_via NOT NULL DEFAULT 'search',

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT meal_items_grams_positive CHECK (grams > 0)
);

-- 1.7) Optional: per-day insight text (we said text block for now)
CREATE TABLE IF NOT EXISTS foodtracker_app.day_insights (
  user_id    UUID NOT NULL REFERENCES foodtracker_app.users(user_id) ON DELETE CASCADE,
  insight_date DATE NOT NULL,
  text       TEXT NOT NULL,
  severity   foodtracker_app.insight_severity NOT NULL DEFAULT 'neutral',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (user_id, insight_date)
);
