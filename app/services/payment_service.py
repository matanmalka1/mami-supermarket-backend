"""Payment provider stub for tokenized charges."""

from __future__ import annotations
from uuid import uuid4

class PaymentService:
    @staticmethod
    def charge(payment_token_id: int, amount: float) -> str:

        return f"pay_{uuid4().hex[:12]}"
