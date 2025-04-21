# import os
from pathlib import Path
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime
from airflow.utils.dates import days_ago

def fetch_data(**kwargs):
    """Fetch data from files in the directory."""
    try:
        directory_path = './files'  # Directory with the files
        # files = os.listdir(directory_path)
        files = Path(directory_path).glob("*")
        print("Files in directory:", files)

        # Initialize a dataframe to hold the data
        combined_df = pd.DataFrame()

        for file in files:
            print(file)
            # full_file_path = os.path.join(directory_path, file)
            full_file_path = directory_path.joinpath(file)
            if file.endswith(".csv"):
                df = pd.read_csv(full_file_path, engine='python')
            elif file.endswith(".xlsx"):
                df = pd.read_excel(full_file_path, engine='openpyxl')  # For .xlsx files
            elif file.endswith(".xls"):
                df = pd.read_excel(full_file_path, engine='xlrd')  # For .xls files
            else:
                continue
            
            print(f"Data from {file}:")
            print(df.head())  # Display the first few rows of data
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Push the combined dataframe to XCom for use in the approval step
        kwargs['ti'].xcom_push(key='data', value=combined_df)

    except Exception as e:
        print(f"Error reading files: {e}")
        raise

def approve_data(**kwargs):
    """Approve or Reject the fetched data."""
    # Pull the data from XCom
    df = kwargs['ti'].xcom_pull(task_ids='fetch_data', key='data')

    # Show the first few rows of the data for approval/rejection
    print("Data for approval:")
    print(df.head())  # Show a preview of the data to the user

    # Implement your approval logic here. For now, we'll just simulate approval.
    if df.empty:
        print("No data to approve.")
        return 'rejected_task'  # If data is empty, reject it

    # Simulate approval or rejection
    # You can modify this to get the decision dynamically from the UI (for example, via an XCom push from the UI)
    decision = 'approved'  # This would be dynamic in a real-world scenario

    if decision == 'approved':
        return 'load_data'  # Proceed with data loading
    else:
        return 'alert_rejection'  # Reject and alert the user

def load_data(**kwargs):
    """Simulate loading data into the database."""
    df = kwargs['ti'].xcom_pull(task_ids='fetch_data', key='data')
    print("Loading data into the database...")
    print(df.head())  # Display data that would be loaded
    # Implement actual database loading logic here (e.g., use psycopg2 to load data into PostgreSQL)
    
    return "Data loaded successfully."

def alert_rejection():
    """Simulate sending an alert when the data is rejected."""
    print("Alert: Data has been rejected.")


dag = DAG(
    'approval_rejection_dag',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2025, 4, 11),
        'retries': 1,
    },
    description='A workflow with approval and rejection tasks',
    schedule_interval=None,
    catchup=False,
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Fetch data task
fetch = PythonOperator(
    task_id='fetch_data',
    python_callable=fetch_data,
    provide_context=True,
    dag=dag,
)

# Approve/reject data task
approve = PythonOperator(
    task_id='approve_data',
    python_callable=approve_data,
    provide_context=True,
    dag=dag,
)

# Load data into database if approved
load = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

# Alert task if rejected
alert = PythonOperator(
    task_id='alert_rejection',
    python_callable=alert_rejection,
    dag=dag,
)

# Task dependencies
start >> fetch >> approve
approve >> [load, alert]
