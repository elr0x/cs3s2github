"""Flask application factory for the Monitoring Web Frontend."""
import logging
from flask import Flask
from app.config import get_config


def create_app(config=None):
    """Create and configure the Flask application."""
    if config is None:
        config = get_config()

    app = Flask(__name__)
    app.config.from_object(config)

    # Configure logging
    _configure_logging(app)

    # Register blueprints
    _register_blueprints(app)

    # Register error handlers
    _register_error_handlers(app)

    # Initialize context processors
    _init_context_processors(app)

    return app


def _configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        ))
        app.logger.addHandler(handler)
        app.logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))


def _register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp
    from app.integrated_api.routes import integrated_api_bp
    from app.auth import entra_auth

    # Initialize authentication
    entra_auth.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(api_bp, url_prefix="/api/web")
    app.register_blueprint(integrated_api_bp, url_prefix="/api/v1")


def _register_error_handlers(app):
    """Register error handlers."""
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f"Server error: {error}")
        return {"error": "Internal server error"}, 500


def _init_context_processors(app):
    """Initialize context processors for templates."""
    @app.context_processor
    def inject_config():
        return {
            "app_name": "Knowledge Hub Monitoring",
            "auth_enabled": app.config.get("AUTH_ENABLED", False)
        }
