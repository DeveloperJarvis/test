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

    # 🚫 Remove DAG and Task-related permissions
    removed = 0
    for perm in list(role.permissions):
        if (
            "dag" in perm.resource.name.lower()
            or "task" in perm.resource.name.lower()
            or "log" in perm.resource.name.lower()
        ):
            role.permissions.remove(perm)
            removed += 1
    if removed:
        print(f"🧹 Removed {removed} DAG/Task/Log permissions from role '{role_name}'.")

    # ✅ Add specified custom permissions
    for perm_name, view_menu_name in perms:
        perm_name = perm_name.replace(" ", "_")  # Normalize e.g., "menu access" → "menu_access"
        print(f"🔐 Granting: {perm_name} on {view_menu_name}")
        try:
            permission = security_manager.get_permission(perm_name, view_menu_name)
            if permission:
                if permission not in role.permissions:
                    role.permissions.append(permission)
                    print(f"✅ Granted permission {perm_name} on {view_menu_name}")
                else:
                    print(f"↪️ Already has permission {perm_name} on {view_menu_name}")
            else:
                print(f"⚠️ Permission {perm_name} on {view_menu_name} not found.")
        except Exception as e:
            print(f"⚠️ Failed to grant permission {perm_name} on {view_menu_name}: {e}")

    print(f"✅ Role '{role_name}' setup complete.\n")


create_role("DataAnalyst", [
    ("can_edit", "My Password"),
    ("can_read", "My Password"),
    ("can_edit", "My Profile"),
    ("can_read", "My Profile"),
    ("can_read", "Permissions"),
    ("can_read", "View Menus"),
    ("menu_access", "Browse"),
    ("menu_access", "Datasets"),
    ("can_read", "Datasets"),
    ("can_create", "Datasets"),
    ("can_read", "Website"),
    ("menu_access", "Hello Dashboard"),
    ("menu_access", "Custom"),
    ("menu_access", "Approve/Reject"),
    ("menu_access", "DataActions"),
])
