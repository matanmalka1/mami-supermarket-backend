from __future__ import annotations
from typing import Sequence
from uuid import UUID
import sqlalchemy as sa
from app.extensions import db
from app.models import Category, Inventory, Product
from app.schemas.catalog import CategoryResponse, ProductResponse


def to_category_response(category: Category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        is_active=category.is_active,
    )


def load_inventory(product: Product) -> None:
    if not product.inventory:
        product.inventory = (
            db.session.execute(sa.select(Inventory).where(Inventory.product_id == product.id)).scalars().all()
        )


def matches_stock(product: Product, branch_id: UUID | None, desired: bool) -> bool:
    load_inventory(product)
    if branch_id:
        row = next((i for i in product.inventory if i.branch_id == branch_id), None)
        quantity = row.available_quantity if row else 0
    else:
        quantity = sum(i.available_quantity for i in product.inventory)
    return (quantity > 0) == desired


def to_product_response(product: Product, branch_id: UUID | None) -> ProductResponse:
    load_inventory(product)
    branch_available: bool | None = None
    if branch_id:
        row = next((i for i in product.inventory if i.branch_id == branch_id), None)
        branch_available = bool(row and row.available_quantity > 0)
    return ProductResponse(
        id=product.id,
        name=product.name,
        sku=product.sku,
        price=product.price,
        description=product.description,
        category_id=product.category_id,
        is_active=product.is_active,
        in_stock_anywhere=any(i.available_quantity > 0 for i in product.inventory),
        in_stock_for_branch=branch_available,
    )


def map_products(items: Sequence[Product], branch_id: UUID | None) -> list[ProductResponse]:
    return [to_product_response(item, branch_id) for item in items]
