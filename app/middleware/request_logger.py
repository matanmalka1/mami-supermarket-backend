"""Lightweight request logging middleware."""

from __future__ import annotations

import time

from flask import g, request


def register_request_logger(app) -> None:
    @app.before_request
    def _start_timer():
        g._request_started_at = time.monotonic()

    @app.after_request
    def _log_request(response):
        try:
            duration_ms = None
            if hasattr(g, "_request_started_at"):
                duration_ms = round((time.monotonic() - g._request_started_at) * 1000, 2)
            app.logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "request_id": getattr(g, "request_id", None),
                    "ip": request.remote_addr,
                },
            )
        except Exception:
            app.logger.exception("request_log_failed")
        return response
