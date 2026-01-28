"""Admin analytics: revenue endpoint (sum of completed orders, grouped by day/month)."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.services.admin_analytics_service import AdminAnalyticsService
from app.utils.responses import success_envelope

blueprint = Blueprint("admin_analytics", __name__)


@blueprint.get("/revenue")
@jwt_required()
@require_role(Role.ADMIN)
def revenue():
    range_ = request.args.get("range", "30d")
    granularity = request.args.get("granularity")
    data = AdminAnalyticsService.get_revenue(range_, granularity)
    return jsonify(success_envelope(data))
