"""Tests for API services."""
import pytest
from app.services.api_client import APIClient
from app.services.data_processor import DataProcessor


class TestDataProcessor:
    """Test data processing utilities."""

    def test_aggregate_metrics_by_host(self):
        """Test metrics aggregation by host."""
        metrics = [
            {"source_host": "host1", "metric_name": "cpu_percent", "metric_value": 50},
            {"source_host": "host1", "metric_name": "memory_percent", "metric_value": 60},
            {"source_host": "host2", "metric_name": "cpu_percent", "metric_value": 30},
        ]
        result = DataProcessor.aggregate_metrics_by_host(metrics)
        assert len(result) == 2
        assert len(result["host1"]) == 2
        assert len(result["host2"]) == 1

    def test_calculate_average_value(self):
        """Test average value calculation."""
        metrics = [
            {"metric_value": 10},
            {"metric_value": 20},
            {"metric_value": 30},
        ]
        avg = DataProcessor.calculate_average_value(metrics)
        assert avg == 20.0

    def test_get_status_summary(self):
        """Test status summary calculation."""
        metrics = [
            {"status": "OK"},
            {"status": "OK"},
            {"status": "WARNING"},
            {"status": "CRITICAL"},
        ]
        summary = DataProcessor.get_status_summary(metrics)
        assert summary["OK"] == 2
        assert summary["WARNING"] == 1
        assert summary["CRITICAL"] == 1
        assert summary["UNKNOWN"] == 0

    def test_format_metric_for_display(self):
        """Test metric formatting."""
        metric = {
            "id": 1,
            "source_host": "testhost",
            "source_type": "onprem",
            "metric_name": "cpu_percent",
            "metric_value": 75.5,
            "unit": "%",
            "status": "WARNING",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        formatted = DataProcessor.format_metric_for_display(metric)
        assert formatted["host"] == "testhost"
        assert formatted["value"] == 75.5
        assert formatted["status"] == "WARNING"
        assert formatted["status_class"] == "warning"
