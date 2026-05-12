{{ config(materialized='view') }}

SELECT
    city,
    CAST(date AS DATE) AS date,
    CAST(temp_max AS FLOAT64) AS temp_max_c,
    CAST(temp_min AS FLOAT64) AS temp_min_c,
    CAST(temp_mean AS FLOAT64) AS temp_mean_c,
    CAST(precipitation_mm AS FLOAT64) AS precipitation_mm,
    CAST(windspeed_max AS FLOAT64) AS windspeed_max_kmh,
    CAST(humidity_mean AS FLOAT64) AS humidity_pct,
    CAST(weather_code AS INTEGER) AS weather_code,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at
FROM {{ source('weather_raw','daily_weather') }}
WHERE date IS NOT NULL AND city IS NOT NULL