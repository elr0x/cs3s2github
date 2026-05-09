import os
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)


def require_api_key(f):
    """Decorator that enforces API Key authentication on any route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            logger.warning(f"AUTH - Missing API key | IP: {request.remote_addr}")
            return jsonify({"error": "Missing API key"}), 401

        if api_key != os.getenv("API_KEY"):
            logger.warning(f"AUTH - Invalid API key attempt | IP: {request.remote_addr}")
            return jsonify({"error": "Invalid API key"}), 403

        return f(*args, **kwargs)
    return decorated