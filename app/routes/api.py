"""Public JSON API."""

from flask import Blueprint, jsonify, request

from app.routes.pages import _explorer_service, _lookup_service
from app.services.lookup import LookupResult

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _serialize(result: LookupResult) -> dict:
    payload: dict = {
        "vin": result.parsed.normalized,
        "valid": result.parsed.ok,
        "check_digit_ok": result.parsed.check_digit_ok,
        "issues": [
            {"code": i.code, "message": i.message, "severity": i.severity}
            for i in result.parsed.issues
        ],
        "suggestions": [
            {"vin": s.vin, "description": s.description, "confidence": s.confidence}
            for s in result.suggestions
        ],
        "structure": result.structural or None,
        "from_cache": result.from_cache,
    }

    if result.consensus:
        payload["confidence"] = {
            "score": round(result.consensus.confidence, 3),
            "bucket": result.consensus.confidence_bucket,
            "providers_ok": result.consensus.providers_ok,
            "providers_total": result.consensus.providers_total,
        }
        payload["fields"] = {
            name: {
                "status": fc.status,
                "value": fc.value,
                "independent_sources": fc.independent_sources,
                "votes": [
                    {"provider": v.provider, "value": v.value}
                    for v in fc.votes
                ],
            }
            for name, fc in result.consensus.fields.items()
        }
        payload["providers"] = [
            {
                "name": pr.provider,
                "display_name": pr.display_name,
                "ok": pr.ok,
                "error": pr.error,
                "latency_ms": pr.latency_ms,
                "from_cache": pr.from_cache,
            }
            for pr in result.provider_results
        ]
    return payload


@api_bp.get("/vin/<vin>")
def decode_vin(vin: str):
    force_refresh = request.args.get("refresh") == "1"
    result = _lookup_service().lookup(vin, force_refresh=force_refresh)
    status = 200 if result.parsed.ok else 422
    return jsonify(_serialize(result)), status


@api_bp.get("/makes")
def makes():
    return jsonify({"makes": _explorer_service().makes()})


@api_bp.get("/models")
def models():
    make = request.args.get("make", "").strip()
    try:
        year = int(request.args.get("year", ""))
    except ValueError:
        return jsonify({"error": "year must be an integer"}), 400
    if not make:
        return jsonify({"error": "make is required"}), 400
    return jsonify({
        "make": make,
        "year": year,
        "models": _explorer_service().models(make, year),
    })
