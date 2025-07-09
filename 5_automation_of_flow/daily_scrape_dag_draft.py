from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Default args for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=10)
}

# Define the DAG
with DAG(
    dag_id='daily_scraping_and_update',
    default_args=default_args,
    description='Scrape data daily and update dashboard',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
) as dag:

    def run_scraping_general_info():
        os.system("python3 ../1_data_collection/extracting_company_data/scraping_general_info.py")

    def run_scraping_review_classes():
        os.system("python3 ../1_data_collection/extracting_company_data/scraping_review_classes.py")

    def run_review_table():
        os.system("python3 ../1_data_collection/reviews_extracting/review_table.py")

    task1 = PythonOperator(
        task_id='scrape_general_info',
        python_callable=run_scraping_general_info
    )

    task2 = PythonOperator(
        task_id='scrape_reviews',
        python_callable=run_scraping_review_classes
    )

    task3 = PythonOperator(
        task_id='build_review_table',
        python_callable=run_review_table
    )

    task1 >> task2 >> task3  # Set task order
