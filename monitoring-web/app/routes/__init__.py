"""API endpoints for AJAX calls from the frontend."""
import logging
from flask import Blueprint, jsonify, request, current_app
from app.services.api_client import APIClient
from app.services.data_processor import DataProcessor

logger = logging.getLogger(__name__)
api_bp = Blueprint("api", __name__)


@api_bp.route("/metrics", methods=["GET"])
def get_metrics_api():
    """Get metrics data for AJAX requests."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        source_host = request.args.get("host")
        metric_name = request.args.get("metric")
        limit = int(request.args.get("limit", 50))

        result = api_client.get_metrics(
            source_host=source_host,
            metric_name=metric_name,
            limit=limit
        )

        if result["success"]:
            metrics = result.get("data", [])
            formatted = [DataProcessor.format_metric_for_display(m) for m in metrics]
            return jsonify({"success": True, "data": formatted})
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"API metrics error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/metrics/summary", methods=["GET"])
def get_metrics_summary():
    """Get summary statistics of metrics."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        result = api_client.get_metrics(limit=200)

        if result["success"]:
            metrics = result.get("data", [])
            status_summary = DataProcessor.get_status_summary(metrics)
            metrics_by_host = DataProcessor.aggregate_metrics_by_host(metrics)

            return jsonify({
                "success": True,
                "data": {
                    "status_summary": status_summary,
                    "total_metrics": len(metrics),
                    "total_hosts": len(metrics_by_host)
                }
            })
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"API summary error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/status", methods=["GET"])
def get_status():
    """Get system status."""
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
            "backend": backend_status.get("data", {}).get("status", "unknown") if backend_status.get("success") else "unavailable"
        })

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({
            "success": False,
            "frontend": "ok",
            "backend": "error",
            "error": str(e)
        }), 500
