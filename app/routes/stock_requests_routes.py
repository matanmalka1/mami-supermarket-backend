"""Stock request endpoints for employees and managers/admins."""

from __future__ import annotations
from uuid import UUID
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import Role, StockRequestStatus
from app.schemas.stock_requests import (
    BulkReviewRequest,
    StockRequestCreateRequest,
    StockRequestReviewRequest,
)
from app.services.stock_requests_service import StockRequestService
from app.utils.request_utils import current_user_id, parse_json_or_400, parse_pagination
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("stock_requests", __name__)

@blueprint.post("")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def create_stock_request():
    payload = StockRequestCreateRequest.model_validate(parse_json_or_400())
    result = StockRequestService.create_request(current_user_id(), payload)
    return jsonify(success_envelope(result)), 201

@blueprint.get("/my")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_my_requests():
    limit, offset = parse_pagination()
    rows, total = StockRequestService.list_my(current_user_id(), limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))

@blueprint.get("/admin")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_admin_requests():
    status_val = request.args.get("status")
    try:
        status = StockRequestStatus(status_val) if status_val else None
    except ValueError:
        raise DomainError("BAD_REQUEST", "Invalid status filter", status_code=400)
    limit, offset = parse_pagination()
    rows, total = StockRequestService.list_admin(status, limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))

@blueprint.patch("/admin/<uuid:request_id>/review")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def review_request(request_id: UUID):
    payload = StockRequestReviewRequest.model_validate(parse_json_or_400())
    result = StockRequestService.review(
        request_id,
        payload.status,
        payload.approved_quantity,
        payload.rejection_reason,
        current_user_id(),
    )
    return jsonify(success_envelope(result))

@blueprint.patch("/admin/bulk-review")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def bulk_review():
    payload = BulkReviewRequest.model_validate(parse_json_or_400())
    results = StockRequestService.bulk_review(payload, current_user_id())
    return jsonify(success_envelope({"results": results}))
