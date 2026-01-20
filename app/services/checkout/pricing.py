from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from flask import current_app
from app.models import Cart
from app.models.enums import FulfillmentType


@dataclass
class CheckoutTotals:
    cart_total: Decimal
    delivery_fee: Decimal | None
    total_amount: Decimal


class CheckoutPricing:
    @staticmethod
    def calculate(cart: Cart, fulfillment_type: FulfillmentType | None) -> CheckoutTotals:
        cart_total = sum(item.unit_price * item.quantity for item in cart.items)
        if fulfillment_type == FulfillmentType.DELIVERY:
            min_total = Decimal(str(current_app.config.get("DELIVERY_MIN_TOTAL", 150)))
            under_min_fee = Decimal(str(current_app.config.get("DELIVERY_FEE_UNDER_MIN", 30)))
            delivery_fee: Decimal | None = Decimal("0") if cart_total >= min_total else under_min_fee
        else:
            delivery_fee = None
        total_amount = cart_total + (delivery_fee or Decimal("0"))
        return CheckoutTotals(cart_total=cart_total, delivery_fee=delivery_fee, total_amount=total_amount)
