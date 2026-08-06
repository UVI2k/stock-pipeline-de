# dags/stock_pipeline_dag.py

import sys
import os
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extract.alpha_vantage_client import fetch_daily_time_series
from src.transform.clean_time_series import clean_time_series
from src.load.postgres_loader import load_rows

logger = logging.getLogger(__name__)

SYMBOLS = ["AAPL", "MSFT", "GOOGL"]

default_args = {
    "owner": "yuvraj",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    dag_id="stock_pipeline",
    default_args=default_args,
    description="Daily extraction, transform, and load of stock price data",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["portfolio", "etl"],
)


def run_pipeline_for_symbol(symbol: str, **context):
    logger.info(f"Starting pipeline for symbol={symbol}")
    raw_data = fetch_daily_time_series(symbol)
    rows = clean_time_series(raw_data, symbol=symbol)
    count = load_rows(rows)
    logger.info(f"Completed pipeline for symbol={symbol}: {count} rows loaded")
    return count


tasks = {}
for symbol in SYMBOLS:
    tasks[symbol] = PythonOperator(
        task_id=f"pipeline_{symbol.lower()}",
        python_callable=run_pipeline_for_symbol,
        op_kwargs={"symbol": symbol},
        dag=dag,
    )