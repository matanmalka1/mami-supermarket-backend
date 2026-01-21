# seed/seed_inventory.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory  # TODO: adjust import path
from app.models.product import Product
from app.models.category import Category
from app.models.branch import Branch


def _ensure_inventory(
    session: Session,
    *,
    product_id,
    branch_id,
    available_quantity: int,
    reserved_quantity: int,
) -> Inventory:
    inv = session.execute(
        select(Inventory).where(
            Inventory.product_id == product_id,
            Inventory.branch_id == branch_id,
        )
    ).scalar_one_or_none()

    if inv:
        # ברירת מחדל: seed מעדכן כדי ליישר דאטה
        inv.available_quantity = available_quantity
        inv.reserved_quantity = reserved_quantity
        session.add(inv)
        return inv

    inv = Inventory(
        product_id=product_id,
        branch_id=branch_id,
        available_quantity=available_quantity,
        reserved_quantity=reserved_quantity,
    )
    session.add(inv)
    return inv


def _qty_range_for_category(category_name: str) -> tuple[int, int]:
    """
    טווחים ריאליסטיים לפי קטגוריה.
    """
    c = category_name.lower()
    if "frozen" in c:
        return (5, 40)
    if "dairy" in c or "eggs" in c:
        return (10, 80)
    if "meat" in c or "fish" in c:
        return (5, 30)
    if "fruits" in c or "vegetables" in c:
        return (15, 120)
    if "bakery" in c:
        return (10, 90)
    if "beverages" in c:
        return (20, 200)
    if "household" in c:
        return (10, 150)
    if "personal care" in c:
        return (5, 80)
    # pantry/snacks/default
    return (10, 120)


def seed_inventory(session: Session) -> list[Inventory]:
    """
    יוצר מלאי לכל שילוב של (branch, product).
    """
    branches = session.execute(select(Branch)).scalars().all()
    products = session.execute(
        select(Product).options()
    ).scalars().all()

    if not branches:
        raise RuntimeError("No branches found. Seed branches first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")

    # כדי לדעת קטגוריה לכל מוצר בלי N+1 נביא גם categories למפה
    categories = session.execute(select(Category)).scalars().all()
    category_by_id = {c.id: c for c in categories}

    created: list[Inventory] = []
    rnd = random.Random(42)  # קבוע כדי לקבל seed יציב

    for b in branches:
        for p in products:
            cat = category_by_id.get(p.category_id)
            cat_name = cat.name if cat else "Unknown"

            lo, hi = _qty_range_for_category(cat_name)
            available = rnd.randint(lo, hi)

            # reserved קטן יחסית לזמין
            reserved = rnd.randint(0, min(8, max(0, available // 10)))

            created.append(
                _ensure_inventory(
                    session,
                    product_id=p.id,
                    branch_id=b.id,
                    available_quantity=available,
                    reserved_quantity=reserved,
                )
            )

    session.flush()
    return created