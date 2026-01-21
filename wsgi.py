"""WSGI entry point for production servers."""

from app import create_app

application = create_app()
