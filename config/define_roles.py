from airflow import settings
from airflow.www.security import AirflowSecurityManager
from airflow.www.app import create_app
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Check if the table is already defined
if 'ab_permission_view_role' not in Base.metadata.tables:
    assoc_permissionview_role = Table(
        'ab_permission_view_role',
        Base.metadata,
        Column('permission_view_id', Integer, ForeignKey('ab_permission_view.id'), primary_key=True),
        Column('role_id', Integer, ForeignKey('ab_role.id'), primary_key=True),
        extend_existing=True  # Prevents the InvalidRequestError
    )

# Initialize Airflow app
app = create_app()
app.app_context().push()

# Get the Airflow Security Manager instance
security_manager: AirflowSecurityManager = app.appbuilder.sm

def create_custom_role(name, permissions):
    role = security_manager.find_role(name)
    if not role:
        role = security_manager.add_role(name)

    print(f"log: {permissions}")

    for perm_name, view_menu in permissions:
        # Check if the permission already exists
        perm = security_manager.find_permission_view_menu(perm_name, view_menu)
        if not perm:
            # If the permission does not exist, create it
            security_manager.add_permission_view_menu(perm_name, view_menu)
            perm = security_manager.find_permission_view_menu(perm_name, view_menu)
        
        # Add the permission to the role if it's not already there
        if perm not in role.permissions:
            security_manager.add_permission_role(role, perm)

# Example: Custom role with limited access
custom_permissions = [
    ("can_read", "DAGs"),
    ("can_read", "TaskInstances"),
    ("can_read", "Browse"),
]

if __name__ == "__main__":
    create_custom_role("Viewer", custom_permissions)
    create_custom_role("Public", custom_permissions)  # Fixed extra space after 'OpsUser'

    print("✅ Role 'Viewer' created.")
    print("✅ Role 'Public' created.")
