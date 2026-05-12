import os
from dotenv import load_dotenv

load_dotenv()

CITIES = [
    {
        "city_name": "Caen",
        "latitude": "49.1859",
        "longitude": "-0.3591",
        "country": "France",
    },
    {
        "city_name": "Paris",
        "latitude": "48.8534",
        "longitude": "2.3488",
        "country": "France",
    },
    {
        "city_name": "Nice",
        "latitude": "43.7031",
        "longitude": "7.2661",
        "country": "France",
    },
    {
        "city_name": "Rennes",
        "latitude": "48.1111",
        "longitude": "-1.6743",
        "country": "France",
    },
    {
        "city_name": "Rouen",
        "latitude": "49.4431",
        "longitude": "1.0993",
        "country": "France",
    },
    {
        "city_name": "Bordeaux",
        "latitude": "44.8412",
        "longitude": "-0.5805",
        "country": "France",
    },
]
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "relative_humidity_2m_mean",
    "weather_code",
]
TIMEZONE = "Europe/Berlin"
BIGQUERY_RAW_TABLE = "weather-pipeline-495522.weather_raw.daily_weather"
BIGQUERY_TEST_TABLE = "weather-pipeline-495522.weather_test.daily_weather"
