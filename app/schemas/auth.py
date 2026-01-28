from __future__ import annotations
from datetime import datetime
from pydantic import Field, field_validator
from .common import DefaultModel
from app.utils.password import validate_password_complexity
from ..models.enums import Role

class ResetPasswordRequest(DefaultModel):
    email: str = Field(min_length=6, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    token: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z\d!@#$%^&*()_+=-]{8,64}$")

    @field_validator('new_password')
    def password_complexity(cls, v):
        validate_password_complexity(v)
        return v
    
class RegisterRequest(DefaultModel):
    email: str = Field(min_length=6, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z\d!@#$%^&*()_+=-]{8,64}$")

    @field_validator('password')
    def password_complexity(cls, v):
        validate_password_complexity(v)
        return v
    full_name: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-zא-ת\s\-']+$")
    role: Role = Role.CUSTOMER

class LoginRequest(DefaultModel):
    email: str = Field(min_length=6, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=64)

class ChangePasswordRequest(DefaultModel):
    current_password: str = Field(min_length=8, max_length=64)
    new_password: str = Field(min_length=8, max_length=64, pattern=r"^[A-Za-z\d!@#$%^&*()_+=-]{8,64}$")

    @field_validator('new_password')
    def password_complexity(cls, v):
        validate_password_complexity(v)
        return v

class UserResponse(DefaultModel):
    id: int
    email: str
    full_name: str
    role: Role

class AuthResponse(DefaultModel):
    user: UserResponse
    access_token: str = Field(min_length=16, max_length=512)
    refresh_token: str | None = Field(default=None, min_length=16, max_length=512)
    expires_at: datetime


class VerifyRegisterOTPRequest(DefaultModel):
    email: str = Field(min_length=6, max_length=100, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    code: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
