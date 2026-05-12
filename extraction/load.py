from google.cloud import bigquery
import pandas as pd
from datetime import datetime

RAW_WEATHER_SCHEMA = [
    bigquery.SchemaField(name="city", field_type="STRING", mode="REQUIRED"),
    bigquery.SchemaField(name="date", field_type="DATE", mode="REQUIRED"),
    bigquery.SchemaField(name="temp_max", field_type="FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField(name="temp_min", field_type="FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField(name="temp_mean", field_type="FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField(
        name="precipitation_mm", field_type="FLOAT64", mode="NULLABLE"
    ),
    bigquery.SchemaField(name="windspeed_max", field_type="FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField(name="humidity_mean", field_type="FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField(name="weather_code", field_type="INTEGER", mode="NULLABLE"),
    bigquery.SchemaField(name="ingested_at", field_type="TIMESTAMP", mode="REQUIRED"),
]


def get_bigquery_client():
    return bigquery.Client()


def rows_to_dataframe(rows):
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["ingested_at"] = pd.to_datetime(df["ingested_at"])
    return df


def load_to_bigquery(df, table_id, client):
    config = bigquery.LoadJobConfig(
        schema=RAW_WEATHER_SCHEMA, write_disposition="WRITE_APPEND"
    )
    load_job = client.load_table_from_dataframe(df, table_id, job_config=config)
    load_job.result()
    return load_job


def get_existing_dates(city, table_id, client):
    query = f"SELECT DISTINCT date FROM `{table_id}` WHERE city = '{city}'"
    query_job = client.query(query)
    results = query_job.result()
    existing_dates = []
    for row in results:
        existing_dates.append(row.date)
    return existing_dates


# Testing load
if __name__ == "__main__":
    from config import BIGQUERY_RAW_TABLE

    client = get_bigquery_client()
    test_rows = [
        {
            "city": "Caen",
            "date": "2025-01-01",
            "temp_max": 20.1,
            "temp_min": 10.5,
            "temp_mean": 15.3,
            "precipitation_mm": 0.0,
            "windspeed_max": 12.0,
            "humidity_mean": 65.0,
            "weather_code": 63,
            "ingested_at": datetime.utcnow(),
        }
    ]
    df = rows_to_dataframe(test_rows)
    load_to_bigquery(df, BIGQUERY_RAW_TABLE, client)
