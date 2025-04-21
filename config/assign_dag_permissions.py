from airflow.www.app import create_app
from airflow import settings

app = create_app()
with app.app_context():
    sm = app.appbuilder.sm
    session = settings.Session()

    role_name = "DataAnalyst"
    dag_ids = ["approval_rejection_dag", "approval_workflow"]

    role = sm.find_role(role_name)

    for dag_id in dag_ids:
        perm = sm.get_permission("can_read", dag_id)
        if not perm:
            perm = sm.add_permission("can_read", dag_id)
        sm.add_permission_to_role(role, perm)

    session.commit()
    print(f"✅ DAG permissions assigned to role '{role_name}'")
