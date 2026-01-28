from __future__ import annotations
from flask import Blueprint, jsonify, request
from app.middleware.auth import require_role
from flask_jwt_extended import jwt_required

from app.middleware.error_handler import DomainError
from app.services.inventory_service import InventoryService
from app.services.branch import BranchCoreService, DeliverySlotService
from app.utils.request_params import optional_int, safe_int, toggle_flag
from app.utils.responses import success_envelope 
from app.services.inventory_bulk_service import handle_bulk_inventory_upload
from app.schemas.admin_branches_query import ToggleBranchQuery
from app.models.enums import Role

from app.schemas.branches import (
    BranchAdminRequest,
    DeliverySlotAdminRequest,
    InventoryCreateRequest,
    InventoryUpdateRequest,
)
blueprint = Blueprint("admin_branches", __name__)

## CREATE (Branch)
@blueprint.post("/branches")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def create_branch():
    payload = BranchAdminRequest.model_validate(request.get_json())
    branch = BranchCoreService.create_branch(payload.name, payload.address)
    return jsonify(success_envelope(branch)), 201


## UPDATE (Branch)
@blueprint.patch("/branches/<int:branch_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_branch(branch_id: int):
    payload = BranchAdminRequest.model_validate(request.get_json())
    branch = BranchCoreService.update_branch(branch_id, payload.name, payload.address)
    return jsonify(success_envelope(branch))


## TOGGLE ACTIVE (Branch)
@blueprint.patch("/branches/<int:branch_id>/toggle")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_branch(branch_id: int):
    params = ToggleBranchQuery(**request.args)
    if params.active is None:
        raise DomainError("MISSING_ACTIVE_PARAM", "Missing 'active' query parameter", status_code=400)
    branch = BranchCoreService.toggle_branch(branch_id, params.active)
    return jsonify(success_envelope(branch))


## CREATE (Delivery Slot)
@blueprint.post("/delivery-slots")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def create_delivery_slot():
    payload = DeliverySlotAdminRequest.model_validate(request.get_json())
    slot = DeliverySlotService.create_delivery_slot(
        payload.branch_id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
    )
    return jsonify(success_envelope(slot)), 201


## UPDATE (Delivery Slot)
@blueprint.patch("/delivery-slots/<int:slot_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_delivery_slot(slot_id: int):
    payload = DeliverySlotAdminRequest.model_validate(request.get_json())
    slot = DeliverySlotService.update_delivery_slot(
        slot_id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
    )
    return jsonify(success_envelope(slot))


## TOGGLE ACTIVE (Delivery Slot)
@blueprint.patch("/delivery-slots/<int:slot_id>/toggle")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_delivery_slot(slot_id: int):
    active = toggle_flag(request.args)
    slot = DeliverySlotService.toggle_delivery_slot(slot_id, active)
    return jsonify(success_envelope(slot))


## READ (Inventory)
@blueprint.get("/inventory")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_inventory():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    branch_id = optional_int(request.args, "branchId")
    product_id = optional_int(request.args, "productId")
    payload = InventoryService.list_inventory(branch_id, product_id, limit, offset)
    return jsonify(success_envelope(payload))


## UPDATE (Inventory)
@blueprint.patch("/inventory/<int:inventory_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_inventory(inventory_id: int):
    payload = InventoryUpdateRequest.model_validate(request.get_json())
    inventory = InventoryService.update_inventory(inventory_id, payload)
    return jsonify(success_envelope(inventory))


## CREATE (Inventory)
@blueprint.post("/inventory")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def create_inventory():
    payload = InventoryCreateRequest.model_validate(request.get_json())
    inventory = InventoryService.create_inventory(payload)
    return jsonify(success_envelope(inventory)), 201

# Endpoint: GET /admin/delivery-slots
## READ (Delivery Slots)
@blueprint.get("/delivery-slots")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_delivery_slots():
    slots = DeliverySlotService.list_delivery_slots()
    return jsonify(success_envelope(slots))

# Endpoint: POST /admin/inventory/bulk (CSV upload)
## CREATE (Bulk Inventory Upload)
@blueprint.post("/inventory/bulk")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def bulk_inventory_upload():
    return handle_bulk_inventory_upload()
