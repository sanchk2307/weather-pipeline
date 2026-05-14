from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
import subprocess

default_args = {
    "owner": "sanch",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_feature": False,
}


def run_extract_and_load(**args):
    execution_date = args["ds"]
    subprocess.run(
        [
            "python",
            "/opt/airflow/extraction/main.py",
            "--start",
            execution_date,
            "--end",
            execution_date,
        ],
        check=True,
    )


with DAG(
    "weather_pipeline",
    default_args=default_args,
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:
    extract_and_load = PythonOperator(
        task_id="extract_and_load", python_callable=run_extract_and_load
    )
    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command="cd /opt/airflow/dbt/weather_dbt && dbt run",
    )
    test_dbt_models = BashOperator(
        task_id="test_dbt_models",
        bash_command="cd /opt/airflow/dbt/weather_dbt && dbt test",
    )

    extract_and_load >> run_dbt_models >> test_dbt_models
