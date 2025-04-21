# config/create_roles.py
# from airflow.www.security_manager import AirflowSecurityManager
from airflow.www.security_manager import AirflowSecurityManagerV2
from airflow.www.app import create_app
from flask_appbuilder.security.sqla.models import Role, PermissionView
from flask_appbuilder.security.manager import BaseSecurityManager

app = create_app()

with app.app_context():
    # sm: AirflowSecurityManager = app.appbuilder.sm
    sm: AirflowSecurityManagerV2 = app.appbuilder.sm


    def create_role(role_name: str, perms: list[tuple[str, str]]):
        existing_role = sm.find_role(role_name)
        if existing_role:
            print(f"🔁 Role '{role_name}' already exists, skipping.")
            return

        print(f"🎯 Creating role: {role_name}")
        role = sm.add_role(role_name)

        for view_name, perm_name in perms:
            pv = sm.find_permission_view_menu(perm_name, view_name)
            if pv:
                sm.add_permission_role(role, pv)
                print(f"✅ Added permission: {perm_name} on {view_name}")
            else:
                print(f"⚠️  Permission {perm_name} on {view_name} not found!")

    # Define your roles and permissions
    create_role("DataAnalyst", [
        ("DAGs", "can_read"),
        ("DAG Runs", "can_read"),
        ("Task Instances", "can_read"),
        ("Browse", "can_access_menu"),
    ])

    create_role("OpsUser", [
        ("DAGs", "can_read"),
        ("DAG Runs", "can_read"),
        ("Task Instances", "can_read"),
        ("Browse", "can_access_menu"),
        ("DAGs", "can_trigger"),
    ])

    create_role("Public", [
        ("Home", "can_access_menu"),
    ])
