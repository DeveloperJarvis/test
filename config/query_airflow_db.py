from airflow import settings
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import sessionmaker

# Create a session to interact with the database
Session = sessionmaker(bind=settings.engine)
session = Session()

try:
    # Query the 'ab_user' table (Airflow's User table)
    users = session.query(User).all()
    # print(users)

    # Print the usernames and email addresses of all users in the database
    for user in users:
        print(user)
        print(f"Username: {user.username}, Email: {user.email}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    session.close()
