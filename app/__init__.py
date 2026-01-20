"""Application factory and package definition for Mami Supermarket backend."""

from flask import Flask

from .config import AppConfig
from .extensions import db, jwt, limiter
from .middleware import register_middlewares
from .utils.logging_config import setup_structured_logging
from .routes.v1 import (
    admin,
    auth,
    branches,
    cart,
    catalog,
    checkout,
    health,
    stock_requests,
    ops,
    orders,
    audit,
)

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
    _register_blueprints(app)
    _register_delivery_branch_check(app)

    return app


def _register_extensions(app: Flask) -> None:
    from datetime import timedelta

    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(minutes=15))
    app.config.setdefault("JWT_REFRESH_TOKEN_EXPIRES", timedelta(days=30))

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)


def _register_blueprints(app: Flask) -> None:


    app.register_blueprint(auth.blueprint, url_prefix="/api/v1/auth")
    app.register_blueprint(catalog.blueprint, url_prefix="/api/v1/catalog")
    app.register_blueprint(health.blueprint, url_prefix="/api/v1/health")
    app.register_blueprint(branches.blueprint, url_prefix="/api/v1")
    app.register_blueprint(cart.blueprint, url_prefix="/api/v1/cart")
    app.register_blueprint(checkout.blueprint, url_prefix="/api/v1/checkout")
    app.register_blueprint(stock_requests.blueprint, url_prefix="/api/v1/stock-requests")
    app.register_blueprint(orders.blueprint, url_prefix="/api/v1/orders")
    app.register_blueprint(ops.blueprint, url_prefix="/api/v1/ops")
    app.register_blueprint(audit.blueprint, url_prefix="/api/v1/admin/audit")
    app.register_blueprint(admin.blueprint, url_prefix="/api/v1/admin")


def _register_delivery_branch_check(app: Flask) -> None:
    """Validate DELIVERY_SOURCE_BRANCH_ID exists; run once lazily."""
    from flask import g, request
    from .services.branches import BranchService

    @app.before_request
    def _ensure_branch():
        if request.path.startswith("/api/v1/health"):
            return
        if getattr(g, "_delivery_branch_validated", False):
            return
        try:
            BranchService.ensure_delivery_source_branch_exists(app.config.get("DELIVERY_SOURCE_BRANCH_ID", ""))
        except Exception:
            # let the global error handlers format the response
            raise
        g._delivery_branch_validated = True
