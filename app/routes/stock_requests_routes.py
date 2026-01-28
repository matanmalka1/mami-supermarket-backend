"""Stock request endpoints for employees and managers/admins."""

from __future__ import annotations
from flask import Blueprint, jsonify, request 
from flask_jwt_extended import jwt_required

from app.middleware.auth import require_role
from app.models.enums import Role

from app.schemas.admin_branches_query import AdminStockRequestsQuery
from app.services.stock_requests import StockRequestEmployeeService, StockRequestReviewService
from app.utils.request_utils import current_user_id, parse_json_or_400, parse_pagination
from app.utils.responses import pagination_envelope, success_envelope , error_envelope
from app.schemas.stock_requests import (
    BulkReviewRequest,
    StockRequestCreateRequest,
    StockRequestReviewRequest,
)

blueprint = Blueprint("stock_requests", __name__)

## CREATE (Stock Request)
@blueprint.post("")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def create_stock_request():
    payload = StockRequestCreateRequest.model_validate(parse_json_or_400())
    result = StockRequestEmployeeService.create_request(current_user_id(), payload)
    return jsonify(success_envelope(result)), 201

## READ (My Stock Requests)
@blueprint.get("/my")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_my_requests():
    limit, offset = parse_pagination()
    rows, total = StockRequestEmployeeService.list_my(current_user_id(), limit, offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, limit, offset)))

## READ (Admin Stock Requests)
@blueprint.get("/admin")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_admin_requests():
    params = AdminStockRequestsQuery(**request.args)
    rows, total = StockRequestReviewService.list_admin(params.status, params.limit, params.offset)
    return jsonify(success_envelope(rows, pagination_envelope(total, params.limit, params.offset)))

## READ (Admin Stock Request Detail)
@blueprint.get("/admin/<int:request_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def get_admin_request(request_id: int):
    """Get detailed stock request information."""
    result = StockRequestReviewService.get_request(request_id)
    return jsonify(success_envelope(result))

## UPDATE (Review Stock Request)
@blueprint.patch("/admin/<int:request_id>/resolve")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def review_request(request_id: int):
    payload = StockRequestReviewRequest.model_validate(parse_json_or_400())
    result = StockRequestReviewService.review(
        request_id,
        payload.status,
        payload.approved_quantity,
        payload.rejection_reason,
        current_user_id(),
    )
    return jsonify(success_envelope(result))

## UPDATE (Bulk Review Stock Requests)
@blueprint.patch("/admin/bulk-review")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def bulk_review():
    payload = BulkReviewRequest.model_validate(parse_json_or_400())
    results = StockRequestReviewService.bulk_review(payload, current_user_id())
    return jsonify(success_envelope({"results": results}))
