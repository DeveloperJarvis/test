# plugins/custom_approve_reject.py

from flask import request, redirect, flash
from flask_appbuilder import BaseView as AppBuilderBaseView, expose
from airflow.www.app import csrf
from airflow.models import Variable
import logging

class ApproveRejectView(AppBuilderBaseView):
    default_view = "approve"

    @expose("/approve")
    @csrf.exempt
    def approve(self):
        data_id = request.args.get("id")
        logging.info(f"Approved ID: {data_id}")
        flash(f"Data with ID {data_id} approved!", "success")
        return redirect("/home")

    @expose("/reject")
    @csrf.exempt
    def reject(self):
        data_id = request.args.get("id")
        logging.info(f"Rejected ID: {data_id}")
        flash(f"Data with ID {data_id} rejected!", "warning")
        return redirect("/home")
