"""CORS setup for API endpoints."""

from __future__ import annotations

from flask_cors import CORS
from app.middleware.error_handler import DomainError


def register_cors(app) -> None:
    allowed = (app.config.get("CORS_ALLOWED_ORIGINS") or "").strip()
    if allowed == "*" and app.config.get("ENV") == "production":
        raise DomainError("CONFIG_ERROR", "CORS_ALLOWED_ORIGINS cannot be '*' in production", status_code=500)
    origins = "*" if allowed == "*" else [o.strip() for o in allowed.split(",") if o.strip()]
    CORS(
        app,
        resources={r"/api/*": {"origins": origins}},
        supports_credentials=True,
        expose_headers=["X-Request-Id"],
        allow_headers=["Content-Type", "Authorization", "X-Request-Id"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
