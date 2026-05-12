from config import DAILY_VARIABLES, BASE_URL
import requests
from datetime import datetime


def build_api_params(lat, lon, start_date, end_date):
    return {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "Europe/Berlin",
    }


def fetch_weather_data(lat, lon, start_date, end_date):
    r = requests.get(BASE_URL, params=build_api_params(lat, lon, start_date, end_date))
    if r.status_code != 200:
        raise Exception(f"LOG: Status: {r.status_code}, {r.text}")
    return r.json()


def parse_response(response_json, city_name):
    daily = response_json["daily"]
    time = daily["time"]
    zipped_arr = zip(daily["time"], *(daily[k] for k in DAILY_VARIABLES))
    ingested_at = datetime.utcnow()
    parsed_response = []
    for el in zipped_arr:
        parsed_response.append(
            {
                "city": city_name,
                "date": el[0],
                "temp_max": el[1],
                "temp_min": el[2],
                "temp_mean": el[3],
                "precipitation_mm": el[4],
                "windspeed_max": el[5],
                "humidity_mean": el[6],
                "weather_code": el[7],
                "ingested_at": ingested_at,
            }
        )
    return parsed_response


def fetch_city_weather(city_dict, start_date, end_date):
    weather_api_response = fetch_weather_data(
        city_dict["latitude"], city_dict["longitude"], start_date, end_date
    )
    return parse_response(weather_api_response, city_dict["city_name"])


# Testing extraction
if __name__ == "__main__":
    from config import CITIES

    rows = fetch_city_weather(CITIES[0], "2025-01-01", "2025-01-07")
    print(f"Got {len(rows)} rows")
    print(rows[0])
