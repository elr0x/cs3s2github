"""Configuration management for the Monitoring Web Frontend."""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = False
    TESTING = False

    # Backend API configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api/v1")
    API_KEY = os.getenv("API_KEY", "")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))

    # Session configuration
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Authentication (Entra ID - Proftask Tenant)
    ENTRA_ID_CLIENT_ID = os.getenv("ENTRA_ID_CLIENT_ID", "")
    ENTRA_ID_CLIENT_SECRET = os.getenv("ENTRA_ID_CLIENT_SECRET", "")
    ENTRA_ID_TENANT_ID = os.getenv("ENTRA_ID_TENANT_ID", "")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5001/auth/callback")
    AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

    # Data refresh intervals (seconds)
    METRICS_REFRESH_INTERVAL = int(os.getenv("METRICS_REFRESH_INTERVAL", 30))
    HEALTH_REFRESH_INTERVAL = int(os.getenv("HEALTH_REFRESH_INTERVAL", 60))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    AUTH_ENABLED = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    AUTH_ENABLED = False
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False


def get_config():
    """Get configuration based on environment."""
    env = os.getenv("FLASK_ENV", "development").lower()
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    return config_map.get(env, DevelopmentConfig)
