"""Simple seeding helpers for the initial data."""

from __future__ import annotations

from datetime import datetime, timedelta
import os
import sys
from datetime import time
from pathlib import Path
from uuid import UUID

# Local imports after sys.path tweak for script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import AppConfig  # noqa: E402
from app.models import (  # noqa: E402
    Base,
    Branch,
    DeliverySlot,
    Inventory,
    Order,
    OrderDeliveryDetails,
    OrderItem,
    Cart,
    CartItem,
    CartStatus,
    FulfillmentType,
    OrderStatus,
    Role,
    User,
    Category,
    Product,
    Address,
)



def seed_warehouse_branch(session: Session) -> Branch:
    config = AppConfig()
    configured_id = config.DELIVERY_SOURCE_BRANCH_ID
    branch = None
    if configured_id:
        try:
            branch_uuid = UUID(str(configured_id))
            branch = session.get(Branch, branch_uuid)
        except ValueError:
            print("Invalid DELIVERY_SOURCE_BRANCH_ID in config; using name lookup.")
    if not branch:
        branch = session.query(Branch).filter_by(name="The Warehouse").first()
    if branch:
        print(f"Warehouse branch already exists: {branch.id}")
        return branch

    branch = Branch(
        id=branch_uuid if configured_id else None,
        name="The Warehouse",
        address="Central warehouse, main street",
    )
    session.add(branch)
    session.flush()
    print(f"Created warehouse branch with id={branch.id}")
    return branch


def seed_additional_branch(session: Session, name: str, address: str) -> Branch:
    branch = session.query(Branch).filter_by(name=name).first()
    if branch:
        return branch
    branch = Branch(name=name, address=address)
    session.add(branch)
    session.flush()
    print(f"Created branch '{name}' with id={branch.id}")
    return branch


def seed_delivery_slots(session: Session, branch: Branch) -> None:
    window_start = 6
    window_end = 22
    slot_duration = 2
    existing = {
        (slot.day_of_week, slot.start_time, slot.end_time)
        for slot in session.query(DeliverySlot).filter_by(branch_id=branch.id)
    }

    for day in range(7):
        for start in range(window_start, window_end, slot_duration):
            slot_start = time(hour=start, minute=0)
            slot_end = time(hour=min(start + slot_duration, window_end), minute=0)
            key = (day, slot_start, slot_end)
            if key in existing:
                continue
            session.add(
                DeliverySlot(
                    branch_id=branch.id,
                    day_of_week=day,
                    start_time=slot_start,
                    end_time=slot_end,
                )
            )


pwd_context = CryptContext(
    # Stick to bcrypt with 2b ident to dodge broken __about__ in some bcrypt builds
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2b",
)


def seed_admin_user(session: Session) -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@mami.local")
    password = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
    full_name = os.environ.get("ADMIN_FULL_NAME", "Super Admin")

    existing = session.query(User).filter_by(email=email).first()
    if existing:
        return

    user = User(
        email=email,
        full_name=full_name,
        password_hash=pwd_context.hash(password),
        role=Role.ADMIN,
    )
    session.add(user)


def seed_sample_users(session: Session, default_branch_id) -> None:
    samples = [
        ("customer@mami.local", "Customer One", "Customer123!", Role.CUSTOMER),
        ("employee@mami.local", "Employee One", "Employee123!", Role.EMPLOYEE),
        ("manager@mami.local", "Manager One", "Manager123!", Role.MANAGER),
    ]
    for email, full_name, password, role in samples:
        if session.query(User).filter_by(email=email).first():
            continue
        session.add(
            User(
                email=email,
                full_name=full_name,
                password_hash=pwd_context.hash(password),
                role=role,
                default_branch_id=default_branch_id,
            )
        )


def seed_addresses(session: Session) -> None:
    users = session.query(User).all()
    if not users:
        return
    existing = session.query(Address).count()
    target = 30
    if existing >= target:
        return
    for idx in range(existing + 1, target + 1):
        user = users[(idx - 1) % len(users)]
        session.add(
            Address(
                user_id=user.id,
                address_line=f"{idx} Main Street",
                city="Tel Aviv",
                country="Israel",
                postal_code=f"60{100 + idx:03d}",
            )
        )


