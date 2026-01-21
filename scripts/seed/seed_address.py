# seed/seed_addresses.py
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address  # תעדכן נתיב לפי הפרויקט שלך
# from app.models.user import User      # אם תרצה טיפוס


def _ensure_address(
    session: Session,
    *,
    user_id,
    address_line: str,
    city: str,
    country: str,
    postal_code: str,
) -> Address:
    """Idempotent insert: אם הכתובת כבר קיימת למשתמש – מחזיר את הקיימת."""
    existing = session.execute(
        select(Address).where(
            Address.user_id == user_id,
            Address.address_line == address_line,
            Address.city == city,
            Address.postal_code == postal_code,
        )
    ).scalar_one_or_none()

    if existing:
        return existing

    addr = Address(
        user_id=user_id,
        address_line=address_line,
        city=city,
        country=country,
        postal_code=postal_code,
    )
    session.add(addr)
    return addr


def seed_addresses(session: Session, user_ids: list) -> list[Address]:
    """
    מזין כתובות לכל המשתמשים.
    user_ids: רשימת UUIDs של משתמשים קיימים (אחרי seed של users).
    """
    # כתובות "ריאליסטיות" בישראל – תוכל להחליף/להרחיב
    address_templates = [
        ("דיזנגוף 123, דירה 4", "תל אביב-יפו", "Israel", "6433221"),
        ("אבן גבירול 77, קומה 2", "תל אביב-יפו", "Israel", "6433402"),
        ("הנשיא 10", "חיפה", "Israel", "3463807"),
        ("שדרות רוטשילד 15", "ראשון לציון", "Israel", "7536508"),
        ("הרצל 52", "רחובות", "Israel", "7642341"),
        ("בן גוריון 3", "רמת גן", "Israel", "5257333"),
        ("ויצמן 19", "כפר סבא", "Israel", "4432009"),
        ("הנביאים 25", "ירושלים", "Israel", "9510416"),
        ("שד' ירושלים 102", "אשדוד", "Israel", "7745120"),
        ("העצמאות 8", "באר שבע", "Israel", "8453210"),
    ]

    created: list[Address] = []

    for i, user_id in enumerate(user_ids):
        # לכל משתמש כתובת 1 (ולחלקם כתובת 2)
        t1 = address_templates[i % len(address_templates)]
        created.append(
            _ensure_address(
                session,
                user_id=user_id,
                address_line=t1[0],
                city=t1[1],
                country=t1[2],
                postal_code=t1[3],
            )
        )

        # כתובת נוספת לכל משתמש שני (רק כדי שיהיה מגוון)
        if i % 2 == 0:
            t2 = address_templates[(i + 3) % len(address_templates)]
            created.append(
                _ensure_address(
                    session,
                    user_id=user_id,
                    address_line=t2[0],
                    city=t2[1],
                    country=t2[2],
                    postal_code=t2[3],
                )
            )

    session.flush()  # נותן IDs לפני commit אם צריך בהמשך
    return created