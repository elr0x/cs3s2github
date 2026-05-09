"""Tests for the main routes."""
import pytest
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def client():
    """Create test client."""
    app = create_app(TestingConfig)
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test home page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Knowledge Hub' in response.data


def test_about_page(client):
    """Test about page."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About' in response.data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code in [200, 503]


def test_dashboard_overview(client):
    """Test dashboard overview page."""
    response = client.get('/dashboard/')
    assert response.status_code == 200


def test_dashboard_metrics(client):
    """Test metrics view page."""
    response = client.get('/dashboard/metrics')
    assert response.status_code == 200


def test_404_error(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
