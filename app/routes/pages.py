"""Full page routes."""

from flask import Blueprint, current_app, render_template

from app.services.lookup import LookupService

pages_bp = Blueprint("pages", __name__)


def _lookup_service() -> LookupService:
    settings = current_app.config["SETTINGS"]
    service = current_app.config.get("LOOKUP_SERVICE")
    if service is None:
        service = LookupService(settings)
        current_app.config["LOOKUP_SERVICE"] = service
    return service


@pages_bp.get("/")
def index():
    return render_template("index.html")


@pages_bp.get("/vin/<vin>")
def vin_detail(vin: str):
    result = _lookup_service().lookup(vin)
    return render_template("index.html", prefill_vin=vin, result=result)
