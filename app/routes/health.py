"""
app/routes/health.py
Server health check endpoint

GET /api/health   Returns server status (used to verify the server is running)
"""

from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "service": "IT Ticket System",
    }), 200