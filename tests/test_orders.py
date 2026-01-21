from decimal import Decimal

import pytest

from app.middleware.error_handler import DomainError
from app.models import Order, OrderItem
from app.models.enums import FulfillmentType, OrderStatus
from app.services.order_service import OrderService


def test_order_ownership_returns_404(session, users, product_with_inventory):
    user1, user2 = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user1.id,
        order_number="ORD1",
        total_amount=Decimal("10.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.CREATED,
    )
    session.add(order)
    session.flush()
    session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            name="Milk",
            sku="SKU1",
            unit_price=Decimal("10.00"),
            quantity=1,
        )
    )
    session.commit()
    with pytest.raises(DomainError) as exc:
        OrderService.get_order(order.id, user2.id)
    assert exc.value.code == "NOT_FOUND"
