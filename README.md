# Gateway API Overview

## Проект
- FastAPI сервис с модульной структурой (`app/main.py`, `routers/`, `repositories/`, `schemas/`, `services/`).
- Настройки через `app/config.py` + `pydantic-settings`, фиксированный `user_id` (dev mode). `requirements.txt` / `requirements-dev.txt` описывают зависимости.

## База и репозитории
- Подключение `asyncpg` через пул (`app/db.py`), доступ к connection: `app/dependencies.py`.
- Репозитории работают с `foodtracker_app` схемой и вьюхами (`v_day_totals`, `v_meal_totals`, `v_meal_items_computed`, `v_day_totals`, `settings`, `day_insights`).
- Все изменения нутриентов происходят через `product_nutrition_events` (manual/correction), расчётные данные из вьюх.

## Эндпоинты
- `/v1/day/{date}` — сводка дня, калории, статус, инсайт.
- `/v1/meals` + `/v1/meals/{id}` + `/v1/meals/{id}/items` — создание, получение, добавление/редактирование/удаление.
- `/v1/products/search` — поиск по имени, `/v1/products` создание + запись nutrition event, `/v1/products/{id}/nutrition` запись correction.
- `/v1/products/recognize-photo` — stub, возвращает `{status: "not_implemented", results: []}`.
- `/v1/settings` GET/PATCH с валидацией шагов (ккал±50, макро±5, проценты=100).
- `/v1/stats?range=` — диапазоны 7/14/30 дней, статус based on tolerance.

## Валидация и ошибки
- Pydantic схемы (`app/schemas/common.py`) контролируют шаги, макросы, суммы, поля запросов/ответов, реагируют через `ValidationError`.
- Общая структура ошибок в `app/errors.py`, глобальный exception handler в `app/main.py`.
- Утилиты: `app/services/utils.py` (статус/дата).

## Тесты
- `tests/test_utils.py` (статус и валидация даты).
- `tests/test_settings_validation.py` (macro sum, steps).
- Запуск: `pytest` (сначала `pip install -r requirements-dev.txt`).

## Как подцепить фронт
1. Настроить `.env`/переменную `DATABASE_URL`, указывающую на `foodtracker_app`.
2. `uvicorn app.main:app --reload` запускает API.
3. Фронт обращается к `/v1/...` маршрутам, никаких дополнительных мостов не требуется.

## Запуск тестов
```bash
pip install -r requirements-dev.txt
pytest
```

## Railway deployment checklist
1. **Service topology**
   - Один сервис `gateway-api` и один PostgreSQL `foodtracker-db`.
   - `gateway-api` получает `DATABASE_URL` из Railway и использует его в `app.config.Settings.database_url`.
2. **Переменные окружения**
   - `DATABASE_URL` (Railway inject).
   - `ENV` / `APP_ENV` (например, `production`).
   - `PORT` (Railway inject).
   - `LOG_LEVEL` (по умолчанию `INFO`).
   - `CORS_ORIGINS` (добавьте список origin-ов, разделённых запятыми).
   - `ENABLE_DOCS=false` чтобы отключать Swagger/Redoc в prod.
   - Pool/timeouts: `DB_POOL_MIN_SIZE`, `DB_POOL_MAX_SIZE`, `DB_POOL_TIMEOUT`, `DB_COMMAND_TIMEOUT`.
3. **Запуск**
   - Railway использует Railpack (Nixpacks):
     - Создайте файл `.python-version` со значением `3.11.9`, чтобы Railpack не поднимал Python 3.13, несовместимый с `asyncpg 0.29`.`.
     - Укажите Start Command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   - Если Docker: убедитесь, что образ устанавливает зависимости и запускает Uvicorn на `$PORT`.
4. **Хелсчек**
   - `GET /healthz` (без DB) → `{ok: true}`.
   - `GET /readyz` (проверяет пул, возвращает 503 если база недоступна).
5. **CORS**
   - Перечисленные origins потребуются для фронта.
   - `allow_methods` / `allow_headers` настроены на `"*"`, `allow_credentials` = `false`.
6. **База и таймауты**
   - `asyncpg.create_pool` использует значения из env `DB_POOL_*`.
   - Пул min 1–2, max 5–10, `timeout` около 5s, `command_timeout` около 10s.
7. **Smoke checklist**
   - `GET /healthz`.
   - `GET /v1/settings` (dev user).
   - `GET /v1/day/{today}`.
   - `POST /v1/meals`.
   - `POST /v1/meals/{meal_id}/items`.
   - `PATCH /v1/products/{id}/nutrition`.
   - Проверить CORS для фронта.
