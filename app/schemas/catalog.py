from __future__ import annotations
from decimal import Decimal

from .common import DefaultModel, Pagination
from pydantic import Field

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
    available_quantity: int = Field(ge=0, default=0)
    branch_available_quantity: int | None = Field(default=None, ge=0)

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
    name: str = Field(min_length=2, max_length=50, pattern=r"^[\w\s\-א-ת]+$")
    description: str | None = Field(default=None, min_length=0, max_length=300)

class ProductAdminRequest(DefaultModel):
    name: str = Field(min_length=2, max_length=100, pattern=r"^[\w\s\-א-ת]+$")
    sku: str = Field(min_length=2, max_length=20, pattern=r"^[A-Za-z0-9\-]+$")
    price: Decimal = Field(gt=0, le=10000)
    category_id: int = Field(gt=0)
    description: str | None = Field(default=None, min_length=0, max_length=500)

class ProductUpdateRequest(DefaultModel):
    name: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[\w\s\-א-ת]+$")
    sku: str | None = Field(default=None, min_length=2, max_length=20, pattern=r"^[A-Za-z0-9\-]+$")
    price: Decimal | None = Field(default=None, gt=0, le=10000)
    category_id: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, min_length=0, max_length=500)
