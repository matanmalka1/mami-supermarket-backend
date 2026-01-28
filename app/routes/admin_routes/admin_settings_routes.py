from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.utils.responses import success_envelope

blueprint = Blueprint("admin_settings", __name__, url_prefix="/api/v1/admin")

## READ (Settings)
@blueprint.get("/settings")
@jwt_required()
@require_role(Role.ADMIN)
def get_settings():
    config = current_app.config
    settings = {
        "delivery_min": config.get("DELIVERY_MIN_TOTAL", 150),
        "delivery_fee": config.get("DELIVERY_FEE_UNDER_MIN", 30),
        "slots": "06:00-22:00",
    }
    return jsonify(success_envelope(settings))


# Minimal update endpoint for settings
## UPDATE (Settings)
@blueprint.put("/settings")
@jwt_required()
@require_role(Role.ADMIN, Role.MANAGER)
def update_settings():
    data = (request.get_json() or {})
    # Only allow updating known settings
    allowed_keys = {"delivery_min", "delivery_fee", "slots"}
    updates = {k: v for k, v in data.items() if k in allowed_keys}
    # In real app, persist to DB/config. Here, just echo back for demo.
    # Optionally: update current_app.config if needed
    return jsonify(success_envelope(updates))
