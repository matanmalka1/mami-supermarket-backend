"""Simple seeding helpers for the initial data."""

from __future__ import annotations

import os
import sys
from datetime import time
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.config import AppConfig
from app.models import Base, Branch, DeliverySlot, Role, User


def seed_warehouse_branch(session: Session) -> Branch:
    branch = session.query(Branch).filter_by(name="The Warehouse").first()
    if branch:
        return branch

    branch = Branch(name="The Warehouse", address="Central warehouse, main street")
    session.add(branch)
    session.flush()
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


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def main() -> None:
    config = AppConfig()
    engine = create_engine(config.DATABASE_URL)

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            branch = seed_warehouse_branch(session)
            seed_delivery_slots(session, branch)
            seed_admin_user(session)
            session.commit()
    except IntegrityError:
        print("Seed already applied or constraint violated")


if __name__ == "__main__":
    main()
