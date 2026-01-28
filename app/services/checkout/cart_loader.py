from __future__ import annotations
from sqlalchemy import select
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Cart


class CheckoutCartLoader:
    @staticmethod
    def load(cart_id: int, for_update: bool = False) -> Cart:
        stmt = select(Cart).where(Cart.id == cart_id)
        if for_update:
            stmt = stmt.with_for_update()
        cart = db.session.execute(stmt).scalar_one_or_none()
        if not cart:
            raise DomainError("NOT_FOUND", "Cart not found", status_code=404)
        _ = cart.items
        for item in cart.items:
            _ = item.product
        return cart
