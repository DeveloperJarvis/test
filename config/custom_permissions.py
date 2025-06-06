#config/custom_permissions.py

from airflow.www.app import create_app
from airflow import settings

app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    session = settings.Session()

    # Use correct models via sm
    ActionModel = sm.action_model
    ResourceModel = sm.resource_model
    PermissionModel = sm.permission_model

    role_name = "DataAnalyst"
    role = sm.find_role(role_name) or sm.add_role(role_name)

    # 🚫 Remove DAG-related permissions (if any)
    removed = 0
    for perm in list(role.permissions):
        try:
            resource_name = perm.resource.name.lower()
            action_name = perm.action.name.lower()

            if (
                "dag" in resource_name
                or "task" in resource_name
                or "log" in resource_name
                or "browse" in resource_name
                or "graph" in resource_name
                or resource_name.startswith("dag_id:")
                or resource_name in ["dags", "browse", "graph view", "task instances", "task logs"]
                or "dag" in action_name
                or "task" in action_name
                or "log" in action_name
            ):
                role.permissions.remove(perm)
                removed += 1
        except Exception as e:
            print(f"⚠️ Skipping perm during cleanup due to error: {e}")

    print(f"🔧 Removed {removed} DAG/Task/Log permissions from role '{role_name}'.")

    # ✅ Add custom permissions
    permissions = [
        ("can_edit", "My Password"),
        ("can_read", "My Password"),
        ("can_edit", "My Profile"),
        ("can_read", "My Profile"),
        ("can_read", "Permissions"),
        # ("can_read", "View Menus"),
        # ("menu_access", "Browse"),
        # ("menu_access", "Datasets"),
        # ("can_read", "Datasets"),
        # ("can_create", "Datasets"),
        ("can_read", "Website"),
        ("menu_access", "Hello Dashboard"),
        ("can_read", "HelloView"),
        ("menu_access", "Custom"),
        # ("menu_access", "Approve/Reject"),
        # ("menu_access", "DataActions"),
    ]

    for action_name, resource_name in permissions:
        # Get or create Action
        action = session.query(ActionModel).filter_by(name=action_name).first()
        if not action:
            action = ActionModel(name=action_name)
            session.add(action)
            session.commit()

        # Get or create Resource
        resource = session.query(ResourceModel).filter_by(name=resource_name).first()
        if not resource:
            resource = ResourceModel(name=resource_name)
            session.add(resource)
            session.commit()

        # Get or create Permission (action + resource)
        permission = (
            session.query(PermissionModel)
            .filter_by(action=action, resource=resource)
            .first()
        )
        if not permission:
            permission = PermissionModel(action=action, resource=resource)
            session.add(permission)
            session.commit()

        # Assign to role if not already there
        if permission not in role.permissions:
            role.permissions.append(permission)

    session.commit()
    
    print(f"✅ Role '{role_name}' updated with custom permissions.")
