"""Address query service."""

from __future__ import annotations
from uuid import UUID
from ....extensions import db
from ....models import Address
from ....schemas.profile import AddressResponse
from .mappers import address_to_response


def list_addresses(user_id: UUID) -> list[AddressResponse]:
    """List all addresses for a user."""
    addresses = (
        db.session.query(Address)
        .filter_by(user_id=user_id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
        .all()
    )
    return [address_to_response(addr) for addr in addresses]
