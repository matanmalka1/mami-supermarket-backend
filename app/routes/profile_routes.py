"""Profile and address management endpoints."""

from __future__ import annotations

from uuid import UUID
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.schemas.profile import (
    AddressLocationRequest,
    AddressRequest,
    AddressUpdateRequest,
    MembershipRequest,
    UpdatePhoneRequest,
    UpdateProfileRequest,
)
from app.services.profile import AddressService, ProfileService
from app.utils.request_utils import current_user_id, parse_json_or_400
from app.utils.responses import success_envelope

blueprint = Blueprint("profile", __name__)


## UPDATE (Phone)
@blueprint.patch("/phone")
@jwt_required()
def update_phone():
    """Update user's phone number."""
    user_id = current_user_id()
    payload = UpdatePhoneRequest.model_validate(parse_json_or_400())
    profile = ProfileService.update_phone(user_id, payload)
    return jsonify(success_envelope(profile.model_dump()))


## UPDATE (Profile)
@blueprint.patch("")
@jwt_required()
def update_profile():
    """Update user profile information."""
    user_id = current_user_id()
    payload = UpdateProfileRequest.model_validate(parse_json_or_400())
    profile = ProfileService.update_profile(user_id, payload)
    return jsonify(success_envelope(profile.model_dump()))

## READ (Profile)
@blueprint.get("")
@jwt_required()
def get_profile():
    """Return full user profile (including loyalty if needed)."""
    user_id = current_user_id()
    profile = ProfileService.get_user_profile(user_id)
    return jsonify(success_envelope(profile.model_dump())), 200


## READ (Addresses)
@blueprint.get("/addresses")
@jwt_required()
def list_addresses():
    """List user's saved delivery addresses."""
    user_id = current_user_id()
    addresses = AddressService.list_addresses(user_id)
    return jsonify(success_envelope([addr.model_dump() for addr in addresses]))


## CREATE (Address)
@blueprint.post("/addresses")
@jwt_required()
def create_address():
    """Add a new delivery address."""
    user_id = current_user_id()
    payload = AddressRequest.model_validate(parse_json_or_400())
    address = AddressService.create_address(user_id, payload)
    return jsonify(success_envelope(address.model_dump())), 201


## UPDATE (Address)
@blueprint.put("/addresses/<uuid:address_id>")
@jwt_required()
def update_address(address_id: UUID):
    """Update an existing delivery address."""
    user_id = current_user_id()
    payload = AddressUpdateRequest.model_validate(parse_json_or_400())
    address = AddressService.update_address(user_id, address_id, payload)
    return jsonify(success_envelope(address.model_dump()))


## UPDATE (Address Location)
@blueprint.patch("/addresses/<uuid:address_id>/location")
@jwt_required()
def update_address_location(address_id: UUID):
    """Update GPS tags for an address."""
    user_id = current_user_id()
    payload = AddressLocationRequest.model_validate(parse_json_or_400())
    address = AddressService.update_location(user_id, address_id, payload)
    return jsonify(success_envelope(address.model_dump()))


## DELETE (Address)
@blueprint.delete("/addresses/<uuid:address_id>")
@jwt_required()
def delete_address(address_id: UUID):
    """Delete a delivery address."""
    user_id = current_user_id()
    result = AddressService.delete_address(user_id, address_id)
    return jsonify(success_envelope(result))


## UPDATE (Default Address)
@blueprint.patch("/addresses/<uuid:address_id>/default")
@jwt_required()
def set_default_address(address_id: UUID):
    """Set an address as the default delivery address."""
    user_id = current_user_id()
    address = AddressService.set_default_address(user_id, address_id)
    return jsonify(success_envelope(address.model_dump()))


## UPDATE (Membership)
@blueprint.post("/membership")
@jwt_required()
def set_membership():
    """Update the user's membership tier."""
    payload = MembershipRequest.model_validate(parse_json_or_400())
    tier = ProfileService.update_membership(current_user_id(), payload.tier)
    return jsonify(success_envelope({"tier": tier.value}))
