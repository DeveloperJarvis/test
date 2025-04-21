# from airflow.plugins_manager import AirflowPlugin
# from flask_appbuilder import BaseView as AppBuilderBaseView, expose
# from flask_login import current_user, login_required
# from flask import Blueprint, redirect, render_template
# import os
# import sqlite3

# # Blueprint for redirecting /home or /
# hello_blueprint = Blueprint('hello_blueprint', __name__)

# @hello_blueprint.route('/')
# @hello_blueprint.route('/home')
# def redirect_home():
#     return redirect('/hello/')  # Triggers role-based view

# db_path = '/tmp/airflow_temp.db'  # Same DB as used in upload/review logic

# class HelloView(AppBuilderBaseView):
#     route_base = "/hello"
#     default_view = "role_based_home"
#     template_folder = os.path.join(os.path.dirname(__file__), "custom_home", "templates")

#     @expose("/")
#     @login_required
#     def role_based_home(self):
#         roles = [role.name for role in current_user.roles]

#         if "DataAnalyst" in roles:
#             # Fetch datasets for display
#             with sqlite3.connect(db_path) as conn:
#                 pending = conn.execute("SELECT * FROM temporary_data").fetchall()
#                 approved = conn.execute("SELECT * FROM permanent_data").fetchall()

#             return self.render_template(
#                 "home_analyst.html",
#                 user=current_user,
#                 pending_data=pending,
#                 approved_data=approved
#             )

#         elif "Op" in roles:
#             return self.render_template("home_ops.html", user=current_user)

#         elif "Public" in roles:
#             return self.render_template("public_home.html", user=current_user)

#         else:
#             return self.render_template("default_home.html", user=current_user)


# class HelloPlugin(AirflowPlugin):
#     name = "hello_plugin"
#     appbuilder_views = [
#         {
#             "name": "Hello Dashboard",
#             "category": "Custom",
#             "view": HelloView()
#         }
#     ]
#     flask_blueprints = [hello_blueprint]
