from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from .common import DefaultModel, Pagination

class CategoryResponse(DefaultModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool = True

class ProductResponse(DefaultModel):
    id: UUID
    name: str
    sku: str
    price: Decimal
    description: str | None
    category_id: UUID
    is_active: bool
    in_stock_anywhere: bool
    in_stock_for_branch: bool | None = None

class ProductSearchResponse(DefaultModel):
    items: list[ProductResponse]
    pagination: Pagination

class AutocompleteItem(DefaultModel):
    id: UUID
    name: str

class AutocompleteResponse(Pagination):
    items: list[AutocompleteItem]

class CategoryAdminRequest(DefaultModel):
    name: str
    description: str | None = None

class ProductAdminRequest(DefaultModel):
    name: str
    sku: str
    price: Decimal
    category_id: UUID
    description: str | None = None

class ProductUpdateRequest(DefaultModel):
    name: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    category_id: UUID | None = None
    description: str | None = None
