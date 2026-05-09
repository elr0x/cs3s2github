"""Main blueprint - public routes (home, health check, etc)."""
import logging
from flask import Blueprint, render_template, jsonify, current_app
from app.services.api_client import APIClient

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    """Home page."""
    return render_template("index.html")


@main_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint for the web frontend."""
    try:
        # Try to check backend health, but don't fail if it's unavailable
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )
        result = api_client.get_health_status()
        
        if result["success"]:
            return jsonify({"status": "ok", "service": "monitoring-web"}), 200
        else:
            # Backend is down but frontend is running
            return jsonify({"status": "ok", "service": "monitoring-web", "backend": "unavailable"}), 200
    except Exception as e:
        # Frontend is running, backend check failed - still return 200
        logger.warning(f"Health check: backend unavailable - {str(e)}")
        return jsonify({"status": "ok", "service": "monitoring-web", "backend": "unavailable"}), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "error"}), 500


@main_bp.route("/about", methods=["GET"])
def about():
    """About page."""
    return render_template("about.html")


@main_bp.route("/api/status", methods=["GET"])
def api_status():
    """Check if backend API is available."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )
        result = api_client.get_health_status()
        return jsonify(result), 200 if result["success"] else 503
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
