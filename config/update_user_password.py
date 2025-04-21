from flask_appbuilder.security.sqla.models import User
from werkzeug.security import generate_password_hash
from airflow import settings

# Create a session to interact with the database
session = settings.Session()

# Find the user by username
user = session.query(User).filter_by(username='analyst').first()

# If user exists, update the password
if user:
    user.password = generate_password_hash('analyst')
    session.commit()  # Save the change
    print('Password updated successfully.')
else:
    print('User not found.')
