"""Address write service."""

from __future__ import annotations
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import Address
from ....schemas.profile import (
    AddressRequest,
    AddressResponse,
    AddressUpdateRequest,
)
from ...audit_service import AuditService
from .mappers import address_to_response


def create_address(user_id: UUID, data: AddressRequest) -> AddressResponse:
    """Create a new address for a user."""
    # If this should be default, unset other defaults
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
    
    try:
        db.session.commit()
        AuditService.log_event(
            entity_type="address",
            action="CREATE",
            entity_id=address.id,
            actor_user_id=user_id,
            new_value={
                "address_line": data.address_line,
                "city": data.city,
                "postal_code": data.postal_code,
                "country": data.country,
                "is_default": data.is_default,
            },
        )
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError("DATABASE_ERROR", "Could not create address", details={"error": str(exc)})
    
    return address_to_response(address)


def update_address(user_id: UUID, address_id: UUID, data: AddressUpdateRequest) -> AddressResponse:
    """Update an existing address."""
    address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    old_values = {}
    new_values = {}
    
    if data.address_line is not None:
        old_values["address_line"] = address.address_line
        address.address_line = data.address_line
        new_values["address_line"] = data.address_line
    
    if data.city is not None:
        old_values["city"] = address.city
        address.city = data.city
        new_values["city"] = data.city
    
    if data.postal_code is not None:
        old_values["postal_code"] = address.postal_code
        address.postal_code = data.postal_code
        new_values["postal_code"] = data.postal_code
    
    if data.country is not None:
        old_values["country"] = address.country
        address.country = data.country
        new_values["country"] = data.country
    
    if not new_values:
        return address_to_response(address)
    
    try:
        db.session.commit()
        AuditService.log_event(
            entity_type="address",
            action="UPDATE",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_values,
            new_value=new_values,
        )
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError("DATABASE_ERROR", "Could not update address", details={"error": str(exc)})
    
    return address_to_response(address)


def delete_address(user_id: UUID, address_id: UUID) -> dict:
    """Delete an address."""
    address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    old_value = {
        "address_line": address.address_line,
        "city": address.city,
        "postal_code": address.postal_code,
        "country": address.country,
        "is_default": address.is_default,
    }
    
    db.session.delete(address)
    
    try:
        db.session.commit()
        AuditService.log_event(
            entity_type="address",
            action="DELETE",
            entity_id=address_id,
            actor_user_id=user_id,
            old_value=old_value,
        )
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError("DATABASE_ERROR", "Could not delete address", details={"error": str(exc)})
    
    return {"message": "Address deleted successfully"}


def set_default_address(user_id: UUID, address_id: UUID) -> AddressResponse:
    """Set an address as the default."""
    address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    
    # Unset all other defaults for this user
    db.session.query(Address).filter_by(user_id=user_id, is_default=True).update(
        {"is_default": False}
    )
    
    old_value = {"is_default": address.is_default}
    address.is_default = True
    
    try:
        db.session.commit()
        AuditService.log_event(
            entity_type="address",
            action="SET_DEFAULT",
            entity_id=address.id,
            actor_user_id=user_id,
            old_value=old_value,
            new_value={"is_default": True},
        )
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError("DATABASE_ERROR", "Could not set default address", details={"error": str(exc)})
    
    return address_to_response(address)
