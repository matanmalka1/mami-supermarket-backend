from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from pydantic import Field
from .common import DefaultModel

class CartItemUpsertRequest(DefaultModel):
    product_id: UUID
    quantity: int = Field(gt=0)

class CartItemResponse(DefaultModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal

class CartResponse(DefaultModel):
    id: UUID
    user_id: UUID
    total_amount: Decimal
    items: list[CartItemResponse]
