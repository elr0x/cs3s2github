"""Service initialization and management."""
from app.services.api_client import APIClient
from app.services.data_processor import DataProcessor


def create_api_client(base_url: str, api_key: str, timeout: int = 10) -> APIClient:
    """Factory function to create API client instance."""
    return APIClient(base_url, api_key, timeout)


__all__ = ["APIClient", "DataProcessor", "create_api_client"]
