from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import pandas as pd
import os
import psycopg2

def wait_for_approval():
    decision = Variable.get("approval_decision", default_var="pending")
    if decision == "pending":
        raise ValueError("Waiting for approval...")
    return decision

def branch_decision(**kwargs):
    decision = Variable.get("approval_decision", default_var="pending")
    return "process_data" if decision == "approved" else "reject_data"

def process_data():
    df = pd.read_excel("/opt/airflow/files/Data.xlsx")
    # Example transformation
    df['processed'] = True
    conn = psycopg2.connect(
        host="postgres", database="analytics", user="airflow", password="airflow"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS processed_data (id SERIAL PRIMARY KEY, data JSONB)")
    for _, row in df.iterrows():
        cursor.execute("INSERT INTO processed_data (data) VALUES (%s)", (row.to_json(),))
    conn.commit()
    cursor.close()
    conn.close()

def send_alert():
    print("Data rejected. Alert sent.")

with DAG("approval_workflow", start_date=days_ago(1), schedule_interval=None, catchup=False) as dag:

    start = EmptyOperator(task_id="start")

    wait = PythonOperator(
        task_id="wait_for_approval",
        python_callable=wait_for_approval,
    )

    branch = BranchPythonOperator(
        task_id="branch_decision",
        python_callable=branch_decision,
        provide_context=True
    )

    approve = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
    )

    reject = PythonOperator(
        task_id="reject_data",
        python_callable=send_alert,
    )

    end = EmptyOperator(task_id="end", trigger_rule='none_failed_min_one_success')

    start >> wait >> branch >> [approve, reject] >> end
