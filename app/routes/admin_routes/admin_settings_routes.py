from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.models import GlobalSettings
from app.extensions import db
from app.utils.responses import success_envelope
from app.utils.request_utils import current_user_id
from app.services.audit_service import AuditService

blueprint = Blueprint("admin_settings", __name__, url_prefix="/api/v1/admin")


def get_or_create_settings() -> GlobalSettings:
    """Get existing settings or create default settings."""
    settings = db.session.query(GlobalSettings).first()
    if not settings:
        settings = GlobalSettings(
            delivery_min=150.0,
            delivery_fee=30.0,
            free_threshold=200.0,
        )
        db.session.add(settings)
        db.session.commit()
    return settings


## READ (Settings)
@blueprint.get("/settings")
@jwt_required()
@require_role(Role.ADMIN)
def get_settings():
    settings = get_or_create_settings()
    return jsonify(success_envelope(settings.to_dict()))


## UPDATE (Settings)
@blueprint.put("/settings")
@jwt_required()
@require_role(Role.ADMIN, Role.MANAGER)
def update_settings():
    data = request.get_json() or {}
    user_id = current_user_id()
    
    settings = get_or_create_settings()
    old_values = settings.to_dict()
    
    # Update allowed fields
    if "delivery_min" in data:
        settings.delivery_min = float(data["delivery_min"])
    if "delivery_fee" in data:
        settings.delivery_fee = float(data["delivery_fee"])
    if "free_threshold" in data:
        settings.free_threshold = float(data["free_threshold"])
    
    settings.updated_by = user_id

    AuditService.log_event(
        entity_type="global_settings",
        action="UPDATE",
        actor_user_id=user_id,
        entity_id=settings.id,
        old_value=old_values,
        new_value=settings.to_dict(),
    )

    db.session.commit()

    return jsonify(success_envelope(settings.to_dict()))
