from __future__ import annotations
from decimal import Decimal
from pydantic import Field

from .common import DefaultModel

class CartItemUpsertRequest(DefaultModel):
    product_id: int
    quantity: int = Field(gt=0)

class CartItemResponse(DefaultModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

class CartResponse(DefaultModel):
    id: int
    user_id: int
    total_amount: Decimal
    items: list[CartItemResponse]
