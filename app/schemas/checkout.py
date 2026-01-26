from __future__ import annotations
from enum import Enum
from decimal import Decimal
from .common import DefaultModel
from ..models.enums import FulfillmentType

class FulfillmentChoice(str, Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"

class CheckoutPreviewRequest(DefaultModel):
    cart_id: int
    fulfillment_type: FulfillmentType
    branch_id: int | None = None
    delivery_slot_id: int | None = None
    address: str | None = None

class MissingItem(DefaultModel):
    product_id: int
    requested_quantity: int
    available_quantity: int

class CheckoutPreviewResponse(DefaultModel):
    cart_total: Decimal
    delivery_fee: Decimal | None
    missing_items: list[MissingItem]
    fulfillment_type: FulfillmentType

class CheckoutConfirmRequest(DefaultModel):
    cart_id: int
    payment_token_id: int
    fulfillment_type: FulfillmentType | None = None
    branch_id: int | None = None
    delivery_slot_id: int | None = None
    address: str | None = None
    save_as_default: bool = False

class CheckoutConfirmResponse(DefaultModel):
    order_id: int
    order_number: str
    total_paid: Decimal
    payment_reference: str | None = None
