-- 0.1) Create schema
CREATE SCHEMA IF NOT EXISTS foodtracker_app;

-- 0.2) Extensions (uuid generation)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 0.3) Enums
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
                 WHERE n.nspname='foodtracker_app' AND t.typname='meal_type') THEN
    CREATE TYPE foodtracker_app.meal_type AS ENUM ('breakfast','lunch','dinner','snack');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
                 WHERE n.nspname='foodtracker_app' AND t.typname='macro_mode') THEN
    CREATE TYPE foodtracker_app.macro_mode AS ENUM ('percent','grams');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
                 WHERE n.nspname='foodtracker_app' AND t.typname='added_via') THEN
    CREATE TYPE foodtracker_app.added_via AS ENUM ('search','manual','label','photo');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
                 WHERE n.nspname='foodtracker_app' AND t.typname='insight_severity') THEN
    CREATE TYPE foodtracker_app.insight_severity AS ENUM ('positive','neutral','warning');
  END IF;
END $$;
