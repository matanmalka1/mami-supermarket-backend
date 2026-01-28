"""Package entrypoint for admin blueprints."""

from . import (
    admin_analytics_routes,
    admin_branches_routes,
    admin_catalog_routes,
    admin_settings_routes,
    admin_users_routes,
)

__all__ = [
    "admin_analytics_routes",
    "admin_branches_routes",
    "admin_catalog_routes",
    "admin_settings_routes",
    "admin_users_routes",
]
