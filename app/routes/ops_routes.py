"""Operations endpoints for employees/managers."""

from __future__ import annotations

from datetime import datetime
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import OrderStatus, Role
from app.services.ops import OpsOrderQueryService, OpsOrderUpdateService
from app.schemas.ops import OpsOrdersQuery
from app.services.ops.custom_ops_service import (
    create_batch_for_ops,
    get_ops_performance,
    get_ops_alerts,
)
from app.services.stock_requests import StockRequestEmployeeService, StockRequestReviewService
from app.schemas.stock_requests import StockRequestCreateRequest
from app.schemas.ops import UpdatePickStatusRequest, UpdateOrderStatusRequest ,OpsStockRequestsQuery
from app.utils.request_params import optional_int
from app.utils.request_utils import current_user_id, parse_pagination, parse_iso_date
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("ops", __name__)

def _parse_filters() -> tuple[OrderStatus | None, datetime | None, datetime | None, int, int]:
    status_val = request.args.get("status")
    try:
        status = OrderStatus(status_val) if status_val else None
    except ValueError:
        raise DomainError("BAD_REQUEST", "Invalid status filter", status_code=400)
    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")
    limit, offset = parse_pagination()
    return status, parse_iso_date(date_from), parse_iso_date(date_to), limit, offset


## READ (List Orders)
@blueprint.get("/orders")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_orders():
    params = OpsOrdersQuery(**request.args)
    orders, total = OpsOrderQueryService.list_orders(
        params.status, params.date_from, params.date_to, params.limit, params.offset
    )
    return jsonify(success_envelope(orders, pagination_envelope(total, params.limit, params.offset)))


## READ (Get Order)
@blueprint.get("/orders/<int:order_id>")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def get_order(order_id: int):
    order = OpsOrderQueryService.get_order(order_id)
    return jsonify(success_envelope(order))


## UPDATE (Picked Status)
@blueprint.patch("/orders/<int:order_id>/items/<int:item_id>/picked-status")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def update_picked_status(order_id: int, item_id: int):
    payload = UpdatePickStatusRequest.model_validate(request.get_json() or {})
    order = OpsOrderUpdateService.update_item_status(order_id, item_id, payload.picked_status, current_user_id())
    return jsonify(success_envelope(order))

# Endpoint: POST /ops/batches
## CREATE (Batch)
@blueprint.post("/batches")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def create_batch():
    user_id = current_user_id()
    payload = request.get_json() or {}
    # Optionally: define a Pydantic schema for batch creation if structure is known
    batch_data = create_batch_for_ops(user_id, payload)
    return jsonify(success_envelope(batch_data)), 201

# Endpoint: GET /api/v1/ops/stock-requests
## READ (Stock Requests)
@blueprint.get("/stock-requests")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def list_ops_stock_requests():
    
    params = OpsStockRequestsQuery(**request.args)
    # Assuming list_ops is a review/admin operation; fallback to employee if needed
    if hasattr(StockRequestReviewService, "list_ops"):
        rows, total = StockRequestReviewService.list_ops(
            params.branch_id, params.status, params.limit, params.offset
        )
    else:
        rows, total = StockRequestEmployeeService.list_ops(
            params.branch_id, params.status, params.limit, params.offset
        )
    return jsonify(success_envelope(rows, pagination_envelope(total, params.limit, params.offset)))

# Endpoint: POST /api/v1/ops/stock-requests
## CREATE (Stock Request)
@blueprint.post("/stock-requests")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def create_ops_stock_request():
    payload = StockRequestCreateRequest.model_validate(request.get_json() or {})
    # Use EmployeeService for creation
    result = StockRequestEmployeeService.create_request(current_user_id(), payload)
    return jsonify(success_envelope(result)), 201

# Endpoint: GET /ops/performance
## READ (Performance)
@blueprint.get("/performance")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def get_performance():
    user_id = current_user_id()
    performance_data = get_ops_performance(user_id)
    return jsonify(success_envelope(performance_data)), 200

# Endpoint: GET /ops/alerts
## READ (Alerts)
@blueprint.get("/alerts")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def get_alerts():
    alerts = get_ops_alerts(current_user_id())
    return jsonify(success_envelope(alerts)), 200


## UPDATE (Order Status)
@blueprint.patch("/orders/<int:order_id>/status")
@jwt_required()
@require_role(Role.EMPLOYEE, Role.MANAGER, Role.ADMIN)
def update_order_status(order_id: int):
    payload = UpdateOrderStatusRequest.model_validate(request.get_json() or {})
    user = getattr(g, "current_user", None)
    actor_role = user.role if user else Role.EMPLOYEE
    order = OpsOrderUpdateService.update_order_status(order_id, payload.status, current_user_id(), actor_role)
    return jsonify(success_envelope(order))
