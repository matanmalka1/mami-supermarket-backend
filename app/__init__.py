"""Application factory and package definition for Mami Supermarket backend."""

from flask import Flask

from .services.branch import BranchCoreService
from .config import AppConfig
from .extensions import db, jwt, limiter
from .middleware import register_middlewares
from .utils.logging_config import setup_structured_logging
from .routes import (
    auth_routes,
    auth_otp_routes,
    branches_routes,
    cart_routes,
    catalog_routes,
    checkout_routes,
    health_routes,
    orders_routes,
    profile_routes,
    stock_requests_routes,
    ops_routes,
    audit_routes,
)
from .routes.admin_routes import (
    admin_analytics_routes,
    admin_branches_routes,
    admin_catalog_routes,
    admin_settings_routes,
    admin_users_routes,
)
from app.middleware.cors import register_cors


def create_app(config: AppConfig | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        instance_relative_config=False,
        static_folder=None,
    )

    cfg = config or AppConfig()
    app.config.from_mapping(vars(cfg))

    setup_structured_logging(app)
    _register_extensions(app)
    register_middlewares(app)
    register_cors(app)
    _register_blueprints(app)
    _register_options_short_circuit(app)
    with app.app_context():
        BranchCoreService.ensure_delivery_source_branch_exists(app.config.get("DELIVERY_SOURCE_BRANCH_ID", ""))

    return app

def _register_extensions(app: Flask) -> None:
    from datetime import timedelta

    expires_minutes = app.config.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 240)
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(minutes=expires_minutes))
    app.config.setdefault("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

def _register_blueprints(app: Flask) -> None:
    from .routes import ops_actions_routes, store_routes

    app.register_blueprint(auth_routes.blueprint, url_prefix="/api/v1/auth")
    app.register_blueprint(auth_otp_routes.blueprint, url_prefix="/api/v1/auth")
    app.register_blueprint(profile_routes.blueprint, url_prefix="/api/v1/me")
    app.register_blueprint(catalog_routes.blueprint, url_prefix="/api/v1/catalog")
    app.register_blueprint(store_routes.blueprint, url_prefix="/api/v1/store")
    app.register_blueprint(health_routes.blueprint, url_prefix="/api/v1/health")
    app.register_blueprint(branches_routes.blueprint, url_prefix="/api/v1")
    app.register_blueprint(cart_routes.blueprint, url_prefix="/api/v1/cart")
    app.register_blueprint(checkout_routes.blueprint, url_prefix="/api/v1/checkout")
    app.register_blueprint(stock_requests_routes.blueprint, url_prefix="/api/v1/stock-requests")
    app.register_blueprint(ops_actions_routes.blueprint, url_prefix="/api/v1/ops")
    app.register_blueprint(orders_routes.blueprint, url_prefix="/api/v1/orders")
    app.register_blueprint(ops_routes.blueprint, url_prefix="/api/v1/ops")
    app.register_blueprint(audit_routes.blueprint, url_prefix="/api/v1/admin/audit")
    app.register_blueprint(admin_catalog_routes.blueprint, url_prefix="/api/v1/admin")
    app.register_blueprint(admin_branches_routes.blueprint, url_prefix="/api/v1/admin")
    app.register_blueprint(admin_settings_routes.blueprint, url_prefix="/api/v1/admin")
    app.register_blueprint(admin_users_routes.blueprint, url_prefix="/api/v1/admin/users")
    app.register_blueprint(admin_analytics_routes.blueprint, url_prefix="/api/v1/admin/analytics")
    limiter.exempt(health_routes.blueprint)

def _register_options_short_circuit(app: Flask) -> None:
    from flask import request

    @app.before_request
    def _allow_options_preflight():
        if request.method == "OPTIONS":
            return "", 204
