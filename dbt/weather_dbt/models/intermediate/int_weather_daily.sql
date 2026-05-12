{{ config(materialized='table') }}

WITH deduplicated AS (
    SELECT
        city,
        date,
        temp_max_c,
        temp_min_c,
        temp_mean_c,
        precipitation_mm,
        windspeed_max_kmh,
        humidity_pct,
        weather_code,
        ingested_at,
        ROW_NUMBER() OVER (
            PARTITION BY city, date
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM {{ ref('stg_weather') }}
)

SELECT
    city,
    date,
    temp_max_c,
    temp_min_c,
    temp_mean_c,
    precipitation_mm,
    windspeed_max_kmh,
    humidity_pct,
    weather_code,
    ROUND(temp_max_c - temp_min_c, 2) AS temp_range_c,
    CAST(CASE
        WHEN precipitation_mm > 1.0 THEN TRUE
        ELSE FALSE
    END AS BOOLEAN) AS is_rainy,
    ROUND(temp_mean_c - 0.55*(1 - humidity_pct/100.0)*(temp_mean_c - 14.5), 2) AS heat_index_c,
    ingested_at
FROM deduplicated
WHERE row_num = 1