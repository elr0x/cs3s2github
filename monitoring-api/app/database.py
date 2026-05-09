import logging
import pyodbc
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_connection() -> pyodbc.Connection:
    """Open and return a connection to Azure SQL Database."""
    conn_str = os.getenv("DB_CONNECTION_STRING")
    if not conn_str:
        raise ValueError("DB_CONNECTION_STRING environment variable is not set")
    return pyodbc.connect(conn_str)


def insert_metric(source_host: str, source_type: str, metric_name: str,
                  metric_value: float, unit: Optional[str], status: Optional[str]) -> None:
    """Insert a monitoring metric into the MonitoringMetrics table."""
    sql = """
        INSERT INTO MonitoringMetrics 
            (source_host, source_type, metric_name, metric_value, unit, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            conn.execute(sql, (source_host, source_type, metric_name,
                               metric_value, unit, status))
            conn.commit()
            logger.info(f"DB - Metric inserted: {source_host} | {metric_name}={metric_value}")
    except pyodbc.Error as e:
        logger.error(f"DB - Failed to insert metric: {e}")
        raise


def get_metrics(source_host: Optional[str] = None,
                metric_name: Optional[str] = None,
                limit: int = 100) -> list:
    """Retrieve metrics from MonitoringMetrics with optional filters."""
    sql = "SELECT id, timestamp, source_host, source_type, metric_name, metric_value, unit, status FROM MonitoringMetrics WHERE 1=1"
    params = []

    if source_host:
        sql += " AND source_host = ?"
        params.append(source_host)
    if metric_name:
        sql += " AND metric_name = ?"
        params.append(metric_name)

    sql += " ORDER BY timestamp DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY"
    params.append(limit)

    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    except pyodbc.Error as e:
        logger.error(f"DB - Failed to retrieve metrics: {e}")
        raise


def insert_health(service_name: str, status: str,
                  response_ms: Optional[int], error_message: Optional[str]) -> None:
    """Insert a PaaS health check result into the AzurePaaSHealth table."""
    sql = """
        INSERT INTO AzurePaaSHealth 
            (service_name, status, response_ms, error_message)
        VALUES (?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            conn.execute(sql, (service_name, status, response_ms, error_message))
            conn.commit()
            logger.info(f"DB - Health inserted: {service_name} | {status}")
    except pyodbc.Error as e:
        logger.error(f"DB - Failed to insert health record: {e}")
        raise