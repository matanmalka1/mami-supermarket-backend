"""Admin-only ops actions that currently return placeholder data."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models import Branch, Order, OrderItem
from app.models.enums import Role
from app.services.audit_service import AuditService
from app.schemas.ops import DamageReportRequest
from app.utils.request_utils import current_user_id
from app.utils.responses import success_envelope

blueprint = Blueprint("ops_actions", __name__)


## UPDATE (Sync Order)
@blueprint.post("/orders/<int:order_id>/sync")
@jwt_required()
@require_role(Role.ADMIN)
def sync_order(order_id: int):
    """Return a successful sync flag."""
    order = db.session.get(Order, order_id)
    if not order:
        raise DomainError("NOT_FOUND", "Order not found", status_code=404)
    AuditService.log_event(
        entity_type="order",
        action="SYNC",
        actor_user_id=current_user_id(),
        entity_id=order_id,
        context={"status": order.status.value},
    )
    return jsonify(success_envelope({"synced": True}))


## CREATE (Report Damage)
@blueprint.post("/orders/<int:order_id>/items/<int:item_id>/report-damage")
@jwt_required()
@require_role(Role.ADMIN)
def report_damage(order_id: int, item_id: int):
    payload = DamageReportRequest.model_validate(request.get_json() or {})
    order = db.session.get(Order, order_id)
    if not order:
        raise DomainError("NOT_FOUND", "Order not found", status_code=404)
    item = (
        db.session.query(OrderItem)
        .filter_by(id=item_id, order_id=order_id)
        .first()
    )
    if not item:
        raise DomainError("NOT_FOUND", "Order item not found", status_code=404)
    AuditService.log_event(
        entity_type="order_item",
        action="REPORT_DAMAGE",
        actor_user_id=current_user_id(),
        entity_id=item_id,
        new_value={
            "reason": payload.reason,
            "notes": payload.notes,
        },
    )
    return jsonify(success_envelope({"reported": True})), 201


## READ (Map View)
@blueprint.get("/map")
@jwt_required()
@require_role(Role.ADMIN)
def map_view():
    """Return available branch coordinates."""
    branches = (
        db.session.query(Branch)
        .filter_by(is_active=True)
        .order_by(Branch.name.asc())
        .all()
    )
    branch_rows = []
    for branch in branches:
        branch_rows.append(
            {
                "id": str(branch.id),
                "name": branch.name,
                "lat": getattr(branch, "latitude", None),
                "lng": getattr(branch, "longitude", None),
            }
        )
    return jsonify(success_envelope({"branches": branch_rows, "bins": []}))
