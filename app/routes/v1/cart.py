"""Customer cart endpoints."""

from __future__ import annotations

from uuid import UUID

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.middleware.error_handler import DomainError
from app.schemas.cart import CartItemUpsertRequest
from app.services.cart import CartService
from app.utils.responses import success_envelope

blueprint = Blueprint("cart", __name__)


def _current_user_id() -> UUID:
    ident = get_jwt_identity()
    if not ident:
        raise DomainError("AUTH_REQUIRED", "Authentication required", status_code=401)
    return UUID(ident)


def _parse_payload() -> dict:
    body = request.get_json()
    if not body:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    return body


@blueprint.get("")
@jwt_required()
def get_cart():
    user_id = _current_user_id()
    cart = CartService.get_cart(user_id)
    return jsonify(success_envelope(cart))


@blueprint.post("/items")
@jwt_required()
def add_item():
    user_id = _current_user_id()
    payload = CartItemUpsertRequest.model_validate(_parse_payload())
    cart = CartService.add_item(user_id, payload.product_id, payload.quantity)
    return jsonify(success_envelope(cart)), 201


@blueprint.put("/items/<uuid:item_id>")
@jwt_required()
def update_item(item_id: UUID):
    user_id = _current_user_id()
    payload = CartItemUpsertRequest.model_validate(_parse_payload())
    cart_id = CartService.get_or_create_cart(user_id).id
    cart = CartService.update_item(user_id, cart_id, item_id, payload.quantity)
    return jsonify(success_envelope(cart))


@blueprint.delete("/items/<uuid:item_id>")
@jwt_required()
def delete_item(item_id: UUID):
    user_id = _current_user_id()
    cart = CartService.delete_item(user_id, CartService.get_or_create_cart(user_id).id, item_id)
    return jsonify(success_envelope(cart))


@blueprint.delete("")
@jwt_required()
def clear_cart():
    user_id = _current_user_id()
    cart = CartService.clear_cart(user_id, CartService.get_or_create_cart(user_id).id)
    return jsonify(success_envelope(cart))
