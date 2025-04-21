from airflow import settings
from flask_appbuilder.security.sqla.models import User, Role
from sqlalchemy.orm import sessionmaker

# Create a session to interact with the database
Session = sessionmaker(bind=settings.engine)
session = Session()

# Find the user by username
username = 'analyst'  # Replace with the username you want to assign roles to
user = session.query(User).filter_by(username=username).first()

# Find the role by role name
role_name = 'DataAnalyst'  # Replace with the desired role name
role = session.query(Role).filter_by(name=role_name).first()

if user and role:
    user.roles.append(role)  # Assign the role to the user
    session.commit()  # Save the change
    print(f"Role '{role_name}' has been assigned to user '{username}'.")
else:
    print(f"User '{username}' or role '{role_name}' not found.")

# Close the session
session.close()
