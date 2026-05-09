"""API routes - AJAX endpoints for frontend."""
import logging
from flask import Blueprint, jsonify, request, current_app
from app.services.api_client import APIClient
from app.auth import entra_auth

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


@api_bp.route("/status", methods=["GET"])
def get_status():
    """Get public frontend/backend status for the home page."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        backend_status = api_client.get_health_status()
        return jsonify({
            "success": True,
            "frontend": "ok",
            "backend": backend_status.get("data", {}).get("status", "unknown")
            if backend_status.get("success") else "unavailable"
        })

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            "success": False,
            "frontend": "ok",
            "backend": "error",
            "error": str(e)
        }), 500


@api_bp.route("/metrics", methods=["GET"])
@entra_auth.login_required
def get_metrics():
    """Get metrics data (AJAX endpoint)."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )
        
        limit = request.args.get("limit", 100, type=int)
        host = request.args.get("host")
        
        result = api_client.get_metrics(source_host=host, limit=limit)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API metrics error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/health", methods=["GET"])
@entra_auth.login_required
def get_health():
    """Get health status (AJAX endpoint)."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )
        
        result = api_client.get_health_status()
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API health error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
