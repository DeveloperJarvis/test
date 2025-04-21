from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.operators.dummy_operator import DummyOperator
import os
import pandas as pd
import psycopg2

def wait_for_approval(**kwargs):
    ti = kwargs['ti']
    approval_status = ti.xcom_pull(task_ids='approval_input_task', key='approval_status')

    if approval_status == 'approved':
        print("Approval received. Proceeding with the task.")
        return 'approved_task'
    elif approval_status == 'rejected':
        print("Rejection received. Stopping the task.")
        return 'rejected_task'
    else:
        print("Waiting for approval...")
        return 'waiting_for_approval'

def fetch_data():
    # Load data from Excel file
    try:
        print("fetch_data execute..")
        # Define the path to the directory you want to access
        # directory_path = config.directory_path
        directory_path = './files'

        # List all files in the directory
        files = os.listdir(directory_path)
        print("Files in directory:", files)

        for file in files:
            print(file)
            full_file_path = os.path.join(directory_path, file)
            if file.endswith(".csv"):
                df = pd.read_csv(full_file_path, engine='python')
            elif file.endswith(".xlsx"):
                df = pd.read_excel(full_file_path, engine='openpyxl') # For .xlsx files
            elif file.endswith(".xls"):
                df = pd.read_excel(directory_path, engine='xlrd')  # For .xls files
            print(df)
            # updated_df = df[df['Contact'].notnull()]
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")


def process_data(**kwargs):
    print("Processing data after approval.")

def send_alert(**kwargs):
    print("Sending alert after rejection.")

dag = DAG(
    'approval_rejection_dag',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2025, 4, 11),
        'retries': 1,
    },
    description='A workflow with approval and rejection tasks',
    schedule_interval=None,
)

start = DummyOperator(task_id='start', dag=dag)

approval_input_task = PythonOperator(
    task_id='approval_input_task',
    python_callable=wait_for_approval,
    provide_context=True,
    dag=dag,
)

approved_task = PythonOperator(
    task_id='approved_task',
    python_callable=process_data,
    provide_context=True,
    dag=dag,
)

rejected_task = PythonOperator(
    task_id='rejected_task',
    python_callable=send_alert,
    provide_context=True,
    dag=dag,
)

start >> approval_input_task >> [approved_task, rejected_task]
