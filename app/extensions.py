"""Extension registration (DB, JWT, limiter)."""

from flask import current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()


@jwt.token_in_blocklist_loader
def _check_token_in_blocklist(_jwt_header, jwt_data: dict) -> bool:
    from .models.token_blocklist import TokenBlocklist

    jti = jwt_data.get("jti")
    if not jti:
        return False
    return db.session.query(TokenBlocklist).filter_by(jti=jti).first() is not None


def _skip_options() -> bool:
    return request.method == "OPTIONS"


def get_rate_limit_defaults():
    limits = current_app.config.get("RATE_LIMIT_DEFAULTS", "200 per day, 50 per hour")
    return tuple(limit.strip() for limit in limits.split(",") if limit.strip())


def _dynamic_default_limits() -> str:
    defaults = get_rate_limit_defaults()
    return ", ".join(defaults) if defaults else ""


# Use a callable that reads the config each request so rate limits follow runtime config.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_dynamic_default_limits],
)
limiter.request_filter = _skip_options
