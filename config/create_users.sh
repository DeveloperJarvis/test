#!/bin/bash

# Create default admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Create a viewer user
airflow users create \
    --username viewer \
    --firstname View \
    --lastname Only \
    --role Viewer \
    --email viewer@example.com \
    --password viewer

airflow users create \
  --username analyst \
  --firstname Data \
  --lastname Analyst \
  --role Public \
  --email analyst@example.com \
  --password analystpass

airflow users create \
  --username ops \
  --firstname Ops \
  --lastname User \
  --role OpsUser \
  --email ops@example.com \
  --password opspass


# Add more users as needed...
