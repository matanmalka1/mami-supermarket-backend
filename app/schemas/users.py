"""User management schemas for admin endpoints."""

from __future__ import annotations

from datetime import datetime
from ..models.enums import Role
from .common import DefaultModel

class UserListItem(DefaultModel):
    """User list item response."""
    id: int
    email: str
    full_name: str
    phone: str | None
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime

class UserDetailResponse(DefaultModel):
    """Detailed user response."""
    id: int
    email: str
    full_name: str
    phone: str | None
    role: Role
    is_active: bool
    default_branch_id: int | None
    created_at: datetime
    updated_at: datetime

class UpdateUserRequest(DefaultModel):
    """Admin user update request."""
    role: Role | None = None
    is_active: bool | None = None
    full_name: str | None = None
    phone: str | None = None

class UserListResponse(DefaultModel):
    """Paginated user list response."""
    data: list[UserListItem]
    total: int
    limit: int
    offset: int
