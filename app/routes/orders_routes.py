"""Customer order endpoints."""

from __future__ import annotations
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.order_service import OrderService
from app.utils.request_utils import current_user_id, parse_pagination
from app.utils.responses import pagination_envelope, success_envelope

blueprint = Blueprint("orders", __name__)

## READ (List Orders)
@blueprint.get("")
@jwt_required()
def list_orders():
    user_id = current_user_id()
    limit, offset = parse_pagination()
    orders, total = OrderService.list_orders(user_id, limit, offset)
    return jsonify(success_envelope(orders, pagination_envelope(total, limit, offset)))

## READ (Get Order)
@blueprint.get("/<int:order_id>")
@jwt_required()
def get_order(order_id: int):
    user_id = current_user_id()
    order = OrderService.get_order(order_id, user_id)
    return jsonify(success_envelope(order))

## UPDATE (Cancel Order)
@blueprint.post("/<int:order_id>/cancel")
@jwt_required()
def cancel_order(order_id: int):
    user_id = current_user_id()
    payload = OrderService.cancel_order(order_id, user_id)
    return jsonify(success_envelope(payload))
