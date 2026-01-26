"""Profile and address management schemas."""

from __future__ import annotations

from pydantic import Field
from app.models.enums import MembershipTier
from .common import DefaultModel

class UpdatePhoneRequest(DefaultModel):
    phone: str = Field(min_length=1, max_length=32)

class UpdateProfileRequest(DefaultModel):
    full_name: str | None = Field(None, min_length=1, max_length=128)
    phone: str | None = Field(None, min_length=1, max_length=32)

class AddressRequest(DefaultModel):
    address_line: str = Field(min_length=1, max_length=256)
    city: str = Field(min_length=1, max_length=64)
    postal_code: str = Field(min_length=1, max_length=16)
    country: str = Field(min_length=1, max_length=64)
    is_default: bool = False

class AddressUpdateRequest(DefaultModel):
    address_line: str | None = Field(None, min_length=1, max_length=256)
    city: str | None = Field(None, min_length=1, max_length=64)
    postal_code: str | None = Field(None, min_length=1, max_length=16)
    country: str | None = Field(None, min_length=1, max_length=64)

class AddressResponse(DefaultModel):
    id: int
    user_id: int
    address_line: str
    city: str
    postal_code: str
    country: str
    is_default: bool = False
    lat: float | None = None
    lng: float | None = None

class UserProfileResponse(DefaultModel):
    id: int
    email: str
    full_name: str
    phone: str | None = None
    role: str


class AddressLocationRequest(DefaultModel):
    lat: float
    lng: float


class MembershipRequest(DefaultModel):
    tier: MembershipTier
