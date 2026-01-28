"""Middleware helpers for managing error responses."""

from __future__ import annotations

from typing import Mapping

from flask import jsonify, current_app, request
from flask_jwt_extended.exceptions import JWTExtendedException
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

HTTP_ERROR_MESSAGES: dict[int, str] = {
    400: "The request was not formed correctly. Please review your input.",
    401: "Authentication is required. Please sign in and try again.",
    403: "You do not have permission to take that action.",
    404: "We cannot find the requested resource.",
    405: "The requested method is not supported for this endpoint.",
    409: "There is a conflict with the current state of the resource.",
    410: "The requested resource is no longer available.",
    422: "Some of the submitted values were invalid.",
}

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
        payload = error_envelope(
            error.code,
            error.message,
            status_code=error.status_code,
            details=error.details,
        )
        return jsonify(payload), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        payload = error_envelope(
            "VALIDATION_ERROR",
            "Please correct the highlighted input and submit again.",
            status_code=400,
            details={"errors": list(error.errors())},
        )
        return jsonify(payload), 400

    @app.errorhandler(JWTExtendedException)
    def handle_auth_error(error: JWTExtendedException):
        payload = error_envelope(
            "AUTH_ERROR",
            "Your session has expired or is invalid. Please log in again.",
            status_code=401,
        )
        return jsonify(payload), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        status_code = error.code or 500
        payload = error_envelope(
            f"HTTP_{status_code}",
            HTTP_ERROR_MESSAGES.get(
                status_code,
                "The request could not be completed as submitted. Please try again.",
            ),
            status_code=status_code,
        )
        return jsonify(payload), status_code

    @app.errorhandler(Exception)
    def handle_unhandled_error(error: Exception):
        request_id = (
            request.headers.get("X-Request-Id")
            or request.environ.get("HTTP_X_REQUEST_ID")
            or "unknown"
        )
        current_app.logger.exception(
            "Unhandled error during %s %s (request_id=%s)",
            request.method,
            request.path,
            request_id,
        )
        payload = error_envelope(
            "UNEXPECTED_ERROR",
            "We could not complete your request at this time. Please try again shortly.",
            status_code=500,
        )
        return jsonify(payload), 500
