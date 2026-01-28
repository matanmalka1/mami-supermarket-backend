"""Admin analytics: revenue endpoint (sum of completed orders, grouped by day/month)."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.services.admin_analytics_service import AdminAnalyticsService
from app.utils.responses import success_envelope
from app.schemas.admin_branches_query import RevenueQuery

blueprint = Blueprint("admin_analytics", __name__)

@blueprint.get("/revenue")
@jwt_required()
@require_role(Role.ADMIN)
def revenue():
    try:
        params = RevenueQuery(**request.args)
    except Exception as e:
        return jsonify({"error": str(e)}), 422
    data = AdminAnalyticsService.get_revenue(params.range, params.granularity)
    return jsonify(success_envelope(data))
