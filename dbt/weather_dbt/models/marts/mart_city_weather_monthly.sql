{{ config(materialized='table') }}

WITH monthly_metrics AS (
    SELECT
        city,
        DATE_TRUNC(date, MONTH) as month,
        ROUND(AVG(temp_max_c), 2) as monthly_avg_temp_max_c,
        ROUND(AVG(temp_min_c), 2) as monthly_avg_temp_min_c,
        ROUND(AVG(temp_mean_c), 2) as monthly_avg_temp_mean_c,
        ROUND(AVG(temp_range_c), 2) as monthly_avg_temp_range_c,
        SUM(precipitation_mm) AS monthly_total_rainfall_mm,
        MAX(windspeed_max_kmh) AS monthly_max_windspeed_kmh,
        ROUND(AVG(humidity_pct), 2) AS monthly_avg_humidity_pct,
        COUNTIF(is_rainy) as rainy_days_count,
        ROUND(AVG(heat_index_c), 2) AS monthly_avg_heat_index_c
    FROM {{ ref('int_weather_daily') }}
    GROUP BY city, month
)

SELECT
    city,
    month,
    EXTRACT(MONTH from month) AS month_number,
    EXTRACT(YEAR from month) AS year,
    monthly_avg_temp_max_c,
    monthly_avg_temp_min_c,
    monthly_avg_temp_mean_c,
    monthly_avg_temp_range_c,
    monthly_total_rainfall_mm,
    monthly_max_windspeed_kmh,
    monthly_avg_humidity_pct,
    rainy_days_count,
    monthly_avg_heat_index_c,
    RANK() OVER (
        PARTITION BY month
        ORDER BY monthly_avg_temp_mean_c DESC
    ) as city_rank_temp
FROM monthly_metrics