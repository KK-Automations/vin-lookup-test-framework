from flask import Flask
from config.logging_config import setup_logging

setup_logging()

def create_app():
    """
    Create and configure the Flask app.
    """
    app = Flask(__name__)

    # Import routes and register them
    from app.routes import app as routes_app
    app = routes_app

    return app