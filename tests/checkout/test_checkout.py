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


def _cart_payload(cart, *, fulfillment, branch_id, slot_id=None, addr=None):
    """Create checkout confirm request (without idempotency_key in body)."""
    return CheckoutConfirmRequest(
        cart_id=cart.id,
        fulfillment_type=fulfillment,
        branch_id=branch_id,
        delivery_slot_id=slot_id,
        address=addr,
        payment_token_id=uuid.uuid4(),
        save_as_default=False,
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
            _cart_payload(cart, fulfillment=FulfillmentType.PICKUP, branch_id=branch.id),
            idempotency_key="test-key-1"
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
    )

    def _fail_commit(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(PaymentService, "charge", lambda *_args, **_kw: "ref123")
    monkeypatch.setattr(db.session, "commit", _fail_commit)

    with pytest.raises(RuntimeError):
        CheckoutService.confirm(payload, idempotency_key="danger-key")
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
    """Test that same idempotency key returns same response."""
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    slot = session.query(DeliverySlot).first()
    monkeypatch.setattr(PaymentService, "charge", lambda *_a, **_k: "ref-idem")
    payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Addr",
    )
    first = CheckoutService.confirm(payload, idempotency_key="same-key")
    second = CheckoutService.confirm(payload, idempotency_key="same-key")
    assert second.order_id == first.order_id
    assert second.payment_reference == "ref-idem"

def test_checkout_idempotency_key_reuse_mismatch(session, users, product_with_inventory, monkeypatch):
    """Test that same key with different payload raises IDEMPOTENCY_KEY_REUSE_MISMATCH."""
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    slot = session.query(DeliverySlot).first()
    monkeypatch.setattr(PaymentService, "charge", lambda *_a, **_k: "ref-conflict")
    base_payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Addr",
    )
    CheckoutService.confirm(base_payload, idempotency_key="idem-conflict")
    
    # Create new cart with different content
    cart2 = _build_cart(session, user.id, product.id, qty=3, price=Decimal("20.00"))
    mutated = _cart_payload(
        cart2,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Different Address",
    )
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(mutated, idempotency_key="idem-conflict")
    assert exc.value.code == "IDEMPOTENCY_KEY_REUSE_MISMATCH"

def test_checkout_idempotency_in_progress(session, users, product_with_inventory, monkeypatch):
    """Test that concurrent requests with same key get IDEMPOTENCY_IN_PROGRESS."""
    from app.models import IdempotencyKey
    from app.models.enums import IdempotencyStatus
    
    user, product, inv, _, cart = _prep_cart(session, users, product_with_inventory)
    slot = session.query(DeliverySlot).first()
    
    # Manually create IN_PROGRESS record
    idem_key = IdempotencyKey(
        user_id=user.id,
        key="in-progress-key",
        request_hash="somehash",
        status=IdempotencyStatus.IN_PROGRESS,
    )
    session.add(idem_key)
    session.commit()
    
    payload = _cart_payload(
        cart,
        fulfillment=FulfillmentType.DELIVERY,
        branch_id=None,
        slot_id=slot.id,
        addr="Addr",
    )
    
    with pytest.raises(DomainError) as exc:
        CheckoutService.confirm(payload, idempotency_key="in-progress-key")
    assert exc.value.code == "IDEMPOTENCY_IN_PROGRESS"

def test_checkout_saves_payment_preferences(session, test_app, users):
    user, _ = users
    CheckoutService._maybe_save_default_payment_token(user.id, uuid.uuid4(), save_as_default=True)
    db.session.commit()
    audit_rows = db.session.execute(
        sa.select(Audit).where(Audit.entity_type == "payment_preferences")
    ).scalars().all()
    assert audit_rows
