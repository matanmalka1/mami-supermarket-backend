"""Address management service."""

from __future__ import annotations
from typing import Any

from ....extensions import db
from ....models import Address
from ....schemas.profile import (
    AddressLocationRequest,
    AddressRequest,
    AddressResponse,
    AddressUpdateRequest,
)
from ...audit_service import AuditService
from .helpers import commit_with_audit, ENTITY_TYPE, fetch_address, update_field
from .mappers import address_to_response


class AddressService:
    """Address operations used by the profile routes."""

    _ADDRESS_FIELDS = ("address_line", "city", "postal_code", "country")

    @staticmethod
    def list_addresses(user_id: int) -> list[AddressResponse]:
        addresses = (
            db.session.query(Address)
            .filter_by(user_id=user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
            .all()
        )
        return [address_to_response(addr) for addr in addresses]

    @staticmethod
    def create_address(user_id: int, data: AddressRequest) -> AddressResponse:
        if data.is_default:
            db.session.query(Address).filter_by(user_id=user_id, is_default=True).update(
                {"is_default": False}
            )
        address = Address(
            user_id=user_id,
            address_line=data.address_line,
            city=data.city,
            postal_code=data.postal_code,
            country=data.country,
            is_default=data.is_default,
        )
        db.session.add(address)
        commit_with_audit(
            user_id,
            address.id,
            action="CREATE",
            error_message="Could not create address",
            new_value={
                "address_line": data.address_line,
                "city": data.city,
                "postal_code": data.postal_code,
                "country": data.country,
                "is_default": data.is_default,
            },
        )
        return address_to_response(address)

    @staticmethod
    def update_address(user_id: int, address_id: int, data: AddressUpdateRequest) -> AddressResponse:
        address = fetch_address(user_id, address_id)
        old_values: dict[str, Any] = {}
        new_values: dict[str, Any] = {}
        for field in AddressService._ADDRESS_FIELDS:
            update_field(address, data, field, old_values, new_values)
        if not new_values:
            return address_to_response(address)
        commit_with_audit(
            user_id,
            address.id,
            action="UPDATE",
            error_message="Could not update address",
            old_value=old_values,
            new_value=new_values,
        )
        return address_to_response(address)

    @staticmethod
    def delete_address(user_id: int, address_id: int) -> dict[str, str]:
        address = fetch_address(user_id, address_id)
        old_value = {
            "address_line": address.address_line,
            "city": address.city,
            "postal_code": address.postal_code,
            "country": address.country,
            "is_default": address.is_default,
        }
        db.session.delete(address)
        commit_with_audit(
            user_id,
            address_id,
            action="DELETE",
            error_message="Could not delete address",
            old_value=old_value,
        )
        return {"message": "Address deleted successfully"}

    @staticmethod
    def set_default_address(user_id: int, address_id: int) -> AddressResponse:
        address = fetch_address(user_id, address_id)
        db.session.query(Address).filter_by(user_id=user_id, is_default=True).update(
            {"is_default": False}
        )
        old_value = {"is_default": address.is_default}
        address.is_default = True
        commit_with_audit(
            user_id,
            address.id,
            action="SET_DEFAULT",
            error_message="Could not set default address",
            old_value=old_value,
            new_value={"is_default": True},
        )
        return address_to_response(address)

    @staticmethod
    def update_location(user_id: int, address_id: int, data: AddressLocationRequest) -> AddressResponse:
        address = fetch_address(user_id, address_id)
        old_value = {"latitude": address.latitude, "longitude": address.longitude}
        address.latitude = data.lat
        address.longitude = data.lng
        db.session.commit()
        AuditService.log_event(
            entity_type=ENTITY_TYPE,
            action="UPDATE_LOCATION",
            actor_user_id=user_id,
            entity_id=address.id,
            old_value=old_value,
            new_value={"latitude": data.lat, "longitude": data.lng},
        )
        return address_to_response(address)
