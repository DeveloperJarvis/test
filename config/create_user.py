from airflow import settings
from airflow.www.app import create_app
from airflow.www.security import AirflowSecurityManager

app = create_app()
app.app_context().push()

security_manager: AirflowSecurityManager = app.appbuilder.sm

def create_user(username, firstname, lastname, email, role, password):
    # Find if the user already exists
    user = security_manager.find_user(username=username)
    if user:
        print(f"User '{username}' already exists.")
        return user

    # Ensure the role exists
    role_obj = security_manager.find_role(role)
    if not role_obj:
        print(f"❌ Role '{role}' does not exist.")
        return None

    print(f"Creating user '{username}' with role '{role}'...")
    # Add the user
    user = security_manager.add_user(
        username=username,
        first_name=firstname,
        last_name=lastname,
        email=email,
        role=role_obj,
        password=password,
    )
    print(f"✅ User '{username}' created.")
    return user

# 👇 Add users here
# create_user("analyst", "Data", "Analyst", "analyst@example.com", "DataAnalyst", "analystpass")
# create_user("ops", "Ops", "Engineer", "ops@example.com", "OpsUser", "opspass")
create_user("op", "op", "OpRole", "op@example.com", "Op", "op")
create_user("public", "public", "PublicRole", "public@example.com", "Public", "public")
