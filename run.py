"""Development entry point for the Mami Supermarket backend.

This module creates a Flask application instance using the Application Factory pattern.
The global `app` variable is required for WSGI servers like Gunicorn to discover the application.

Usage:
    Development: python run.py
    Production (Gunicorn): gunicorn run:app
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file for local development
# In production (Render, Heroku, etc.), environment variables are injected by the platform
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from app import create_app

# Create Flask application instance
# IMPORTANT: This global `app` variable is required for Gunicorn to discover the application
# Gunicorn will import this module and look for the `app` object via: gunicorn run:app
app = create_app()


if __name__ == "__main__":
    # Run the Flask development server
    # For production deployments, use a WSGI server like Gunicorn instead
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("APP_ENV", "production") != "production"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        threaded=True
    )
