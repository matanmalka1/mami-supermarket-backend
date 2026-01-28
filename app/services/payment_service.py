"""Payment provider stub for tokenized charges."""

from __future__ import annotations

from secrets import token_hex
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models.payment_token import PaymentToken

class PaymentService:
    @staticmethod
    def charge(payment_token_id: int, amount: float) -> str:
        token = db.session.get(PaymentToken, payment_token_id)

        if not token:
            raise DomainError(
                "PAYMENT_TOKEN_NOT_FOUND",
                "Payment token not found",
                status_code=404,
            )

        if not token.is_active:
            raise DomainError(
                "PAYMENT_TOKEN_INACTIVE",
                "Payment token inactive",
                status_code=400,
            )

        if token.provider != "mockpay":
            raise DomainError(
                "UNSUPPORTED_PROVIDER",
                "Payment provider not supported",
                status_code=400,
            )

        # Only return mock reference if all validations pass
        return  f"MOCKPAY-{token.id}-{token_hex(4).upper()}"
