"""HTMX fragment routes."""

from flask import Blueprint, render_template, request

from app.routes.pages import _lookup_service

partials_bp = Blueprint("partials", __name__, url_prefix="/partials")


@partials_bp.post("/lookup")
def lookup():
    vin = request.form.get("vin", "")
    force_refresh = request.args.get("refresh") == "1"
    result = _lookup_service().lookup(vin, force_refresh=force_refresh)
    return render_template("partials/vin_result.html", result=result)


@partials_bp.get("/recent")
def recent():
    entries = _lookup_service().repository.recent_lookups(limit=10)
    return render_template("partials/recent_list.html", entries=entries)
