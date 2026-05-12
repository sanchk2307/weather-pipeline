{{ config(materialized='table') }}

SELECT
    city,
    date,
    temp_max_c,
    temp_min_c,
    temp_mean_c,
    temp_range_c,
    precipitation_mm,
    windspeed_max_kmh,
    humidity_pct,
    weather_code,
    is_rainy,
    ROUND(AVG(temp_max_c) OVER seven_day, 2) as seven_day_rolling_avg_temp_max_c,
    ROUND(AVG(temp_min_c) OVER seven_day, 2) as seven_day_rolling_avg_temp_min_c,
    ROUND(AVG(temp_mean_c) OVER seven_day, 2) as seven_day_rolling_avg_temp_mean_c,
    ROUND(AVG(temp_range_c) OVER seven_day, 2) as seven_day_rolling_avg_temp_range_c,
    ROUND(AVG(precipitation_mm) OVER seven_day, 2) as seven_day_rolling_avg_precipitation_mm,
    ROUND(AVG(windspeed_max_kmh) OVER seven_day, 2) as seven_day_rolling_avg_windspeed_max_kmh,
    ROUND(AVG(humidity_pct) OVER seven_day, 2) as seven_day_rolling_avg_humidity_pct,
    ROUND(AVG(heat_index_c) OVER seven_day, 2) as seven_day_rolling_avg_heat_index_c,
    ingested_at
FROM {{ ref('int_weather_daily') }}

WINDOW seven_day AS (
    PARTITION BY city
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
)