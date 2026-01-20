"""CORS setup for API endpoints."""

from __future__ import annotations

from flask_cors import CORS


def register_cors(app) -> None:
    # Default to permissive CORS for /api; tighten origins in config if needed.
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        expose_headers=["X-Request-Id"],
        allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
