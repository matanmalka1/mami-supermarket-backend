"""Customer cart endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.schemas.cart import CartItemUpsertRequest
from app.services.cart_service import CartService
from app.utils.request_utils import current_user_id, parse_json_or_400
from app.utils.responses import success_envelope

blueprint = Blueprint("cart", __name__)


## READ (Cart)
@blueprint.get("")
@jwt_required()
def get_cart():
    user_id = current_user_id()
    cart = CartService.get_cart(user_id)
    return jsonify(success_envelope(cart))


## CREATE (Cart Item)
@blueprint.post("/items")
@jwt_required()
def add_item():
    user_id = current_user_id()
    payload = CartItemUpsertRequest.model_validate(parse_json_or_400())
    cart = CartService.add_item(user_id, payload.product_id, payload.quantity)
    return jsonify(success_envelope(cart)), 201


## UPDATE (Cart Item)
@blueprint.put("/items/<int:item_id>")
@jwt_required()
def update_item(item_id: int):
    user_id = current_user_id()
    payload = CartItemUpsertRequest.model_validate(parse_json_or_400())
    cart_id = CartService.get_or_create_cart(user_id).id
    cart = CartService.update_item(user_id, cart_id, item_id, payload.quantity)
    return jsonify(success_envelope(cart))


## DELETE (Cart Item)
@blueprint.delete("/items/<int:item_id>")
@jwt_required()
def delete_item(item_id: int):
    user_id = current_user_id()
    cart = CartService.delete_item(user_id, CartService.get_or_create_cart(user_id).id, item_id)
    return jsonify(success_envelope(cart))

## DELETE (Clear Cart)
@blueprint.delete("")
@jwt_required()
def clear_cart():
    user_id = current_user_id()
    cart = CartService.clear_cart(user_id, CartService.get_or_create_cart(user_id).id)
    return jsonify(success_envelope(cart))
