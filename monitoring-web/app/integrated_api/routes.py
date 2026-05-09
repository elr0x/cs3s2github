"""Integrated monitoring API routes."""
import logging

from flask import Blueprint, jsonify, request

from app.integrated_api import database
from app.integrated_api.auth import require_api_key
from app.integrated_api.models import AzurePaaSHealth, MonitoringMetric

logger = logging.getLogger(__name__)
integrated_api_bp = Blueprint("integrated_api", __name__)


@integrated_api_bp.route("/metrics", methods=["POST"])
@require_api_key
def post_metric():
    """Receive a monitoring metric and store it in Azure SQL."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Empty or invalid JSON body"}), 400

        metric = MonitoringMetric.from_dict(data)
        database.insert_metric(
            source_host=metric.source_host,
            source_type=metric.source_type,
            metric_name=metric.metric_name,
            metric_value=metric.metric_value,
            unit=metric.unit,
            status=metric.status,
        )

        logger.info(f"METRIC - Stored: {metric.source_host} | {metric.metric_name}={metric.metric_value}")
        return jsonify({"message": "Metric received", "data": metric.to_dict()}), 201

    except KeyError as e:
        logger.error(f"METRIC - Missing required field: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        logger.error(f"METRIC - Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@integrated_api_bp.route("/metrics", methods=["GET"])
@require_api_key
def get_metrics():
    """Retrieve stored metrics with optional filters."""
    try:
        source_host = request.args.get("source_host")
        metric_name = request.args.get("metric_name")
        limit = int(request.args.get("limit", 100))

        results = database.get_metrics(
            source_host=source_host,
            metric_name=metric_name,
            limit=limit,
        )
        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"METRIC - GET error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@integrated_api_bp.route("/health", methods=["POST"])
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
            error_message=health.error_message,
        )

        logger.info(f"HEALTH - Stored: {health.service_name} | {health.status}")
        return jsonify({"message": "Health record received", "data": health.to_dict()}), 201

    except KeyError as e:
        logger.error(f"HEALTH - Missing required field: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        logger.error(f"HEALTH - Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@integrated_api_bp.route("/health/status", methods=["GET"])
def api_status():
    """Public endpoint confirming the integrated API is running."""
    return jsonify({"status": "ok", "service": "monitoring-integrated-api"}), 200
