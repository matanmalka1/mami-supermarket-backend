from __future__ import annotations
from decimal import Decimal

from .common import DefaultModel, Pagination

class CategoryResponse(DefaultModel):
    id: int
    name: str
    icon_slug: str | None = None
    description: str | None
    is_active: bool = True

class ProductResponse(DefaultModel):
    id: int
    name: str
    sku: str
    price: Decimal
    old_price: Decimal | None = None
    unit: str | None = None
    nutritional_info: dict | None = None
    is_organic: bool = False
    bin_location: str | None = None
    image_url: str | None = None
    description: str | None
    category_id: int
    is_active: bool
    in_stock_anywhere: bool
    in_stock_for_branch: bool | None = None

# For featured endpoint
class FeaturedProductsResponse(DefaultModel):
    items: list[ProductResponse]
    
class ProductSearchResponse(DefaultModel):
    items: list[ProductResponse]
    pagination: Pagination

class AutocompleteItem(DefaultModel):
    id: int
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
    category_id: int
    description: str | None = None

class ProductUpdateRequest(DefaultModel):
    name: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    category_id: int | None = None
    description: str | None = None
