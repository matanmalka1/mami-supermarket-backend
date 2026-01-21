# seed/seed_payment_tokens.py
from __future__ import annotations

import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_token import PaymentToken  # TODO: adjust import path
from app.models.user import User


def _ensure_payment_token(
    session: Session,
    *,
    user_id,
    provider: str,
    token: str,
    is_default: bool,
    metadata: dict | None = None,
) -> PaymentToken:
    existing = session.execute(
        select(PaymentToken).where(
            PaymentToken.user_id == user_id,
            PaymentToken.provider == provider,
            PaymentToken.token == token,
        )
    ).scalar_one_or_none()

    if existing:
        if is_default and getattr(existing, "is_default", False) is False:
            existing.is_default = True
            session.add(existing)
        return existing

    pt = PaymentToken(
        user_id=user_id,
        provider=provider,
        token=token,
        is_default=is_default,
        metadata_payload=metadata,
    )
    session.add(pt)
    return pt


def seed_payment_tokens(session: Session) -> list[PaymentToken]:
    users = session.execute(select(User)).scalars().all()
    if not users:
        raise RuntimeError("No users found. Seed users first.")

    created: list[PaymentToken] = []

    for u in users:
        # לפני קביעת דיפולט: כבה דיפולטים אחרים של אותו משתמש (כדי לשמור 1 דיפולט)
        session.execute(
            PaymentToken.__table__.update()
            .where(PaymentToken.user_id == u.id)
            .values(is_default=False)
        )

        # טוקן דמה שנראה “אמיתי”
        token = f"tok_{secrets.token_urlsafe(24)}"
        created.append(
            _ensure_payment_token(
                session,
                user_id=u.id,
                provider="mockpay",
                token=token,
                is_default=True,
                metadata={"last4": "4242", "brand": "VISA", "exp": "12/29"},
            )
        )

        # עוד טוקן לא-דיפולט (אופציונלי, לכל משתמש שני)
        if str(u.email).endswith("@example.com"):
            token2 = f"tok_{secrets.token_urlsafe(24)}"
            created.append(
                _ensure_payment_token(
                    session,
                    user_id=u.id,
                    provider="mockpay",
                    token=token2,
                    is_default=False,
                    metadata={"last4": "1111", "brand": "MASTERCARD", "exp": "07/28"},
                )
            )

    session.flush()
    return created