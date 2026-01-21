import uuid
from decimal import Decimal
import pytest
import sqlalchemy as sa
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Audit, Cart, CartItem, DeliverySlot
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


def _cart_payload(cart, *, fulfillment, branch_id, slot_id=None, addr=None, key="k1"):
    return CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=fulfillment,
        branch_id=branch_id,
        delivery_slot_id=slot_id,
        address=addr,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
        idempotency_key=key,
    )


def _prep_cart(session, users, product_with_inventory, qty=1, price="10.00"):
    user = users[0]
    product, inv, branch = product_with_inventory
    inv.available_quantity = max(inv.available_quantity, qty)
    session.add(inv)
    session.commit()
    cart = _build_cart(session, user.id, product.id, qty=qty, price=Decimal(price))
    return user, product, inv, branch, cart
def test_checkout_insufficient_stock(session, test_app, users, product_with_inventory):
    user, product, _, branch, cart = _prep_cart(session, users, product_with_inventory, qty=2)
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(
            _cart_payload(cart, fulfillment=FulfillmentType.PICKUP, branch_id=branch.id)
        )
    assert exc.value.code == "INSUFFICIENT_STOCK"

def test_checkout_preview_branch_switch_missing(session, users, product_with_inventory):
    user, product, _, other_branch, cart = _prep_cart(session, users, product_with_inventory)
    payload = CheckoutPreviewRequest(
        cart_id=cart.id,
        fulfillment_type=FulfillmentType.PICKUP,
        branch_id=other_branch.id,
    )
    preview = CheckoutService.preview(payload)
    assert preview.missing_items, "Expected missing items when branch has no stock"

def test_payment_danger_zone_logged(session, test_app, users, product_with_inventory, monkeypatch):
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory, qty=1)
    inv.available_quantity = 5
    session.add(inv)
    session.commit()

    payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.PICKUP,
        branch_id=inv.branch_id,
        key="danger",
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

def test_checkout_delivery_fee_under_min(session, test_app, users, product_with_inventory):
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    with test_app.app_context():
        test_app.config["DELIVERY_MIN_TOTAL"] = 150
        test_app.config["DELIVERY_FEE_UNDER_MIN"] = 30
    preview = CheckoutService.preview(
        CheckoutPreviewRequest(
            cart_id=cart.id,
            fulfillment_type=FulfillmentType.DELIVERY,
            branch_id=None,
            delivery_slot_id=None,
            address="Somewhere 1",
        )
    )
    assert preview.delivery_fee == Decimal("30")

def test_checkout_idempotency_reuse(session, users, product_with_inventory, monkeypatch):
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    slot = session.query(DeliverySlot).first()
    monkeypatch.setattr(PaymentService, "charge", lambda *_a, **_k: "ref-idem")
    payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Addr",
        key="same-key",
    )
    first = CheckoutService.confirm(payload)
    second = CheckoutService.confirm(payload)
    assert second.order_id == first.order_id
    assert second.payment_reference == "ref-idem"

def test_checkout_idempotency_conflict(session, users, product_with_inventory, monkeypatch):
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    slot = session.query(DeliverySlot).first()
    monkeypatch.setattr(PaymentService, "charge", lambda *_a, **_k: "ref-conflict")
    base_payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Addr",
        key="idem-conflict",
    )
    CheckoutService.confirm(base_payload)
    mutated = base_payload.model_copy(update={"payment_token_id": uuid.uuid4()})
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(mutated)
    assert exc.value.code == "IDEMPOTENCY_CONFLICT"

def test_checkout_saves_payment_preferences(session, test_app, users):
    user, _ = users
    CheckoutService._maybe_save_default_payment_token(user.id, uuid.uuid4(), save_as_default=True)
    db.session.commit()
    audit_rows = db.session.execute(
        sa.select(Audit).where(Audit.entity_type == "payment_preferences")
    ).scalars().all()
    assert audit_rows
