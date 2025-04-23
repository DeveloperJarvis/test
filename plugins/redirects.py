# redirects.py

from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from flask_login import current_user
from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_appbuilder.security.decorators import has_access
from airflow.www.app import csrf
import pandas as pd
import os
import sqlite3
import smtplib
from email.message import EmailMessage
import logging

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db_path = '/tmp/airflow_temp.db'

# Initialize DB on first load
def init_db():
    with sqlite3.connect(db_path) as conn:
        # The ID INTEGER PRIMARY KEY tells SQLite to auto-increment ID by default.
        # When no ID value is provided, SQLite automatically assigns one (starting from 1).
        conn.execute("""
            CREATE TABLE IF NOT EXISTS temporary_data (
                ID INTEGER PRIMARY KEY,
                Name TEXT,
                Age INTEGER,
                Department TEXT,
                Contact TEXT,
                Email TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS permanent_data (
                ID INTEGER PRIMARY KEY,
                Name TEXT,
                Age INTEGER,
                Department TEXT,
                Contact TEXT,
                Email TEXT
            )
        """)


init_db()

class UploadReviewView(AppBuilderBaseView):
    route_base = "/data"
    template_folder = os.path.join(os.path.dirname(__file__), "templates")

    @expose("/upload", methods=["GET", "POST"])
    # @has_access
    @csrf.exempt
    def upload(self):
        if request.method == 'POST':
            file = request.files.get('file')
            if not file:
                flash("No file selected", "danger")
                return redirect(url_for('UploadReviewView.upload'))
            try:
                print(f"filename: {file}")
                # df = pd.read_csv(file)
                if file.filename.endswith(".csv"):
                    df = pd.read_csv(file, engine='python')
                elif file.filename.endswith(".xlsx"):
                    df = pd.read_excel(file, engine='openpyxl')  # For .xlsx files
                elif file.filename.endswith(".xls"):
                    df = pd.read_excel(file, engine='xlrd')  # For .xls files
                print(f"[INFO] df: {df}")
            except Exception as e:
                flash("Error reading file.", "danger")
                logging.error(f"Upload error: {e}")
                return redirect(url_for('UploadReviewView.upload'))

            # required_columns = {'name', 'age'}
            # if not required_columns.issubset(df.columns):
            #     flash("Invalid CSV format. 'name' and 'age' columns are required.", "danger")
            #     return redirect(url_for('UploadReviewView.upload'))

            with sqlite3.connect(db_path) as conn:
                existing_cols = pd.read_sql("SELECT * FROM temporary_data LIMIT 0", conn).columns
                if 'ID' in df.columns:
                    df = df.drop(columns=['ID'])  # Prevent conflicts with auto-increment ID
                df = df[[col for col in df.columns if col in existing_cols and col != 'ID']]
                df.to_sql('temporary_data', conn, if_exists='append', index=False)


            flash('File uploaded successfully.', 'success')
        return self.render_template('upload.html')

    @expose("/review", methods=["GET"])
    # @has_access
    def review(self):
        # with sqlite3.connect(db_path) as conn:
        #     df = pd.read_sql_query("SELECT * FROM temporary_data WHERE status='pending'", conn)
        # return self.render_template('review.html', data=df.to_dict(orient='records'))
        # No need to fetch data or render separately
        return redirect(url_for('HelloView.role_based_home'))

    @expose("/approve/<int:id>", methods=["POST"])
    # @has_access
    @csrf.exempt
    def approve(self, id):
        with sqlite3.connect(db_path) as conn:
            # Since you don’t insert ID into permanent_data, SQLite auto-generates it.
            # This keeps ID sequences unique and avoids accidental duplication or overrides.
            row = conn.execute(
                "SELECT Name, Age, Department, Contact, Email FROM temporary_data WHERE ID=?",
                (id,)
            ).fetchone()

            if row:
                conn.execute(
                    "INSERT INTO permanent_data (Name, Age, Department, Contact, Email) VALUES (?, ?, ?, ?, ?)",
                    row
                )
                conn.execute("DELETE FROM temporary_data WHERE ID=?", (id,))
                flash(f"Row {id} approved.", 'success')
            else:
                flash(f"Row {id} not found.", 'danger')

        # return redirect(url_for('UploadReviewView.review'))
        return redirect(url_for('HelloView.role_based_home'))

    @expose("/reject/<int:id>", methods=["POST"])
    # @has_access
    @csrf.exempt
    def reject(self, id):
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("SELECT name FROM temporary_data WHERE id=?", (id,)).fetchone()
            if row:
                conn.execute("DELETE FROM temporary_data WHERE id=?", (id,))
                msg = EmailMessage()
                msg.set_content(f"Row {id} with name {row[0]} was rejected.")
                msg['Subject'] = 'Data Rejection Notification'
                msg['From'] = 'airflow@example.com'
                msg['To'] = 'data.team@example.com'

                try:
                    with smtplib.SMTP('mailhog', 1025) as server:
                        server.send_message(msg)
                except Exception as e:
                    print(f"Email failed: {e}")

                flash(f"Row {id} rejected and notified.", 'warning')
            else:
                flash(f"Row {id} not found.", 'danger')
        # return redirect(url_for('UploadReviewView.review'))
        return redirect(url_for('HelloView.role_based_home'))

class DataUIPlugin(AirflowPlugin):
    name = "data_ui_plugin"
    appbuilder_views = [
        {
            "name": "Upload & Review",
            "category": "Data Tools",
            "view": UploadReviewView()
        }
    ]
