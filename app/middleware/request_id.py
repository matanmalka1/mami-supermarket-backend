"""Middleware for binding a request-id/correlation header."""

import secrets

from flask import g, request

REQUEST_ID_HEADER = "X-Request-Id"

def register_request_id(app) -> None:
    """Ensure every request has a correlative identifier."""

    @app.before_request
    def _attach_request_id():
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if not request_id:
            request_id = secrets.token_hex(16)
        g.request_id = request_id

    @app.after_request
    def _propagate_request_id(response):
        response.headers.setdefault(REQUEST_ID_HEADER, g.get("request_id", ""))
        return response
