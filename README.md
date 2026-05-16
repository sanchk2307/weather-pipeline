# Weather Analytics Pipeline

A production-style ETL pipeline that ingests weather data for French cities, transforms it through a medallion architecture, validates data quality and orchestrates everything with Apache Airflow.

## Architecture

```
Open-Meteo API
         │
         ▼
┌───────────────────┐
│   Python Extract  │  Fetches daily weather for 6 French cities
│   & Load (EL)     │  Idempotent — skips already-loaded dates
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  BigQuery Raw     │  weather_raw.daily_weather
│  (Bronze Layer)   │  Append-only, explicit schema
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Great            │  Validates raw data before transformation
│  Expectations     │  Column existence, nulls, ranges, city set
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  dbt Transform    │  Staging → Intermediate → Marts
│  (Silver & Gold)  │  Deduplication, derived fields, aggregations
└────────┬──────────┘
         │
         ├──► weather_dbt.stg_weather           (view)
         ├──► weather_dbt.int_weather_daily      (table)
         ├──► weather_dbt.mart_city_weather_daily (table)
         └──► weather_dbt.mart_city_weather_monthly (table)
         │
         ▼
┌───────────────────┐
│  Apache Airflow   │  Orchestrates full pipeline daily
│  (Docker)         │  extract_and_load → run_gx_validation → run_dbt_models → test_dbt_models
└───────────────────┘
```

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.13 | Extraction and loading |
| Google BigQuery | 3.41.0 | Cloud data warehouse |
| dbt Core | 1.11.9 | SQL transformations |
| Apache Airflow | 3.2.1 | Orchestration |
| Great Expectations | 1.17.1 | Data quality validation |
| Docker | - | Airflow environment |
| Open-Meteo API | - | Weather data |

## Project Structure

```
weather-pipeline/
├─extraction/
│ ├─config.py                               # Cities, API constants, BigQuery table refs
│ ├─extract.py                              # API fetch and JSON parsing
│ ├─load.py                                 # BigQuery schema and load functions
│ ├─main.py                                 # Entry point: accepts --start and --end args
│ └─util.py                                 # Date range helper (idempotency logic)
├─gx/                                       # Great Expectations config and results
├─dbt/
│ └─weather_dbt/
│   └─models/
│     ├─staging/
│     │ ├─stg_weather.sql                   # Clean types, rename columns
│     │ └─stg_weather.yml                   # Column tests
│     ├─intermediate/
│     │ ├─int_weather_daily.sql             # Deduplicate, derived fields
│     │ └─int_weather_daily.yml             # Uniqueness tests
│     └─marts/
│       ├─mart_city_weather_daily.sql       # 7-day rolling aggregates
│       └─mart_city_weather_monthly.sql     # Monthly aggregates and city ranking
├─airflow/
│ ├─dags/
│ │ └─weather_pipeline_dag.py               # Airflow DAG definition
│ └─docker-compose.yaml                     # Airflow services
├─validate_weather.py                       # Data quality checkpoint runner
├─requirements.txt
├─.gitignore
└─docs/
```

## Data Models

### Bronze - `weather_raw.daily_weather`
Raw daily weather loaded directly from Open-Meteo. Append-only with explicit BigQuery schema.

| Column | Type | Description |
|--------|------|-------------|
| city | STRING | City name |
| date | DATE | Observation date |
| temp_max | FLOAT64 | Max temperature (C) |
| temp_min | FLOAT64 | Min temperature (C) |
| temp_mean | FLOAT64 | Mean temperature (C) |
| precipitation_mm | FLOAT64 | Total precipitation (mm) |
| windspeed_max | FLOAT64 | Max wind speed (km/h) |
| humidity_mean | FLOAT64 | Mean relative humidity (%) |
| weather_code | INTEGER | WMO weather code |
| ingested_at | TIMESTAMP | Load timestamp |

### Silver - `weather_dbt.int_weather_daily`
Deduplicated dailt records with derived fields.
Added columns: `temp_range_c`, `is_rainy`, `heat_index_c`

### Gold - `weather_dbt.mart_city_weather_daily`
Daily records enriched with 7-day rolling aggregates for all metrics.

### Gold - `weather_dbt.mart_city_weather_monthly`
Monthly aggregations per city including total rainfall, average temperature, rainy day counts and city temperature rankings.

## Setup

### Prerequisites
- Python 3.8+
- Google Cloud account with BigQuery enabled
- Docker Desktop
- A GCP service account JSON key with BigQuery Admin role

### 1. Clone and create virtual environment

```bash
git clone https://github.com/sanchk2307/weather-pipeline.git
cd weather-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/gcp_keyfile.json
```

### 3. Create BigQuery datasets

In the GCP console, create two datasets in your preferred region:
- `weather_raw`
- `weather_dbt`

Update `extraction/config.py` with your GCP project ID.

### 4. Configure dbt

Create `dbt/profiles.yml`:

```yaml
weather_dbt:
  outputs:
    dev:
      type: bigquery
      method: service-account
      keyfile: "{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}"
      project: your-gcp-project-id
      dataset: weather_dbt
      location: your-region
      threads: 4
  target: dev
```

### 5. Set up Airflow

```bash
cd airflow
echo "AIRFLOW_UID=50000" > .env
echo "_PIP_ADDITIONAL_REQUIREMENTS=dbt-bigquery" >> .env
docker compose up airflow-init
docker compose up -d
```

Open http://localhost:8080 (login: `airflow` / `airflow`)

## Running the Pipeline

### Manual backfill

```bash
cd extraction
python main.py --start 2024-01-01 --end 2024-12-31
```

### Run dbt transformations

```bash
cd dbt/weather_dbt
dbt run
dbt test
```

### Run data quality validation

```bash
python validate_weather.py
```

### Trigger via Airflow

Enable the `weather_pipeline` DAG in the Airflow UI and trigger a manual run, or let it run automatically on its `@daily` schedule.

The DAG runs four tasks in sequence:
1. `extract_and_load` — fetches yesterday's weather data for all 6 cities
2. `run_gx_validation` — validates the raw data against the Great Expectations suite (column existence, nulls, value ranges, known cities)
3. `run_dbt_models` — rebuilds all dbt models (staging → intermediate → marts)
4. `test_dbt_models` — runs all dbt schema tests (not_null, uniqueness)