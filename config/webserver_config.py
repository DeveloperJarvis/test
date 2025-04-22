# config/webserver_config.py

from flask import redirect
from airflow.www.views import Airflow
from flask_appbuilder import expose
from flask_login import current_user
import logging

class CustomIndexView(Airflow):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login/')
        
        # Log role check
        roles = [role.name for role in current_user.roles]
        logging.info(f"[INFO] CustomIndexView: User roles: {roles}")  # Add this for debugging

        if 'DataAnalyst' in roles:
            return redirect('/hello/')
        
        return super().index()


# IMPORTANT: this must be the dot‑path to the CustomIndexView class
FAB_INDEX_VIEW = "config.CustomIndexView"
