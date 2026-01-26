# seed/seed_delivery_slots.py
from __future__ import annotations

from datetime import time
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.delivery_slot import DeliverySlot
from app.models.branch import Branch


def _ensure_delivery_slot(
    session: Session,
    *,
    branch_id,
    day_of_week: int,
    start_time: time,
    end_time: time,
) -> DeliverySlot:
    """
    Idempotent insert for delivery slot.
    """
    slot = session.execute(
        select(DeliverySlot).where(
            DeliverySlot.branch_id == branch_id,
            DeliverySlot.day_of_week == day_of_week,
            DeliverySlot.start_time == start_time,
            DeliverySlot.end_time == end_time,
        )
    ).scalar_one_or_none()

    if slot:
        if hasattr(slot, "is_active") and slot.is_active is False:
            slot.is_active = True
            session.add(slot)
        return slot

    slot = DeliverySlot(
        branch_id=branch_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
    )
    session.add(slot)
    return slot


def seed_delivery_slots(session: Session) -> list[DeliverySlot]:
    """
    Creates delivery slots for all branches.
    - Days: Sunday (0) to Saturday (6)
    - Time slots: 8:00-10:00, 10:00-12:00, 12:00-14:00, 14:00-16:00, 16:00-18:00, 18:00-20:00
    """
    branches = session.execute(select(Branch)).scalars().all()

    if not branches:
        raise RuntimeError("No branches found. Seed branches first.")

    created: list[DeliverySlot] = []

    time_windows = [
        (time(8, 0), time(10, 0)),
        (time(10, 0), time(12, 0)),
        (time(12, 0), time(14, 0)),
        (time(14, 0), time(16, 0)),
        (time(16, 0), time(18, 0)),
        (time(18, 0), time(20, 0)),
    ]

    for branch in branches:
        for day in range(7):
            for start, end in time_windows:
                created.append(
                    _ensure_delivery_slot(
                        session,
                        branch_id=branch.id,
                        day_of_week=day,
                        start_time=start,
                        end_time=end,
                    )
                )

    session.flush()
    return created
