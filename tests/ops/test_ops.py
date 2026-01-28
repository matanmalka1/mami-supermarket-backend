from decimal import Decimal

import pytest

from app.middleware.error_handler import DomainError
from app.models import Order, OrderItem
from app.models.enums import FulfillmentType, OrderStatus, PickedStatus, Role
from app.services.ops import OpsOrderUpdateService


def test_employee_invalid_status_transition(session, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user.id,
        order_number="ORD2",
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
        OpsOrderUpdateService.update_order_status(order.id, OrderStatus.READY.value, user.id, Role.EMPLOYEE)
    assert exc.value.code == "INVALID_STATUS_TRANSITION"


def test_missing_items_flow_sets_missing(session, users, product_with_inventory):
    user, _ = users
    product, _, _ = product_with_inventory
    order = Order(
        user_id=user.id,
        order_number="ORD3",
        total_amount=Decimal("10.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.IN_PROGRESS,
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
            picked_status=PickedStatus.MISSING,
        )
    )
    session.commit()
    updated = OpsOrderUpdateService.update_order_status(order.id, OrderStatus.MISSING.value, user.id, Role.EMPLOYEE)
    assert updated.status == OrderStatus.MISSING
