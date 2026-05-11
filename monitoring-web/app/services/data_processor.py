"""Data processing and aggregation service for monitoring data."""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataProcessor:
    """Service for processing and aggregating monitoring data."""

    @staticmethod
    def aggregate_metrics_by_host(metrics: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Group metrics by source host.

        Args:
            metrics: List of metric dictionaries

        Returns:
            Dictionary with host as key and list of metrics as value
        """
        aggregated = defaultdict(list)
        for metric in metrics:
            host = metric.get("source_host", "unknown")
            aggregated[host].append(metric)
        return dict(aggregated)

    @staticmethod
    def aggregate_metrics_by_type(metrics: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Group metrics by metric name.

        Args:
            metrics: List of metric dictionaries

        Returns:
            Dictionary with metric type as key and list of metrics as value
        """
        aggregated = defaultdict(list)
        for metric in metrics:
            metric_type = metric.get("metric_name", "unknown")
            aggregated[metric_type].append(metric)
        return dict(aggregated)

    @staticmethod
    def calculate_average_value(metrics: List[Dict[str, Any]]) -> Optional[float]:
        """
        Calculate average value from a list of metrics.

        Args:
            metrics: List of metric dictionaries with 'metric_value' field

        Returns:
            Average value or None if list is empty
        """
        if not metrics:
            return None
        values = [m.get("metric_value", 0) for m in metrics]
        return sum(values) / len(values) if values else None

    @staticmethod
    def get_min_max_values(metrics: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
        """
        Get min and max values from metrics.

        Args:
            metrics: List of metric dictionaries

        Returns:
            Dictionary with 'min' and 'max' keys
        """
        values = [m.get("metric_value", 0) for m in metrics]
        if not values:
            return {"min": None, "max": None}
        return {"min": min(values), "max": max(values)}

    @staticmethod
    def get_status_summary(metrics: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get summary of metric statuses.

        Args:
            metrics: List of metric dictionaries with 'status' field

        Returns:
            Dictionary with status counts
        """
        summary = {"OK": 0, "WARNING": 0, "CRITICAL": 0, "UNKNOWN": 0}
        for metric in metrics:
            raw_status = metric.get("status") or "UNKNOWN"
            status = raw_status.upper()
            if status in summary:
                summary[status] += 1
            else:
                summary["UNKNOWN"] += 1
        return summary

    @staticmethod
    def format_metric_for_display(metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a metric for display in the UI.

        Args:
            metric: Raw metric dictionary from API

        Returns:
            Formatted metric dictionary
        """
        return {
            "id": metric.get("id"),
            "host": metric.get("source_host", "N/A"),
            "type": metric.get("source_type", "N/A"),
            "name": metric.get("metric_name", "N/A"),
            "value": metric.get("metric_value", "N/A"),
            "unit": metric.get("unit", ""),
            "status": metric.get("status", "UNKNOWN"),
            "timestamp": format_timestamp(metric.get("timestamp")),
            "status_class": get_status_css_class(metric.get("status"))
        }

    @staticmethod
    def format_metrics_for_chart(metrics: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Format metrics for chart.js visualization.

        Args:
            metrics: List of metric dictionaries

        Returns:
            Dictionary with labels and data for charts
        """
        if not metrics:
            return {"labels": [], "data": []}

        sorted_metrics = sorted(
            metrics,
            key=lambda m: m.get("timestamp", ""),
            reverse=True
        )[:20]  # Last 20 data points

        return {
            "labels": [format_timestamp(m.get("timestamp")) for m in reversed(sorted_metrics)],
            "data": [m.get("metric_value", 0) for m in reversed(sorted_metrics)]
        }


def format_timestamp(timestamp: Optional[str], format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format ISO timestamp to readable string."""
    if not timestamp:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime(format_string)
    except (ValueError, AttributeError):
        return timestamp


def get_status_css_class(status: Optional[str]) -> str:
    """Get CSS class for status badge."""
    status_map = {
        "OK": "success",
        "WARNING": "warning",
        "CRITICAL": "danger",
        "DEGRADED": "warning",
        "DOWN": "danger",
        "HEALTHY": "success"
    }
    return status_map.get((status or "UNKNOWN").upper(), "secondary")
