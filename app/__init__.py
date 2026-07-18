"""Flask application factory."""

from flask import Flask

from config.logging_config import setup_logging
from config.settings import Settings


def create_app(settings: Settings | None = None) -> Flask:
    setup_logging()
    app = Flask(__name__)
    app.config["SETTINGS"] = settings or Settings.from_env()

    from app.domain.records import FIELD_LABELS
    from app.providers import provider_label
    app.jinja_env.globals["field_labels"] = FIELD_LABELS
    app.jinja_env.filters["provider_label"] = provider_label

    from app.routes.api import api_bp
    from app.routes.pages import pages_bp
    from app.routes.partials import partials_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(partials_bp)
    app.register_blueprint(api_bp)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    return app
