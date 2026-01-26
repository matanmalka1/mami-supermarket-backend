from __future__ import annotations

from app.models.enums import (
    Role,
    OrderStatus,
    FulfillmentType,
    CartStatus,
)

DEFAULT_CUSTOMER_ROLE = Role.CUSTOMER
DEFAULT_ORDER_STATUS = OrderStatus.CREATED
DEFAULT_FULFILLMENT = FulfillmentType.DELIVERY
DEFAULT_CART_STATUS = CartStatus.ACTIVE