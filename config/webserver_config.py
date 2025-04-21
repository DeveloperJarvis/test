# config/webserver_config.py

from flask import redirect
from airflow.www.views import Airflow
from flask_appbuilder import expose
from flask_login import current_user

class CustomIndexView(Airflow):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login/')
        user_roles = [role.name for role in current_user.roles]
        if 'DataAnalyst' in user_roles:
            return redirect('/hello/')
        return super().index()

FAB_INDEX_VIEW = "config.CustomIndexView"  # this string is dynamically imported
