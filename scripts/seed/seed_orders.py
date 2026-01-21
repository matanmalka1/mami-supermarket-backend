# seed/seed_orders.py
from __future__ import annotations

import random
import datetime as dt
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import (
    Order,
    OrderItem,
    OrderDeliveryDetails,
    OrderPickupDetails,
)
from app.models.user import User
from app.models.address import Address
from app.models.product import Product
from app.models.branch import Branch
from app.models.delivery_slot import DeliverySlot
from app.models.enums import FulfillmentType, OrderStatus, PickedStatus, Role


def _order_number(user_id, seq: int) -> str:
    # מספר הזמנה קצר ויציב (ל-dev). אפשר להחליף ללוגיקה שלך.
    return f"ORD-{str(user_id)[:8].upper()}-{seq:04d}"


def _ensure_order(session: Session, *, order_number: str) -> Order | None:
    return session.execute(
        select(Order).where(Order.order_number == order_number)
    ).scalar_one_or_none()


def seed_orders(session: Session, *, max_orders_per_customer: int = 2) -> list[Order]:
    users = session.execute(select(User)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    branches = session.execute(select(Branch)).scalars().all()
    slots = session.execute(select(DeliverySlot)).scalars().all()

    if not users:
        raise RuntimeError("No users found. Seed users first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")
    if not branches:
        raise RuntimeError("No branches found. Seed branches first.")
    if not slots:
        raise RuntimeError("No delivery slots found. Seed delivery slots first.")

    rnd = random.Random(2026)

    # לקוחות בלבד
    customers = [u for u in users if getattr(u, "role", None) == Role.CUSTOMER]
    target_users = customers if customers else users

    # נביא כתובות מראש
    addresses = session.execute(select(Address)).scalars().all()
    addresses_by_user = {}
    for a in addresses:
        addresses_by_user.setdefault(a.user_id, []).append(a)

    created: list[Order] = []
    seq_counter = 1

    for u in target_users:
        orders_count = rnd.randint(1, max_orders_per_customer)

        for _ in range(orders_count):
            order_num = _order_number(u.id, seq_counter)
            seq_counter += 1

            existing = _ensure_order(session, order_number=order_num)
            if existing:
                created.append(existing)
                continue

            fulfillment = rnd.choice([FulfillmentType.DELIVERY, FulfillmentType.PICKUP])
            status = rnd.choices(
                [OrderStatus.CREATED, OrderStatus.IN_PROGRESS, OrderStatus.READY, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED],
                weights=[0.15, 0.25, 0.20, 0.15, 0.25],
                k=1,
            )[0]

            # סניף להזמנה: אם למשתמש יש default_branch_id – נשתמש בו, אחרת נבחר רנדומלי
            branch_id = getattr(u, "default_branch_id", None) or rnd.choice(branches).id

            order = Order(
                order_number=order_num,
                user_id=u.id,
                fulfillment_type=fulfillment,
                status=status,
                branch_id=branch_id,
                total_amount=Decimal("0.00"),  # נחשב אחרי פריטים
            )
            session.add(order)
            session.flush()  # צריך order.id בשביל הילדים

            # פריטים להזמנה (2–6)
            k = rnd.randint(2, 6)
            chosen = rnd.sample(products, k=min(k, len(products)))

            total = Decimal("0.00")
            for p in chosen:
                qty = rnd.randint(1, 4)
                unit_price = Decimal(str(p.price))
                line_total = unit_price * qty
                total += line_total

                item = OrderItem(
                    order_id=order.id,
                    product_id=p.id,         # snapshot id
                    name=p.name,
                    sku=p.sku,
                    unit_price=unit_price,
                    quantity=qty,
                    picked_status=rnd.choices(
                        [PickedStatus.PENDING, PickedStatus.PICKED],
                        weights=[0.35, 0.65],
                        k=1,
                    )[0],
                )
                session.add(item)

            order.total_amount = total
            session.add(order)

            # Details לפי fulfillment
            now = dt.datetime.utcnow()

            if fulfillment == FulfillmentType.DELIVERY:
                # בוחרים slot ששייך לסניף הזה אם אפשר
                branch_slots = [s for s in slots if s.branch_id == branch_id and getattr(s, "is_active", True)]
                slot = rnd.choice(branch_slots) if branch_slots else rnd.choice(slots)

                # כתובת של המשתמש
                user_addrs = addresses_by_user.get(u.id, [])
                if user_addrs:
                    a = rnd.choice(user_addrs)
                    addr_str = f"{a.address_line}, {a.city}, {a.country}, {a.postal_code}"
                else:
                    addr_str = "Seed Address 1, Tel Aviv-Yafo, Israel, 0000000"

                # זמן חלון: “מחר” לפי day_of_week של ה-slot
                # (פשוט ל-dev; אפשר לשפר לפי תאריך אמיתי של השבוע)
                slot_start = now + dt.timedelta(days=1)
                slot_start = slot_start.replace(hour=slot.start_time.hour, minute=slot.start_time.minute, second=0, microsecond=0)
                slot_end = now + dt.timedelta(days=1)
                slot_end = slot_end.replace(hour=slot.end_time.hour, minute=slot.end_time.minute, second=0, microsecond=0)

                delivery = OrderDeliveryDetails(
                    order_id=order.id,
                    delivery_slot_id=slot.id,
                    address=addr_str,
                    slot_start=slot_start,
                    slot_end=slot_end,
                )
                session.add(delivery)

            else:  # PICKUP
                # חלון איסוף 2 שעות, “היום בערב”
                start = (now + dt.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
                end = start + dt.timedelta(hours=2)

                pickup = OrderPickupDetails(
                    order_id=order.id,
                    branch_id=branch_id,
                    pickup_window_start=start,
                    pickup_window_end=end,
                )
                session.add(pickup)

            created.append(order)

    session.flush()
    return created