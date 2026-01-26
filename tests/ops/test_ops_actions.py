"""Smoke tests for the lightweight ops endpoints added in Phase 1."""

from decimal import Decimal

from app.models import Audit, Order, OrderItem
from app.models.enums import FulfillmentType, OrderStatus

def _create_order(session, user, product):
    order = Order(
        user_id=user.id,
        order_number="TEST-OPS",
        total_amount=Decimal("15.00"),
        fulfillment_type=FulfillmentType.PICKUP,
        status=OrderStatus.CREATED,
    )
    session.add(order)
    session.flush()
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        name=product.name,
        sku=product.sku,
        unit_price=Decimal("15.00"),
        quantity=1,
    )
    session.add(item)
    session.commit()
    return order, item

def test_ops_map_returns_branches(client, admin_token):
    response = client.get(
        "/api/v1/ops/map", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert "branches" in payload
    assert isinstance(payload["branches"], list)

def test_ops_sync_and_damage(client, session, users, product_with_inventory, admin_token):
    product, _, _ = product_with_inventory
    order, item = _create_order(session, users[0], product)
    headers = {"Authorization": f"Bearer {admin_token}"}
    sync_resp = client.post(
        f"/api/v1/ops/orders/{order.id}/sync", headers=headers
    )
    assert sync_resp.status_code == 200
    assert sync_resp.get_json()["data"]["synced"] is True
    damage_resp = client.post(
        f"/api/v1/ops/orders/{order.id}/items/{item.id}/report-damage",
        json={"reason": "Damaged", "notes": "Broken seal"},
        headers=headers,
    )
    assert damage_resp.status_code == 201
    assert session.query(Audit).filter_by(action="REPORT_DAMAGE", entity_id=item.id).first()
