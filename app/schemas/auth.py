from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import Field
from .common import DefaultModel
from ..models.enums import Role

class RegisterRequest(DefaultModel):
    # Basic email shape check; allow anything non-space around @ and a dot.
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    full_name: str
    role: Role = Role.CUSTOMER

class LoginRequest(DefaultModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str

class ChangePasswordRequest(DefaultModel):
    current_password: str
    new_password: str = Field(min_length=8)

class UserResponse(DefaultModel):
    id: UUID
    email: str
    full_name: str
    role: Role

class AuthResponse(DefaultModel):
    user: UserResponse
    access_token: str
    refresh_token: str | None = None
    expires_at: datetime
