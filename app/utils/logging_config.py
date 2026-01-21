"""Logging utilities that emit request-aware outputs."""

from __future__ import annotations
import logging
from flask import g, has_request_context

class RequestIDFilter(logging.Filter):
    """Inject the current request id into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        request_id = "-"
        if has_request_context():
            request_id = getattr(g, "request_id", request_id)
        record.request_id = request_id
        return True

def setup_structured_logging(app) -> None:
    """Ensure logs always include a request id and consistent formatter."""

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s] [req=%(request_id)s] %(message)s")
    )
    handler.addFilter(RequestIDFilter())
    handler.setLevel(logging.INFO)

    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)
