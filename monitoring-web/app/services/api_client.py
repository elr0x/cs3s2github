"""API client service for communicating with the monitoring backend."""
import logging
import requests
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with the monitoring backend API."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 10):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the backend API (e.g., http://localhost:5000/api/v1)
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def get_metrics(
        self,
        source_host: Optional[str] = None,
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Retrieve metrics from the backend API.

        Args:
            source_host: Filter by source host
            metric_name: Filter by metric name
            limit: Maximum number of results

        Returns:
            Dictionary with metrics data or error information
        """
        try:
            params = {"limit": limit}
            if source_host:
                params["source_host"] = source_host
            if metric_name:
                params["metric_name"] = metric_name

            response = requests.get(
                f"{self.base_url}/metrics",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                logger.info(f"Successfully retrieved metrics (limit={limit})")
                payload = response.json()
                metrics = payload.get("results", payload) if isinstance(payload, dict) else payload
                return {"success": True, "data": metrics}
            else:
                logger.warning(f"API returned status {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Timeout:
            logger.error(f"API request timed out after {self.timeout}s")
            return {"success": False, "error": "Request timeout"}
        except RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}

    def post_metric(self, metric_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post a new metric to the backend API.

        Args:
            metric_data: Metric data to send

        Returns:
            Dictionary with response or error information
        """
        try:
            response = requests.post(
                f"{self.base_url}/metrics",
                headers=self.headers,
                json=metric_data,
                timeout=self.timeout
            )

            if response.status_code == 201:
                logger.info(f"Successfully posted metric: {metric_data.get('metric_name')}")
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"API returned status {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status from the backend API.

        Returns:
            Dictionary with health status or error information
        """
        try:
            response = requests.get(
                f"{self.base_url}/health/status",
                timeout=self.timeout
            )

            if response.status_code == 200:
                logger.info("Backend API is healthy")
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"Backend health check returned status {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"success": False, "error": str(e)}

    def post_health(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post a health check result to the backend API.

        Args:
            health_data: Health check data to send

        Returns:
            Dictionary with response or error information
        """
        try:
            response = requests.post(
                f"{self.base_url}/health",
                headers=self.headers,
                json=health_data,
                timeout=self.timeout
            )

            if response.status_code == 201:
                logger.info(f"Successfully posted health: {health_data.get('service_name')}")
                return {"success": True, "data": response.json()}
            else:
                logger.warning(f"API returned status {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"success": False, "error": str(e)}
