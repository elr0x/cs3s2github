import unittest
import json
from unittest.mock import patch
from app import create_app
from app.config import Config


class TestMetricsEndpoints(unittest.TestCase):

    def setUp(self):
        self.app = create_app(Config)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.headers = {"X-API-Key": "test-key", "Content-Type": "application/json"}

    @patch("os.getenv", side_effect=lambda k, *a: "test-key" if k == "API_KEY" else None)
    @patch("app.database.insert_metric")
    def test_post_metric_success(self, mock_insert, mock_env):
        """POST /api/v1/metrics with valid data returns 201."""
        payload = {
            "source_host": "DC01",
            "source_type": "onprem",
            "metric_name": "cpu_percent",
            "metric_value": 47.3,
            "unit": "%",
            "status": "OK"
        }
        response = self.client.post(
            "/api/v1/metrics",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["data"]["source_host"], "DC01")

    @patch("os.getenv", side_effect=lambda k, *a: "test-key" if k == "API_KEY" else None)
    def test_post_metric_missing_field(self, mock_env):
        """POST /api/v1/metrics with missing field returns 400."""
        payload = {"source_host": "DC01"}
        response = self.client.post(
            "/api/v1/metrics",
            data=json.dumps(payload),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)

    def test_post_metric_no_api_key(self):
        """POST /api/v1/metrics without API key returns 401."""
        response = self.client.post(
            "/api/v1/metrics",
            data=json.dumps({}),
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 401)

    @patch("os.getenv", side_effect=lambda k, *a: "test-key" if k == "API_KEY" else None)
    @patch("app.database.get_metrics", return_value=[])
    def test_get_metrics_success(self, mock_get, mock_env):
        """GET /api/v1/metrics returns 200 with results list."""
        response = self.client.get("/api/v1/metrics", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.get_json())


if __name__ == "__main__":
    unittest.main()