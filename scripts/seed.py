"""Simple seeding helpers for the initial data."""

from datetime import time

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import AppConfig
from app.models import Base, Branch, DeliverySlot


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


def main() -> None:
    config = AppConfig()
    engine = create_engine(config.DATABASE_URL)

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            branch = seed_warehouse_branch(session)
            seed_delivery_slots(session, branch)
            session.commit()
    except IntegrityError:
        print(\"Seed already applied or constraint violated\")


if __name__ == "__main__":
    main()
