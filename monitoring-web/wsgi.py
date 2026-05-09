"""Application entry point for the Monitoring Web Frontend."""
import os
import sys

# Ensure the current directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Handle the case where this script is run from a different working directory
# (e.g., when deployed in Azure App Service)
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from app import create_app
    from app.config import get_config
except ImportError as e:
    # Provide helpful error message for debugging
    print(f"Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script directory: {current_dir}")
    raise

# Create Flask app instance
app = create_app(get_config())

if __name__ == "__main__":
    config = get_config()
    app.run(
        host=config.__dict__.get("HOST", "0.0.0.0"),
        port=config.__dict__.get("PORT", 5001),
        debug=config.DEBUG
    )
