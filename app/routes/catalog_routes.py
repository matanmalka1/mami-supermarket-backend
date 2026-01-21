"""Catalog endpoints (public)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.catalog_service import CatalogQueryService
from app.utils.request_params import optional_uuid, safe_bool, safe_int
from app.utils.responses import success_envelope

blueprint = Blueprint("catalog", __name__)


@blueprint.get("/categories")
def list_categories():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    categories, total = CatalogQueryService.list_categories(limit, offset)
    return jsonify(success_envelope(categories, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/categories/<uuid:category_id>/products")
def category_products(category_id):
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    branch_id = optional_uuid(request.args, "branchId")
    products, total = CatalogQueryService.get_category_products(category_id, branch_id, limit, offset)
    return jsonify(success_envelope(products, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/products/<uuid:product_id>")
def get_product(product_id):
    branch_id = optional_uuid(request.args, "branchId")
    product = CatalogQueryService.get_product(product_id, branch_id)
    return jsonify(success_envelope(product))


@blueprint.get("/products/search")
def search_products():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    query = request.args.get("q")
    category_id = optional_uuid(request.args, "categoryId")
    branch_id = optional_uuid(request.args, "branchId")
    in_stock = safe_bool(request.args.get("inStock"))
    products, total = CatalogQueryService.search_products(
        query, category_id, in_stock, branch_id, limit, offset
    )
    return jsonify(success_envelope(products, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/products/autocomplete")
def autocomplete():
    query = request.args.get("q")
    limit = safe_int(request.args, "limit", 10)
    payload = CatalogQueryService.autocomplete(query, limit)
    return jsonify(success_envelope(payload))
