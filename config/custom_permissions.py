from airflow.www.app import create_app

app = create_app()
with app.app_context():
    sm = app.appbuilder.sm

    role_name = "DataAnalyst"
    role = sm.find_role(role_name) or sm.add_role(role_name)

    permissions = [
        ("can_edit", "My Password"),
        ("can_read", "My Password"),
        ("can_edit", "My Profile"),
        ("can_read", "My Profile"),
        ("can_read", "View Menus"),
        ("can_create", "DAG Runs"),
        ("can_read", "DAG Runs"),
        ("can_edit", "DAG Runs"),
        ("menu_access", "Browse"),
        ("menu_access", "DAGs"),
        ("menu_access", "Datasets"),
        ("can_read", "DAGs"),
        ("can_read", "DAG Dependencies"),
        ("can_read", "DAG Code"),
        ("can_read", "Datasets"),
        ("can_read", "Website"),
        ("can_edit", "DAGs"),
        ("can_create", "Datasets"),
        ("menu_access", "Hello Dashboard"),
        ("menu_access", "Custom"),
        ("menu_access", "Approve/Reject"),
        ("menu_access", "DataActions"),
    ]

    for action, resource in permissions:
        action_obj = sm.get_action(action) or sm.add_action(action)
        resource_obj = sm.get_resource(resource) or sm.add_resource(resource)
        perm_view = sm.get_permission(action, resource) or sm.add_permission(action, resource)

        if perm_view not in role.permissions:
            sm.add_permission_to_role(role, perm_view)

    print(f"✅ Role '{role_name}' updated with custom permissions.")
