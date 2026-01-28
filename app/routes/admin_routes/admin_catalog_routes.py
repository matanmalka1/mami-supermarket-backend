from __future__ import annotations
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.models.enums import Role
from app.schemas.catalog import CategoryAdminRequest, ProductAdminRequest, ProductUpdateRequest
from app.services.catalog import CatalogAdminService
from app.utils.request_params import toggle_flag
from app.utils.responses import success_envelope 
from app.schemas.admin_branches_query import ToggleCategoryQuery

blueprint = Blueprint("admin_catalog", __name__)

## CREATE (Category)
@blueprint.post("/categories")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def create_category():
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogAdminService.create_category(payload.name, payload.description)
    return jsonify(success_envelope(category)), 201

## UPDATE (Category)
@blueprint.patch("/categories/<int:category_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_category(category_id: int):
    payload = CategoryAdminRequest.model_validate(request.get_json())
    category = CatalogAdminService.update_category(category_id, payload.name, payload.description)
    return jsonify(success_envelope(category))

## TOGGLE ACTIVE (Category)
@blueprint.patch("/categories/<int:category_id>/toggle")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_category(category_id: int):
    params = ToggleCategoryQuery(**request.args)
    category = CatalogAdminService.toggle_category(category_id, params.active)
    return jsonify(success_envelope(category))

## CREATE (Product)
@blueprint.post("/products")
@jwt_required()
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

## UPDATE (Product)
@blueprint.patch("/products/<int:product_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_product(product_id: int):
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

## TOGGLE ACTIVE (Product)
@blueprint.patch("/products/<int:product_id>/toggle")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_product(product_id: int):
    active = toggle_flag(request.args)
    product = CatalogAdminService.toggle_product(product_id, active)
    return jsonify(success_envelope(product))
