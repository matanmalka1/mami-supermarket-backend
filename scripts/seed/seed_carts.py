# seed/seed_carts.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem  # TODO: adjust import path
from app.models.user import User
from app.models.product import Product
from app.models.enums import CartStatus


def _get_or_create_active_cart(session: Session, *, user_id) -> Cart:
    cart = session.execute(
        select(Cart).where(
            Cart.user_id == user_id,
            Cart.status == CartStatus.ACTIVE,
        )
    ).scalar_one_or_none()

    if cart:
        return cart

    cart = Cart(user_id=user_id, status=CartStatus.ACTIVE)
    session.add(cart)
    session.flush()  # צריך cart.id לפריטים
    return cart


def _upsert_cart_item(
    session: Session,
    *,
    cart_id,
    product_id,
    quantity: int,
    unit_price: str,
) -> CartItem:
    item = session.execute(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
    ).scalar_one_or_none()

    if item:
        item.quantity = quantity
        item.unit_price = unit_price
        session.add(item)
        return item

    item = CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
    )
    session.add(item)
    return item


def seed_carts(session: Session, *, max_items_per_cart: int = 6) -> list[Cart]:
    """
    Creates an ACTIVE cart for each customer user and adds a few items.
    Uses Product.price as unit_price.
    """
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()

    if not users:
        raise RuntimeError("No users found. Seed users first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")

    rnd = random.Random(123)  # יציב

    created_carts: list[Cart] = []

    # נזרע רק ללקוחות כדי שיהיה ריאליסטי
    from app.models.enums import Role
    customers = [u for u in users if getattr(u, "role", None) == Role.CUSTOMER]

    target_users = customers if customers else users

    for u in target_users:
        cart = _get_or_create_active_cart(session, user_id=u.id)
        created_carts.append(cart)

        # בוחרים 2..max פריטים רנדומלית
        k = rnd.randint(2, max_items_per_cart)
        chosen = rnd.sample(products, k=min(k, len(products)))

        for p in chosen:
            qty = rnd.randint(1, 4)
            _upsert_cart_item(
                session,
                cart_id=cart.id,
                product_id=p.id,
                quantity=qty,
                unit_price=str(p.price),  # Numeric(10,2) safe as string
            )

    session.flush()
    return created_carts