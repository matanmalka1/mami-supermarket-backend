import uuid
from decimal import Decimal

import pytest
import sqlalchemy as sa

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Audit, Cart, CartItem
from app.models.enums import FulfillmentType
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutPreviewRequest
from app.services.checkout_service import CheckoutService
from app.services.payment_service import PaymentService


def _build_cart(session, user_id, product_id, qty, price):
    cart = Cart(user_id=user_id)
    session.add(cart)
    session.flush()
    item = CartItem(
        cart_id=cart.id,
        product_id=product_id,
        quantity=qty,
        unit_price=price,
    )
    session.add(item)
    session.commit()
    return cart


def test_checkout_insufficient_stock(session, test_app, users, product_with_inventory):
    user, _ = users
    product, _, branch = product_with_inventory
    cart = _build_cart(session, user.id, product.id, qty=2, price=Decimal("10.00"))
    payload = CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=branch.id,
        delivery_slot_id=None,
        address=None,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
        idempotency_key="k1",
    )
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(payload)
    assert exc.value.code == "INSUFFICIENT_STOCK"


def test_checkout_preview_branch_switch_missing(session, users, product_with_inventory):
    user, _ = users
    product, _, other_branch = product_with_inventory
    cart = _build_cart(session, user.id, product.id, qty=1, price=Decimal("10.00"))
    payload = CheckoutPreviewRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=other_branch.id,
    )
    preview = CheckoutService.preview(payload)
    assert preview.missing_items, "Expected missing items when branch has no stock"


def test_payment_danger_zone_logged(session, test_app, users, product_with_inventory, monkeypatch):
    user, _ = users
    product, inv, _ = product_with_inventory
    # replenish inventory for this test
    inv.available_quantity = 5
    session.add(inv)
    session.commit()
    cart = _build_cart(session, user.id, product.id, qty=1, price=Decimal("10.00"))
    payload = CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=inv.branch_id,
        delivery_slot_id=None,
        address=None,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
        idempotency_key="danger",
    )

    def _fail_store(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(PaymentService, "charge", lambda *_args, **_kw: "ref123")
    monkeypatch.setattr(CheckoutService, "_store_idempotency", _fail_store)

    with pytest.raises(RuntimeError):
        CheckoutService.confirm(payload)
    audit_rows = db.session.execute(
        sa.select(Audit).where(Audit.action == "PAYMENT_CAPTURED_NOT_COMMITTED")
    ).scalars().all()
    assert audit_rows, "Expected danger zone audit log when commit fails after payment"
