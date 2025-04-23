

```bash
docker-compose up
```

[apache airflow docker hub](https://hub.docker.com/r/apache/airflow/tags)

alternate
```bash
docker-compose down --volumes --remove-orphans
docker-compose up --build
```

```bash
docker compose down --volumes --remove-orphans
docker compose up --build
```

```bash
sudo lsof -i :8080
```

```bash
docker ps  # to see running containers
docker stop <container_id_or_name>  # replace with the relevant container ID or name
```

remove all containers
```bash
docker rm -f $(docker ps -aq)
```

restart webserver
```bash
docker-compose restart airflow-webserver
```
Restart the webserver and scheduler if using Docker:
```bash
docker-compose restart airflow-webserver airflow-scheduler
```



list images
```bash
docker images
```
delete an image
```bash
docker rmi <image_id_or_name>
```

list all images
```bash
docker images -a
```

remove all docker images
```bash
docker rmi $(docker images -q)
```

save docker compose up logs to dockerlogs file in project directory
```bash
docker-compose up > dockerlogs.txt 2>&1
```

save docker compose up logs to dockerlogs file in project directory (running in detached mode)
```bash
docker-compose up -d
docker-compose logs -f > dockerlogs.txt 2>&1
```
restarting airflow-webserver
```bash
docker compose restart airflow-webserver
```
troubleshooting airflow-webserver
```bash
docker compose logs airflow-webserver
docker compose logs -f airflow-webserver
```
check plugin load errors:
```bash
docker compose logs airflow-webserver | grep plugin
docker compose logs airflow-webserver | grep -i 'plugin\|error'
```
manually check test via curl
```bash
curl -i http://localhost:8080/custom/
curl -i http://localhost:8080/custom/debug_routes

```
test from within the container
```bash
docker compose exec airflow-webserver curl -i http://localhost:8080/custom/
```
also try:
```bash
docker compose exec airflow-webserver airflow plugins list
```

verify volume is mounted and files are available inside docker container:
```bash
docker compose exec airflow-webserver ls /opt/airflow/plugins
```
rebuild and restart everything:
```bash
docker compose down -v
docker compose build
docker compose up
```

test 1:
```bash
docker compose exec airflow-webserver python
```
```bash
from airflow.plugins_manager import plugins
plugins
```
```bash
docker compose exec airflow-webserver flask routes | grep /custom

```

debug inside container:
```bash
docker compose exec airflow-webserver bash
ls /opt/airflow/plugins/templates
cat /opt/airflow/plugins/custom_home.py
```

Test 2:
```bash
docker compose exec airflow-webserver bash
python
```
```bash
from flask_appbuilder import AppBuilder
from airflow.www.app import create_app

app = create_app()
print("🔍 Registered views:")
for rule in app.url_map.iter_rules():
    if 'custom' in rule.rule:
        print(rule.rule)

```
```bash
press <Enter>
```

### Airflow uses this URL pattern for AppBuilder views:
/<lowercase-view-class-name>/<exposed-method-name>


```bash
mkdir -p plugins/custom_home/templates
mv plugins/templates/home_analyst.html plugins/custom_home/templates/
```
container image architecture:
```bash
docker inspect apache/airflow:2.10.5 | grep -i architecture
```

inspect custom sql:
```bash
docker compose exec airflow-webserver bash
psql -h postgres -U airflow -d airflow
```
```bash
SELECT * FROM dag_run LIMIT 5;
```

airflow user list:
```bash
docker compose exec airflow-webserver airflow users list
```

curl user login:
```bash
curl -i -c cookies.txt -X POST \
  -F "username=airflow" \
  -F "password=airflow" \
  http://localhost:8080/login/
```
then reuse cookie from cookies.txt:
```bash
curl -b cookies.txt http://localhost:8080/home
```

## Run after server http://localhost:8080 is up
```bash
# list all permissions for all roles
docker compose exec airflow-webserver python config/list_permissions.py
# create custom role
docker compose exec airflow-webserver python config/create_roles.py
# apply necessary custom permissions
docker compose exec --user airflow airflow-webserver python /opt/airflow/config/custom_permissions.py
# create users with previously available role and new custom role
docker compose exec airflow-webserver python config/create_user.py
# assign role to user
docker compose exec airflow-webserver python config/assign_role_to_user.py
# Updating password...
docker compose exec airflow-webserver python /sources/config/update_user_password.py
# assign dag permission
# docker compose exec --user airflow airflow-webserver python /opt/airflow/config/assign_dag_permissions.py

```

#### dont CTRL+C it
```bash
docker compose up airflow-webserver
```

```bash
docker compose exec --user root airflow-webserver pip show flask_appbuilder
```

create .profile file inside docker
```bash
docker compose exec --user airflow airflow-webserver sh -c 'echo "export PATH=\"$PATH:/home/airflow/.local/bin\"" > /home/airflow/.profile'
```

check if .profile file is setup
```bash
docker compose exec --user airflow airflow-webserver cat /home/airflow/.profile
```

pip version inside docker
```bash
docker compose exec --user airflow airflow-webserver /home/airflow/.local/bin/pip --version
```

show flask_appbuilder details
```bash
docker compose exec --user airflow airflow-webserver /home/airflow/.local/bin/pip show flask_appbuilder
```

# List all routes inside flask app

1. ✅ Method 1: Python snippet in the container
```bash
docker compose exec airflow-webserver python
```
```python
from airflow.www.app import create_app
app = create_app()

for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint:40s} -> {rule.rule}")

```
```bash
Airflow.index                           -> /
AuthDBView.login                        -> /login/
AuthDBView.logout                       -> /logout/
...
```
2. ✅ Method 2: Use Flask CLI (if needed)

```bash
docker compose exec airflow-webserver bash
echo '
from airflow.www.app import create_app
app = create_app()

for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint:40s} -> {rule.rule}")
' > /tmp/routes.py && python /tmp/routes.py

```

create .env file
```bash
AIRFLOW_UID=5000
```