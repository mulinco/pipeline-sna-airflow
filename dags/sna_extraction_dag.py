from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
import pendulum

with DAG(
    dag_id="sna_extraction_pipeline",
    start_date=pendulum.datetime(2025, 8, 27, tz="America/Sao_Paulo"),
    schedule_interval="@daily",
    catchup=False,
    tags=["sna"],
) as dag:
    run_scraper_task = BashOperator(
        task_id="run_sna_scraper",
        bash_command="python include/scraper_ws.py",
    )
