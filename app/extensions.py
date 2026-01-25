"""Extension registration (DB, JWT, limiter)."""

from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

db = SQLAlchemy()
jwt = JWTManager()

def _skip_options() -> bool:
    return request.method == "OPTIONS"

lim_defaults = tuple(
    limit.strip()
    for limit in os.environ.get("RATE_LIMIT_DEFAULTS", "200 per day, 50 per hour").split(",")
    if limit.strip()
)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=lim_defaults,
)
limiter.request_filter = _skip_options
