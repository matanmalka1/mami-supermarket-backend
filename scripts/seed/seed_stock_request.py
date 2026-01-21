# seed/seed_stock_requests.py
from __future__ import annotations

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock_request import StockRequest  # TODO: adjust import path
from app.models.branch import Branch
from app.models.product import Product
from app.models.user import User
from app.models.enums import StockRequestType, StockRequestStatus, Role


def seed_stock_requests(session: Session, *, limit: int = 25) -> list[StockRequest]:
    branches = session.execute(select(Branch)).scalars().all()
    products = session.execute(select(Product)).scalars().all()
    users = session.execute(select(User)).scalars().all()

    if not branches:
        raise RuntimeError("No branches found. Seed branches first.")
    if not products:
        raise RuntimeError("No products found. Seed products first.")
    if not users:
        raise RuntimeError("No users found. Seed users first.")

    # actor עדיף מנהל/אדמין; אם אין אז משתמש ראשון
    actors = [u for u in users if getattr(u, "role", None) in (Role.MANAGER, Role.ADMIN)]
    actor = actors[0] if actors else users[0]

    rnd = random.Random(777)
    created: list[StockRequest] = []

    for _ in range(min(limit, len(products))):
        b = rnd.choice(branches)
        p = rnd.choice(products)

        req_type = rnd.choice([StockRequestType.ADD_QUANTITY, StockRequestType.SET_QUANTITY])
        qty = rnd.randint(5, 80) if req_type == StockRequestType.ADD_QUANTITY else rnd.randint(0, 200)

        status = rnd.choices(
            [StockRequestStatus.PENDING, StockRequestStatus.APPROVED, StockRequestStatus.REJECTED],
            weights=[0.75, 0.20, 0.05],
            k=1,
        )[0]

        sr = StockRequest(
            branch_id=b.id,
            product_id=p.id,
            quantity=qty,
            request_type=req_type,
            status=status,
            actor_user_id=actor.id,
        )
        session.add(sr)
        created.append(sr)

    session.flush()
    return created