def seed_categories_and_products(session: Session) -> list[Product]:
    catalog = {
        "Dairy": [
            ("Whole Milk 1L", "MILK-1L", 5.90, "Fresh whole milk"),
            ("Greek Yogurt", "YOG-GREEK", 7.50, "Thick Greek yogurt"),
        ],
        "Bakery": [
            ("Sourdough Bread", "BREAD-SOUR", 12.00, "Crusty sourdough loaf"),
            ("Butter Croissant", "CROISS-BUT", 6.50, "Buttery flaky croissant"),
        ],
        "Produce": [
            ("Bananas", "BAN-1KG", 4.20, "Fresh bananas (1kg)"),
            ("Cherry Tomatoes", "TOM-CHERRY", 8.30, "Sweet cherry tomatoes"),
        ],
    }
    products: list[Product] = []
    for cat_name, items in catalog.items():
        category = session.query(Category).filter_by(name=cat_name).first()
        if not category:
            category = Category(name=cat_name, description=f"{cat_name} items")
            session.add(category)
            session.flush()
        for name, sku, price, desc in items:
            product = session.query(Product).filter_by(sku=sku).first()
            if product:
                products.append(product)
                continue
            product = Product(
                name=name,
                sku=sku,
                category_id=category.id,
                price=price,
                description=desc,
            )
            session.add(product)
            products.append(product)
    session.flush()
    return products


def seed_inventory(session: Session, branch: Branch, products: list[Product]) -> None:
    for idx, product in enumerate(products, start=1):
        exists = (
            session.query(Inventory)
            .filter_by(product_id=product.id, branch_id=branch.id)
            .first()
        )
        if exists:
            continue
        session.add(
            Inventory(
                product_id=product.id,
                branch_id=branch.id,
                available_quantity=20 + idx * 5,
                reserved_quantity=0,
            )
        )


def seed_carts(session: Session, products: list[Product]) -> None:
    customers = session.query(User).filter_by(role=Role.CUSTOMER).all()
    if not customers:
        return
    if not products:
        return

    for customer in customers:
        cart = session.query(Cart).filter_by(user_id=customer.id).first()
        if not cart:
            cart = Cart(user_id=customer.id, status=CartStatus.ACTIVE)
            session.add(cart)
            session.flush()

        existing_items = {item.product_id for item in cart.items}
        for idx, product in enumerate(products[:3], start=1):
            if product.id in existing_items:
                continue
            session.add(
                CartItem(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=1 + (idx % 2),
                    unit_price=product.price,
                )
            )


def seed_orders(session: Session, branch: Branch, products: list[Product]) -> None:
    customers = session.query(User).filter_by(role=Role.CUSTOMER).all()
    slot = session.query(DeliverySlot).filter_by(branch_id=branch.id).first()
    if not customers or not products or not slot:
        return

    existing = session.query(Order).count()
    target = 5
    if existing >= target:
        return

    today = datetime.utcnow().date()
    for idx in range(existing + 1, target + 1):
        user = customers[(idx - 1) % len(customers)]
        address = session.query(Address).filter_by(user_id=user.id).first()
        address_line = address.address_line if address else f"{idx} Sample Street"

        items = []
        for product in products[:2]:
            quantity = 1 + (idx % 2)
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "unit_price": product.price,
                }
            )

        total_amount = sum(item["unit_price"] * item["quantity"] for item in items)

        order = Order(
            order_number=f"ORD-{idx:04d}",
            user_id=user.id,
            total_amount=total_amount,
            fulfillment_type=FulfillmentType.DELIVERY,
            status=OrderStatus.CREATED,
            branch_id=branch.id,
        )
        session.add(order)
        session.flush()

        for item in items:
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product"].id,
                    name=item["product"].name,
                    sku=item["product"].sku,
                    unit_price=item["unit_price"],
                    quantity=item["quantity"],
                )
            )

        slot_date = today + timedelta(days=idx)
        slot_start = datetime.combine(slot_date, slot.start_time)
        slot_end = datetime.combine(slot_date, slot.end_time)
        session.add(
            OrderDeliveryDetails(
                order_id=order.id,
                delivery_slot_id=slot.id,
                address=address_line,
                slot_start=slot_start,
                slot_end=slot_end,
            )
        )


def main() -> None:
    config = AppConfig()
    engine = create_engine(config.DATABASE_URL)

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            branch = seed_warehouse_branch(session)
            store_branch = seed_additional_branch(session, "Downtown Branch", "Downtown street 5")
            seed_delivery_slots(session, branch)
            seed_admin_user(session)
            products = seed_categories_and_products(session)
            seed_inventory(session, branch, products)
            seed_inventory(session, store_branch, products)
            seed_sample_users(session, branch.id)
            seed_addresses(session)
            seed_carts(session, products)
            seed_orders(session, branch, products)
            session.commit()
    except IntegrityError:
        print("Seed already applied or constraint violated")


if __name__ == "__main__":
    main()
