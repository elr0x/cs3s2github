import logging
from flask import Blueprint, request, jsonify
from app.auth import require_api_key
from app.models import MonitoringMetric
from app import database

metrics_bp = Blueprint("metrics", __name__)
logger = logging.getLogger(__name__)


@metrics_bp.route("/metrics", methods=["POST"])
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
            status=metric.status
        )

        logger.info(f"METRIC - Stored: {metric.source_host} | {metric.metric_name}={metric.metric_value}")
        return jsonify({"message": "Metric received", "data": metric.to_dict()}), 201

    except KeyError as e:
        logger.error(f"METRIC - Missing required field: {e}")
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        logger.error(f"METRIC - Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@metrics_bp.route("/metrics", methods=["GET"])
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
            limit=limit
        )

        return jsonify({"results": results}), 200

    except Exception as e:
        logger.error(f"METRIC - GET error: {e}")
        return jsonify({"error": "Internal server error"}), 500