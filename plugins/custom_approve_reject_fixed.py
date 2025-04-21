# views.py

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

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bp = Blueprint("data_ui", __name__, template_folder="templates", static_folder="static")

db_path = '/tmp/airflow_temp.db'

# Initialize DB on first load
def init_db():
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS temporary_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS permanent_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER
            )
        """)

init_db()

# class CustomHomeView(AppBuilderBaseView):
#     default_view = "other"
#     template_folder = os.path.join(os.path.dirname(__file__), "custom_home", "templates")

#     @expose('/')
#     def home(self):
#         if not current_user.is_authenticated:
#             return redirect('/login/')
#         if current_user.username == "test":
#             return self.render_template("home_analyst.html", user=current_user)
#         else:
#             return redirect(url_for('Airflow.index'))

@bp.route('/upload', methods=['GET', 'POST'])
@has_access
@csrf.exempt
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash("No file selected", "danger")
            return redirect(url_for('data_ui.upload'))
        try:
            df = pd.read_csv(file)
        except Exception:
            flash("Error reading CSV file.", "danger")
            return redirect(url_for('data_ui.upload'))

        required_columns = {'name', 'age'}
        if not required_columns.issubset(df.columns):
            flash("Invalid CSV format. 'name' and 'age' columns are required.", "danger")
            return redirect(url_for('data_ui.upload'))

        with sqlite3.connect(db_path) as conn:
            df.to_sql('temporary_data', conn, if_exists='append', index=False)
        flash('File uploaded successfully.', 'success')
    return render_template('upload.html')

@bp.route('/review', methods=['GET'])
@has_access
def review():
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM temporary_data WHERE status='pending'", conn)
    return render_template('review.html', data=df.to_dict(orient='records'))

@bp.route('/approve/<int:id>', methods=['POST'])
@has_access
@csrf.exempt
def approve(id):
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT name, age FROM temporary_data WHERE id=?", (id,)).fetchone()
        if row:
            conn.execute("INSERT INTO permanent_data (name, age) VALUES (?, ?)", row)
            conn.execute("DELETE FROM temporary_data WHERE id=?", (id,))
            flash(f"Row {id} approved.", 'success')
        else:
            flash(f"Row {id} not found.", 'danger')
    return redirect(url_for('data_ui.review'))

@bp.route('/reject/<int:id>', methods=['POST'])
@has_access
@csrf.exempt
def reject(id):
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
    return redirect(url_for('data_ui.review'))

# Register the plugin with Airflow
class DataUIPlugin(AirflowPlugin):
    name = "data_ui_plugin"
    flask_blueprints = [bp]
