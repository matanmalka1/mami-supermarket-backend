"""Catalog endpoints (public)."""

from __future__ import annotations

from uuid import UUID

from flask import Blueprint, jsonify, request

from app.services.catalog import CatalogService
from app.utils.responses import success_envelope

blueprint = Blueprint("catalog", __name__)


def _safe_int(value: str | None, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    truthy = {"1", "true", "yes"}
    falsy = {"0", "false", "no"}
    lowered = value.lower()
    if lowered in truthy:
        return True
    if lowered in falsy:
        return False
    return None


def _optional_uuid(value: str | None) -> UUID | None:
    if not value:
        return None
    return UUID(value)


@blueprint.get("/categories")
def list_categories():
    limit = _safe_int(request.args.get("limit"), 50)
    offset = _safe_int(request.args.get("offset"), 0)
    categories, total = CatalogService.list_categories(limit, offset)
    return jsonify(success_envelope(categories, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/categories/<uuid:category_id>/products")
def category_products(category_id: UUID):
    limit = _safe_int(request.args.get("limit"), 50)
    offset = _safe_int(request.args.get("offset"), 0)
    branch_id = _optional_uuid(request.args.get("branchId"))
    products, total = CatalogService.get_category_products(category_id, branch_id, limit, offset)
    return jsonify(success_envelope(products, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/products/<uuid:product_id>")
def get_product(product_id: UUID):
    branch_id = _optional_uuid(request.args.get("branchId"))
    product = CatalogService.get_product(product_id, branch_id)
    return jsonify(success_envelope(product))


@blueprint.get("/products/search")
def search_products():
    limit = _safe_int(request.args.get("limit"), 50)
    offset = _safe_int(request.args.get("offset"), 0)
    query = request.args.get("q")
    category_id = _optional_uuid(request.args.get("categoryId"))
    branch_id = _optional_uuid(request.args.get("branchId"))
    in_stock = _safe_bool(request.args.get("inStock"))
    products, total = CatalogService.search_products(
        query, category_id, in_stock, branch_id, limit, offset
    )
    return jsonify(success_envelope(products, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/products/autocomplete")
def autocomplete():
    query = request.args.get("q")
    limit = _safe_int(request.args.get("limit"), 10)
    payload = CatalogService.autocomplete(query, limit)
    return jsonify(success_envelope(payload))
