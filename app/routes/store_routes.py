"""Storefront endpoints."""

# PUBLIC: The /shipping-info endpoint is intentionally unauthenticated for public access.
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.schemas.store import WishlistRequest
from app.services.store import WishlistService
from app.utils.request_utils import current_user_id, parse_json_or_400
from app.utils.responses import success_envelope 

blueprint = Blueprint("store", __name__)

_SHIPPING_POLICIES = [
    {
        "key": "delivery",
        "title": "Local delivery",
        "body": "Orders are delivered within 2 business days, subject to branch availability.",
    },
    {
        "key": "pickup",
        "title": "Pickup",
        "body": "Reserve your order online and pick it up from any open branch within 24 hours.",
    },
    {
        "key": "returns",
        "title": "Returns",
        "body": "Return or exchange any item within 7 days with a receipt.",
    },
]

## READ (Notifications)
@blueprint.get("/notifications")
@jwt_required()
def notifications():
    """Return a placeholder empty notification feed."""
    payload = {"items": [], "unread_count": 0}
    return jsonify(success_envelope(payload))

## READ (Shipping Info)

# PUBLIC ENDPOINT
@blueprint.get("/shipping-info")
def shipping_info():
    """Return the available shipping policies."""
    return jsonify(success_envelope({"policies": _SHIPPING_POLICIES}))

## READ (Wishlist)
@blueprint.get("/wishlist")
@jwt_required()
def wishlist():
    """Return the current user's wishlist."""
    # params = WishlistQuery(**request.args)  # Removed: unused variable
    items = WishlistService.list_items(current_user_id())
    return jsonify(success_envelope({"items": items}))


## CREATE (Wishlist Item)
@blueprint.post("/wishlist")
@jwt_required()
def add_to_wishlist():
    payload = WishlistRequest.model_validate(parse_json_or_400())
    item = WishlistService.add_item(current_user_id(), payload.product_id)
    return jsonify(success_envelope(item))


## DELETE (Wishlist Item)
@blueprint.delete("/wishlist/<int:product_id>")
@jwt_required()
def remove_from_wishlist(product_id):
    removed = WishlistService.remove_item(current_user_id(), product_id)
    return jsonify(success_envelope({"removed": removed}))
