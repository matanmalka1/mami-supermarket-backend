"""Audit listing for admin/manager."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import Role
from app.services.audit_service import AuditQueryService
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("audit", __name__)


def _parse_filters() -> tuple[dict, int, int]:
    params: dict = {}
    if et := request.args.get("entityType"):
        params["entity_type"] = et
    if action := request.args.get("action"):
        params["action"] = action
    if actor := request.args.get("actorId"):
        params["actor_user_id"] = actor
    def _parse_dt(value: str | None):
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid date format; use ISO 8601", status_code=400)
    params["date_from"] = _parse_dt(request.args.get("dateFrom"))
    params["date_to"] = _parse_dt(request.args.get("dateTo"))
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except (TypeError, ValueError):
        raise DomainError("BAD_REQUEST", "Invalid pagination parameters", status_code=400)
    return params, limit, offset


@blueprint.get("")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_audit():
    filters, limit, offset = _parse_filters()
    rows, total = AuditQueryService.list_logs(filters, limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))
