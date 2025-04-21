from airflow.plugins_manager import AirflowPlugin
from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from flask_login import current_user
from flask import redirect
import os


class HelloView(AppBuilderBaseView):
    route_base = "/hello"
    default_view = "role_based_home"  # 👈 Add this line
    template_folder = os.path.join(os.path.dirname(__file__), "custom_home", "templates")

    @expose("/")
    def role_based_home(self):
        if not current_user.is_authenticated:
            return redirect('/login/')

        roles = [role.name for role in current_user.roles]

        if "DataAnalyst" in roles:
            return self.render_template("home_analyst.html", user=current_user)
        elif "Op" in roles:
            return self.render_template("home_ops.html", user=current_user)
        elif "Public" in roles:
            return self.render_template("public_home.html", user=current_user)
        # else:
        #     return self.render_template("default_home.html", user=current_user)


class HelloPlugin(AirflowPlugin):
    name = "hello_plugin"
    appbuilder_views = [
        {
            "name": "Hello Dashboard",
            "category": "Custom",
            "view": HelloView()
        }
    ]
