import logging
from flask import Flask
from app.config import Config


def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Register blueprints
    from app.routes.metrics import metrics_bp
    from app.routes.health import health_bp

    app.register_blueprint(metrics_bp, url_prefix="/api/v1")
    app.register_blueprint(health_bp, url_prefix="/api/v1")

    return app