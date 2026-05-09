import unittest
import json
from unittest.mock import patch
from app import create_app
from app.config import Config


class TestHealthEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app(Config)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.headers = {"X-API-Key": "test-key", "Content-Type": "application/json"}

    def test_api_status_public(self):
        """GET /api/v1/health/status is public and returns 200."""
        response = self.client.get("/api/v1/health/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "monitoring-api")

    @patch("os.getenv", side_effect=lambda k, *a: "test-key" if k == "API_KEY" else None)
    @patch("app.database.insert_health")
    def test_post_health_success(self, mock_insert, mock_env):
        """POST /api/v1/health with valid data returns 201."""
        payload = {
            "service_name": "AzureSQL-DB",
            "status": "Healthy",
            "response_ms": 42,
            "error_message": None
        }
        response = self.client.post(
            "/api/v1/health",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["service_name"], "AzureSQL-DB")

    @patch("os.getenv", side_effect=lambda k, *a: "test-key" if k == "API_KEY" else None)
    def test_post_health_missing_field(self, mock_env):
        """POST /api/v1/health with missing field returns 400."""
        payload = {"service_name": "AzureSQL-DB"}
        response = self.client.post(
            "/api/v1/health",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

    def test_post_health_no_api_key(self):
        """POST /api/v1/health without API key returns 401."""
        response = self.client.post(
            "/api/v1/health",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()