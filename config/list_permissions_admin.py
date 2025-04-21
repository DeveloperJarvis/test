from airflow.www.app import create_app

app = create_app()
app.app_context().push()

security_manager = app.appbuilder.sm

# Accessing the list of roles and their permissions
roles = security_manager.get_all_roles()
for role in roles:
    print(f"Role: {role.name}")
    # print(f"role permissions: {role.permissions}")
    if "Admin" == role.name:
        print(f"Permission: ", end="\0")
        if role.permissions:
            for perm in role.permissions:
                print(f"{perm}, ")
        else:
            print("{ }")
        break
