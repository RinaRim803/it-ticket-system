"""
app/__init__.py
Flask application factory
"""

from flask import Flask
from app.services.database import initialize_db


def create_app():
    app = Flask(__name__)

    # Initialize SQLite database on startup
    initialize_db()
    
    # Register route blueprints
    from app.routes.tickets import tickets_bp
    from app.routes.health import health_bp

    return app