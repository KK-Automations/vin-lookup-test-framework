"""HTMX fragment routes."""

from flask import Blueprint, render_template, request

from app.routes.pages import _lookup_service

partials_bp = Blueprint("partials", __name__, url_prefix="/partials")


@partials_bp.post("/lookup")
def lookup():
    vin = request.form.get("vin", "")
    result = _lookup_service().lookup(vin)
    return render_template("partials/vin_result.html", result=result)
