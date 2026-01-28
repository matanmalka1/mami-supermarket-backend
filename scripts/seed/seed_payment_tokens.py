# seed/seed_payment_tokens.py
from __future__ import annotations

import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_token import PaymentToken
from app.models.user import User


def _ensure_payment_token(
    session: Session,
    *,
    user_id,
    provider: str,
    provider_token: str,
    is_default: bool,
    brand: str,
    last4: str,
    exp_month: int,
    exp_year: int,
) -> PaymentToken:
    existing = session.execute(
        select(PaymentToken).where(
            PaymentToken.user_id == user_id,
            PaymentToken.provider == provider,
            PaymentToken.provider_token == provider_token,
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
        provider_token=provider_token,
        is_default=is_default,
        brand=brand,
        last4=last4,
        exp_month=exp_month,
        exp_year=exp_year,
    )
    session.add(pt)
    return pt


def seed_payment_tokens(session: Session) -> list[PaymentToken]:
    users = session.execute(select(User)).scalars().all()
    if not users:
        raise RuntimeError("No users found. Seed users first.")

    created: list[PaymentToken] = []


    for u in users:
        session.execute(
            PaymentToken.__table__.update()
            .where(PaymentToken.user_id == u.id)
            .values(is_default=False)
        )

        provider_token = f"tok_{secrets.token_urlsafe(24)}"
        created.append(
            _ensure_payment_token(
                session,
                user_id=u.id,
                provider="mockpay",
                provider_token=provider_token,
                is_default=True,
                brand="VISA",
                last4="4242",
                exp_month=12,
                exp_year=2029,
            )
        )

        if str(u.email).endswith("@example.com"):
            provider_token2 = f"tok_{secrets.token_urlsafe(24)}"
            created.append(
                _ensure_payment_token(
                    session,
                    user_id=u.id,
                    provider="mockpay",
                    provider_token=provider_token2,
                    is_default=False,
                    brand="MASTERCARD",
                    last4="1111",
                    exp_month=7,
                    exp_year=2028,
                )
            )

    session.flush()
    return created