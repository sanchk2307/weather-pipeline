import argparse
from datetime import datetime, timedelta
from config import CITIES, BIGQUERY_RAW_TABLE
from load import (
    get_bigquery_client,
    get_existing_dates,
    rows_to_dataframe,
    load_to_bigquery,
)
from extract import fetch_city_weather
from util import get_date_ranges

parser = argparse.ArgumentParser()
parser.add_argument(
    "--start",
    help="Pass the start date in YYYY-MM-DD (defaults to the previous day)",
    default=(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
)
parser.add_argument(
    "--end",
    help="Pass the end date in YYYY-MM-DD (defaults to the previous day)",
    default=(datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
)

args = parser.parse_args()

start_date = datetime.strptime(args.start, "%Y-%m-%d").date()
end_date = datetime.strptime(args.end, "%Y-%m-%d").date()
if start_date > end_date:
    raise ValueError("'--start' cannot be after '--end'")


bigquery_client = get_bigquery_client()
loaded_rows = 0
for city in CITIES:
    try:
        existing_dates = get_existing_dates(
            city["city_name"], BIGQUERY_RAW_TABLE, bigquery_client
        )
        date_ranges = get_date_ranges(start_date, end_date, existing_dates)
        city_rows = 0
        for date_range in date_ranges:
            try:
                rows = fetch_city_weather(city, date_range[0], date_range[1])
                df = rows_to_dataframe(rows)
                load_to_bigquery(df, BIGQUERY_RAW_TABLE, bigquery_client)
                city_rows += len(df)
            except Exception as err:
                print(
                    f"[ERROR] Failed to load data for {city['city_name']} in the range: {date_range} - {err}"
                )
        loaded_rows += city_rows
    except Exception as err:
        print(f"[ERROR] Failed to load data for {city['city_name']} entirely - {err}")

print("=====================SUMMARY=====================")
print(f"Rows loaded: {loaded_rows}")
