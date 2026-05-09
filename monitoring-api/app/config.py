import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Authentication
    API_KEY = os.getenv("API_KEY")

    # Azure SQL Database connection string
    DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

    # Flask settings
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", 5000))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False