"""Authorization & ownership decorators."""

from __future__ import annotations

from functools import wraps
from typing import Callable
from uuid import UUID

from flask import g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import User
from ..models.enums import Role
from ..middleware.error_handler import DomainError

ResourceLoader = Callable[..., object]


def _current_user() -> User:
    identity = get_jwt_identity()
    if not identity:
        raise DomainError("AUTH_REQUIRED", "Authentication required", status_code=401)
    return db.session.get(User, UUID(identity))


def require_auth(view: Callable) -> Callable:
    @wraps(view)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        g.current_user = _current_user()
        return view(*args, **kwargs)

    return wrapper


def require_role(*roles: Role | str) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = _current_user()
            allowed = {
                role.value if isinstance(role, Role) else str(role)
                for role in roles
            }
            if user.role.value not in allowed:
                raise DomainError("AUTHORIZATION_ERROR", "Insufficient permissions", status_code=403)
            g.current_user = user
            return view(*args, **kwargs)

        return wrapper

    return decorator


def require_ownership(loader: ResourceLoader) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = _current_user()
            if user.role in {Role.MANAGER, Role.ADMIN}:
                g.current_user = user
                return view(*args, **kwargs)

            resource = loader(*args, **kwargs)
            owner_id = getattr(resource, "user_id", None)
            if owner_id and owner_id != user.id:
                raise DomainError("NOT_FOUND", "Resource not found", status_code=404)
            g.current_user = user
            return view(*args, **kwargs)

        return wrapper

    return decorator
