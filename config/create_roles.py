from airflow.www.app import create_app

app = create_app()
app.app_context().push()

security_manager = app.appbuilder.sm

def create_role(role_name, perms):
    role = security_manager.find_role(role_name)
    if not role:
        print(f"🎯 Creating role: {role_name}")
        role = security_manager.add_role(role_name)
    else:
        print(f"🔁 Updating role: {role_name}")

    for perm_name, view_menu_name in perms:
        print(f"🔐 Granting: {perm_name} on {view_menu_name}")
        try:
            permission = security_manager.get_permission(perm_name, view_menu_name)
            print(f"permission: {permission}")
            if permission:
                role.permissions.append(permission)  # Directly add the permission to the role
                print(f"✅ Granted permission {perm_name} on {view_menu_name}")
            else:
                print(f"⚠️ Permission {perm_name} on {view_menu_name} not found.")
        except Exception as e:
            print(f"⚠️ Failed to grant permission {perm_name} on {view_menu_name}: {e}")

create_role("DataAnalyst", [
    ("can_edit", "My Password"),
    ("can_read", "My Password"),
    ("can_edit", "My Profile"),
    ("can_read", "My Profile"),
    ("can_read", "View Menus"),
    ("can_create", "DAG Runs"),
    ("can_read", "DAG Runs"),
    ("can_edit", "DAG Runs"),
    ("menu access", "Browse"),
    ("menu access", "DAGs"),
    ("menu access", "Datasets"),
    ("can_read", "DAGs"),
    ("can_read", "DAG Dependencies"),
    ("can_read", "DAG Code"),
    ("can_read", "Datasets"),
    ("can_read", "Website"),
    ("can_edit", "DAGs"),
    ("can_create", "Datasets"),
    ("menu access", "Hello Dashboard"),
    ("menu access", "Custom"),
    ("menu access", "Approve/Reject"),
    ("menu access", "DataActions"),
])
