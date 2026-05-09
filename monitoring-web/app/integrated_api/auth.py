"""API key authentication for integrated monitoring API routes."""
import logging
import os
from functools import wraps

from flask import jsonify, request

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Require the configured API key for write/read API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        expected_api_key = os.getenv("API_KEY")

        if not expected_api_key:
            logger.error("AUTH - API_KEY environment variable is not configured")
            return jsonify({"error": "API authentication is not configured"}), 500

        if not api_key:
            logger.warning(f"AUTH - Missing API key | IP: {request.remote_addr}")
            return jsonify({"error": "Missing API key"}), 401

        if api_key != expected_api_key:
            logger.warning(f"AUTH - Invalid API key attempt | IP: {request.remote_addr}")
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated
