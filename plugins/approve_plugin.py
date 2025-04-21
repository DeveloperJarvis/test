# plugins/approve_plugin.py

from airflow.plugins_manager import AirflowPlugin
from custom_approve_reject import ApproveRejectView

class ApproveRejectPlugin(AirflowPlugin):
    name = "approve_reject_plugin"
    appbuilder_views = [
        {
            "name": "Approve/Reject",
            "category": "DataActions",
            "view": ApproveRejectView()
        }
    ]
