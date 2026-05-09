import logging
from flask import Blueprint, request, jsonify
from app.auth import require_api_key
from app.models import AzurePaaSHealth
from app import database

health_bp = Blueprint("health", __name__)
logger = logging.getLogger(__name__)


@health_bp.route("/health", methods=["POST"])
@require_api_key
def post_health():
    """Receive a PaaS health check result and store it in Azure SQL."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON body"}), 400

        health = AzurePaaSHealth.from_dict(data)

        database.insert_health(
            service_name=health.service_name,
            status=health.status,
            response_ms=health.response_ms,
            error_message=health.error_message
        )

        logger.info(f"HEALTH - Stored: {health.service_name} | {health.status}")
        return jsonify({"message": "Health record received", "data": health.to_dict()}), 201

    except KeyError as e:
        logger.error(f"HEALTH - Missing required field: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        logger.error(f"HEALTH - Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@health_bp.route("/health/status", methods=["GET"])
def api_status():
    """Public endpoint — confirms the API is running. No auth required."""
    return jsonify({"status": "ok", "service": "monitoring-api"}), 200