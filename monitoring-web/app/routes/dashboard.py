"""Dashboard blueprint - monitoring dashboards and views."""
import logging
from flask import Blueprint, render_template, request, current_app
from app.services.api_client import APIClient
from app.services.data_processor import DataProcessor
from app.auth import entra_auth

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/", methods=["GET"])
@entra_auth.login_required
def overview():
    """Main dashboard with overview of all metrics and health status."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        # Get metrics
        metrics_result = api_client.get_metrics(limit=100)
        metrics = metrics_result.get("data", []) if metrics_result.get("success") else []

        # Process metrics for display
        formatted_metrics = [DataProcessor.format_metric_for_display(m) for m in metrics]
        metrics_by_host = DataProcessor.aggregate_metrics_by_host(metrics)
        status_summary = DataProcessor.get_status_summary(metrics)

        # Calculate host status
        host_status = {}
        for host, host_metrics in metrics_by_host.items():
            statuses = [m.get("status", "UNKNOWN") for m in host_metrics]
            if "CRITICAL" in statuses:
                host_status[host] = "CRITICAL"
            elif "WARNING" in statuses:
                host_status[host] = "WARNING"
            else:
                host_status[host] = "OK"

        context = {
            "metrics": formatted_metrics[:50],  # Show latest 50
            "metrics_by_host": metrics_by_host,
            "status_summary": status_summary,
            "host_status": host_status,
            "total_hosts": len(metrics_by_host),
            "total_metrics": len(metrics),
            "api_available": True
        }

        return render_template("dashboard/overview.html", **context)

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template(
            "dashboard/overview.html",
            metrics=[],
            metrics_by_host={},
            status_summary={},
            host_status={},
            total_hosts=0,
            total_metrics=0,
            api_available=False,
            error=str(e)
        )


@dashboard_bp.route("/metrics", methods=["GET"])
@entra_auth.login_required
def metrics_view():
    """Detailed metrics view with filtering."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        # Get filter parameters
        source_host = request.args.get("host")
        metric_name = request.args.get("metric")
        limit = int(request.args.get("limit", 100))

        # Retrieve metrics from API
        metrics_result = api_client.get_metrics(
            source_host=source_host,
            metric_name=metric_name,
            limit=limit
        )

        metrics = metrics_result.get("data", []) if metrics_result.get("success") else []
        formatted_metrics = [DataProcessor.format_metric_for_display(m) for m in metrics]

        # Get unique hosts and metric names for filter dropdowns
        unique_hosts = sorted(set(m.get("source_host") for m in metrics if m.get("source_host")))
        unique_metrics = sorted(set(m.get("metric_name") for m in metrics if m.get("metric_name")))

        context = {
            "metrics": formatted_metrics,
            "total_metrics": len(formatted_metrics),
            "unique_hosts": unique_hosts,
            "unique_metrics": unique_metrics,
            "selected_host": source_host,
            "selected_metric": metric_name,
            "api_available": True
        }

        return render_template("dashboard/metrics.html", **context)

    except Exception as e:
        logger.error(f"Metrics view error: {e}")
        return render_template(
            "dashboard/metrics.html",
            metrics=[],
            total_metrics=0,
            unique_hosts=[],
            unique_metrics=[],
            api_available=False,
            error=str(e)
        )


@dashboard_bp.route("/host/<host>", methods=["GET"])
@entra_auth.login_required
def host_details(host):
    """Detailed view for a specific host."""
    try:
        api_client = APIClient(
            current_app.config["API_BASE_URL"],
            current_app.config["API_KEY"],
            current_app.config["API_TIMEOUT"]
        )

        # Get metrics for this host
        metrics_result = api_client.get_metrics(source_host=host, limit=200)
        metrics = metrics_result.get("data", []) if metrics_result.get("success") else []

        # Group by metric type
        metrics_by_type = DataProcessor.aggregate_metrics_by_type(metrics)

        # Format for display
        formatted_metrics = [DataProcessor.format_metric_for_display(m) for m in metrics]
        stats_by_type = {}

        for metric_type, type_metrics in metrics_by_type.items():
            stats_by_type[metric_type] = {
                "average": DataProcessor.calculate_average_value(type_metrics),
                "min_max": DataProcessor.get_min_max_values(type_metrics),
                "count": len(type_metrics),
                "chart_data": DataProcessor.format_metrics_for_chart(type_metrics)
            }

        context = {
            "host": host,
            "metrics": formatted_metrics,
            "metrics_by_type": metrics_by_type,
            "stats_by_type": stats_by_type,
            "total_metrics": len(formatted_metrics),
            "api_available": True
        }

        return render_template("dashboard/host_details.html", **context)

    except Exception as e:
        logger.error(f"Host details error for {host}: {e}")
        return render_template(
            "dashboard/host_details.html",
            host=host,
            metrics=[],
            metrics_by_type={},
            stats_by_type={},
            api_available=False,
            error=str(e)
        )
