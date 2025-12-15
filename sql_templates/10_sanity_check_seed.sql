SELECT *
FROM foodtracker_app.v_meal_items_computed
ORDER BY meal_id;

SELECT *
FROM foodtracker_app.v_meal_totals
ORDER BY meal_time;

SELECT *
FROM foodtracker_app.v_day_totals
WHERE user_id = '00000000-0000-0000-0000-000000000001';
