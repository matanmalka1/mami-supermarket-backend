"""Admin-only catalog management endpoints."""

from __future__ import annotations

from uuid import UUID

from flask import Blueprint, jsonify, request

from ..middleware.auth import require_role
from ..models.enums import Role
from ..schemas.branches import (
    BranchAdminRequest,
    DeliverySlotAdminRequest,
    InventoryUpdateRequest,
)
from ..schemas.catalog import (
    CategoryAdminRequest,
    ProductAdminRequest,
    ProductUpdateRequest,
)
from ..services.branches import BranchService, InventoryService
from ..services.catalog import CatalogService
from ..utils.responses import success_envelope

blueprint = Blueprint("admin", __name__)


def _toggle_flag() -> bool:
    active = request.args.get("active")
    return active != "false"


def _safe_int(name: str, default: int) -> int:
    try:
        return int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default


def _optional_uuid(name: str) -> UUID | None:
    value = request.args.get(name)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


@blueprint.post("/categories")
@require_role(Role.MANAGER, Role.ADMIN)
def create_category():
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogService.create_category(payload.name, payload.description)
    return jsonify(success_envelope(category)), 201


@blueprint.patch("/categories/<uuid:category_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_category(category_id: UUID):
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogService.update_category(category_id, payload.name, payload.description)
    return jsonify(success_envelope(category))


@blueprint.patch("/categories/<uuid:category_id>/toggle")
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_category(category_id: UUID):
    active = _toggle_flag()
    category = CatalogService.toggle_category(category_id, active)
    return jsonify(success_envelope(category))


@blueprint.post("/products")
@require_role(Role.MANAGER, Role.ADMIN)
def create_product():
    payload = ProductAdminRequest.model_validate(request.get_json())
    product = CatalogService.create_product(
        payload.name,
        payload.sku,
        str(payload.price),
        payload.category_id,
        payload.description,
    )
    return jsonify(success_envelope(product)), 201


@blueprint.patch("/products/<uuid:product_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_product(product_id: UUID):
    payload = ProductUpdateRequest.model_validate(request.get_json())
    product = CatalogService.update_product(
        product_id,
        name=payload.name,
        sku=payload.sku,
        price=str(payload.price) if payload.price is not None else None,
        category_id=payload.category_id,
        description=payload.description,
    )
    return jsonify(success_envelope(product))


@blueprint.patch("/products/<uuid:product_id>/toggle")
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_product(product_id: UUID):
    active = _toggle_flag()
    product = CatalogService.toggle_product(product_id, active)
    return jsonify(success_envelope(product))


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
    active = _toggle_flag()
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
    active = _toggle_flag()
    slot = BranchService.toggle_delivery_slot(slot_id, active)
    return jsonify(success_envelope(slot))


@blueprint.get("/inventory")
@require_role(Role.MANAGER, Role.ADMIN)
def list_inventory():
    limit = _safe_int("limit", 50)
    offset = _safe_int("offset", 0)
    branch_id = _optional_uuid("branchId")
    product_id = _optional_uuid("productId")
    payload = InventoryService.list_inventory(branch_id, product_id, limit, offset)
    return jsonify(success_envelope(payload))


@blueprint.put("/inventory/<uuid:inventory_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_inventory(inventory_id: UUID):
    payload = InventoryUpdateRequest.model_validate(request.get_json())
    inventory = InventoryService.update_inventory(inventory_id, payload)
    return jsonify(success_envelope(inventory))
