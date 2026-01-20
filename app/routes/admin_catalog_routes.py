from __future__ import annotations
from uuid import UUID
from flask import Blueprint, jsonify, request
from app.middleware.auth import require_role
from app.models.enums import Role
from app.schemas.catalog import CategoryAdminRequest, ProductAdminRequest, ProductUpdateRequest
from app.services.catalog_service import CatalogAdminService
from app.utils.request_params import toggle_flag
from app.utils.responses import success_envelope

blueprint = Blueprint("admin_catalog", __name__)

@blueprint.post("/categories")
@require_role(Role.MANAGER, Role.ADMIN)
def create_category():
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogAdminService.create_category(payload.name, payload.description)
    return jsonify(success_envelope(category)), 201

@blueprint.patch("/categories/<uuid:category_id>")
@require_role(Role.MANAGER, Role.ADMIN)
def update_category(category_id: UUID):
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogAdminService.update_category(category_id, payload.name, payload.description)
    return jsonify(success_envelope(category))

@blueprint.patch("/categories/<uuid:category_id>/toggle")
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_category(category_id: UUID):
    active = toggle_flag(request.args)
    category = CatalogAdminService.toggle_category(category_id, active)
    return jsonify(success_envelope(category))

@blueprint.post("/products")
@require_role(Role.MANAGER, Role.ADMIN)
def create_product():
    payload = ProductAdminRequest.model_validate(request.get_json())
    product = CatalogAdminService.create_product(
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
    product = CatalogAdminService.update_product(
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
    active = toggle_flag(request.args)
    product = CatalogAdminService.toggle_product(product_id, active)
    return jsonify(success_envelope(product))
