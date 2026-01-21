"""Payment provider stub for tokenized charges."""

from __future__ import annotations
from uuid import UUID, uuid4

class PaymentService:
    @staticmethod
    def charge(payment_token_id: UUID, amount: float) -> str:
        # TODO: integrate real provider; return reference id
        return f"pay_{uuid4().hex[:12]}"
