"""Middleware package helpers."""

from .cors import register_cors
from .error_handler import register_error_handlers
from .request_id import register_request_id
from .request_logger import register_request_logger
from .security_headers import register_security_headers
from .db_session import register_db_session_teardown

def register_middlewares(app) -> None:
    register_cors(app)
    register_request_id(app)
    register_request_logger(app)
    register_security_headers(app)
    register_error_handlers(app)
    register_db_session_teardown(app)
