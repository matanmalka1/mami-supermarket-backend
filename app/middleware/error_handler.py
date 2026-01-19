"""Middleware helpers for managing error responses."""

from __future__ import annotations

from typing import Mapping

from flask import jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from ..utils.responses import error_envelope


class DomainError(Exception):
    """Domain exception carrying a code and human-readable message."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: Mapping[str, str] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def register_error_handlers(app) -> None:
    """Register consistent error handlers on the app."""

    @app.errorhandler(DomainError)
    def handle_domain_error(error: DomainError):
        payload = error_envelope(error.code, error.message, error.details)
        return jsonify(payload), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        payload = error_envelope(
            "VALIDATION_ERROR",
            "Validation of payload failed",
            {"errors": list(error.errors())},
        )
        return jsonify(payload), 400

    @app.errorhandler(JWTExtendedException)
    def handle_auth_error(error: JWTExtendedException):
        payload = error_envelope(
            "AUTH_ERROR",
            str(error),
        )
        return jsonify(payload), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        payload = error_envelope(
            "HTTP_ERROR", error.description or "HTTP error occurred", {}
        )
        return jsonify(payload), error.code or 500

    @app.errorhandler(Exception)
    def handle_unhandled_error(error: Exception):
        payload = error_envelope("INTERNAL_ERROR", "Unexpected error")
        return jsonify(payload), 500
