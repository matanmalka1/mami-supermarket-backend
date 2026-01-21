from __future__ import annotations
from uuid import UUID
from flask import Blueprint, jsonify, request
from app.middleware.auth import require_role
from app.models.enums import Role
from app.schemas.branches import BranchAdminRequest, DeliverySlotAdminRequest, InventoryUpdateRequest
from app.services.branch_service import BranchService
from app.services.inventory_service import InventoryService
from app.utils.request_params import optional_uuid, safe_int, toggle_flag
from app.utils.responses import success_envelope

blueprint = Blueprint("admin_branches", __name__)

@blueprint.post("/branches")
@require_role(Role.MANAGER, Role.ADMIN)
def create_branch():
    payload = BranchAdminRequest.model_validate(request.get_json())
    branch = BranchService.create_branch(payload.name, payload.address)
    return jsonify(success_envelope(branch)), 201


@blueprint.patch("/branches/<uuid:branch_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_branch(branch_id: UUID):
    payload = BranchAdminRequest.model_validate(request.get_json())
    branch = BranchService.update_branch(branch_id, payload.name, payload.address)
    return jsonify(success_envelope(branch))


@blueprint.patch("/branches/<uuid:branch_id>/toggle")
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_branch(branch_id: UUID):
    active = toggle_flag(request.args)
    branch = BranchService.toggle_branch(branch_id, active)
    return jsonify(success_envelope(branch))


@blueprint.post("/delivery-slots")
@require_role(Role.MANAGER, Role.ADMIN)
def create_delivery_slot():
    payload = DeliverySlotAdminRequest.model_validate(request.get_json())
    slot = BranchService.create_delivery_slot(
        payload.branch_id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
    )
    return jsonify(success_envelope(slot)), 201


@blueprint.patch("/delivery-slots/<uuid:slot_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_delivery_slot(slot_id: UUID):
    payload = DeliverySlotAdminRequest.model_validate(request.get_json())
    slot = BranchService.update_delivery_slot(
        slot_id,
        payload.day_of_week,
        payload.start_time,
        payload.end_time,
    )
    return jsonify(success_envelope(slot))


@blueprint.patch("/delivery-slots/<uuid:slot_id>/toggle")
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_delivery_slot(slot_id: UUID):
    active = toggle_flag(request.args)
    slot = BranchService.toggle_delivery_slot(slot_id, active)
    return jsonify(success_envelope(slot))


@blueprint.get("/inventory")
@require_role(Role.MANAGER, Role.ADMIN)
def list_inventory():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    branch_id = optional_uuid(request.args, "branchId")
    product_id = optional_uuid(request.args, "productId")
    payload = InventoryService.list_inventory(branch_id, product_id, limit, offset)
    return jsonify(success_envelope(payload))


@blueprint.put("/inventory/<uuid:inventory_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_inventory(inventory_id: UUID):
    payload = InventoryUpdateRequest.model_validate(request.get_json())
    inventory = InventoryService.update_inventory(inventory_id, payload)
    return jsonify(success_envelope(inventory))
