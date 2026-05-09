from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MonitoringMetric:
    """Represents a single monitoring metric from on-prem or Azure."""
    source_host: str        # e.g. DC01, FS1, Monitoring
    source_type: str        # 'onprem' or 'azurepaas'
    metric_name: str        # e.g. cpu_percent, disk_free_gb
    metric_value: float
    unit: Optional[str] = None      # e.g. %, GB, ms
    status: Optional[str] = None    # OK, WARNING, CRITICAL
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "source_host": self.source_host,
            "source_type": self.source_type,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "unit": self.unit,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @staticmethod
    def from_dict(data: dict) -> "MonitoringMetric":
        return MonitoringMetric(
            source_host=data["source_host"],
            source_type=data["source_type"],
            metric_name=data["metric_name"],
            metric_value=float(data["metric_value"]),
            unit=data.get("unit"),
            status=data.get("status")
        )


@dataclass
class AzurePaaSHealth:
    """Represents a health check result for an Azure PaaS service."""
    service_name: str       # e.g. AppService-API, AzureSQL-DB
    status: str             # Healthy, Degraded, Down
    response_ms: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "service_name": self.service_name,
            "status": self.status,
            "response_ms": self.response_ms,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @staticmethod
    def from_dict(data: dict) -> "AzurePaaSHealth":
        return AzurePaaSHealth(
            service_name=data["service_name"],
            status=data["status"],
            response_ms=data.get("response_ms"),
            error_message=data.get("error_message")
        )