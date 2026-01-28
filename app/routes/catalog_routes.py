"""Catalog endpoints (public)."""

from __future__ import annotations

# PUBLIC: All endpoints in this file are intentionally unauthenticated for catalog browsing.
from flask import Blueprint, jsonify, request

from app.services.catalog import CatalogQueryService
from app.utils.request_params import optional_int, safe_int
from app.utils.responses import success_envelope 
from app.schemas.query_params import ProductSearchQuery


blueprint = Blueprint("catalog", __name__)


## READ (List Categories)
@blueprint.get("/categories")
def list_categories():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    categories, total = CatalogQueryService.list_categories(limit, offset)
    return jsonify(success_envelope(categories, {"total": total, "limit": limit, "offset": offset}))


## READ (Category Products)
@blueprint.get("/categories/<int:category_id>/products")
def category_products(category_id):
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    branch_id = optional_int(request.args, "branchId")
    products, total = CatalogQueryService.get_category_products(category_id, branch_id, limit, offset)
    return jsonify(success_envelope(products, {"total": total, "limit": limit, "offset": offset}))


## READ (Get Product)
@blueprint.get("/products/<int:product_id>")
def get_product(product_id):
    branch_id = optional_int(request.args, "branchId")
    product = CatalogQueryService.get_product(product_id, branch_id)
    return jsonify(success_envelope(product))


## READ (Search Products)
@blueprint.get("/products/search")
def search_products():
    params = ProductSearchQuery(**request.args)
    products, total = CatalogQueryService.search_products(
        params.q, None, None, None, params.limit, params.offset, params.min_price, params.max_price, None, params.sort
    )
    has_next = total > (params.offset + params.limit)
    meta = {"total": total, "limit": params.limit, "offset": params.offset, "has_next": has_next}
    return jsonify(success_envelope(products, meta))
    
## READ (Featured Products)
@blueprint.get("/products/featured")
def featured_products():
    limit = safe_int(request.args, "limit", 10)
    branch_id = optional_int(request.args, "branchId")
    products = CatalogQueryService.featured_products(limit, branch_id)
    return jsonify(success_envelope(products))


## READ (Autocomplete Products)
@blueprint.get("/products/autocomplete")
def autocomplete():
    query = request.args.get("q")
    limit = safe_int(request.args, "limit", 10)
    payload = CatalogQueryService.autocomplete(query, limit)
    return jsonify(success_envelope(payload))


## READ (Product Reviews)
@blueprint.get("/products/<int:product_id>/reviews")
def product_reviews(product_id):
    """Return an empty list until the review feed is available."""
    return jsonify(success_envelope({"items": []}))
