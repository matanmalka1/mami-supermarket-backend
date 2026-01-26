"""Admin user management routes."""

from __future__ import annotations
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.middleware.auth import require_role
from app.middleware.error_handler import DomainError
from app.models.enums import Role
from app.schemas.users import UpdateUserRequest
from app.services.user_management_service import UserManagementService
from app.utils.responses import success_envelope
from app.utils.request_params import parse_int, parse_bool, parse_enum

blueprint = Blueprint("admin_users", __name__)


## READ (List Users)
@blueprint.get("")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def list_users():
    """List all users with optional filters."""
    q = request.args.get("q")
    role = parse_enum(request.args.get("role"), Role)
    is_active = parse_bool(request.args.get("isActive"))
    limit = parse_int(request.args.get("limit", "50"), default=50, max_value=200)
    offset = parse_int(request.args.get("offset", "0"), default=0)
    
    users, total = UserManagementService.list_users(
        q=q,
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    
    return jsonify({
        "data": [user.model_dump() for user in users],
        "total": total,
        "limit": limit,
        "offset": offset,
    })


## READ (Get User)
@blueprint.get("/<int:user_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def get_user(user_id: int):
    """Get detailed user information."""
    user = UserManagementService.get_user(user_id)
    return jsonify(success_envelope(user.model_dump()))


## UPDATE (User)
@blueprint.patch("/<int:user_id>")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def update_user(user_id: int):
    """Update user administrative fields."""
    data = request.get_json()
    if not data:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    
    payload = UpdateUserRequest.model_validate(data)
    user = UserManagementService.update_user(user_id, payload)
    
    return jsonify(success_envelope(user.model_dump()))


## TOGGLE ACTIVE (User)
@blueprint.patch("/<int:user_id>/toggle")
@jwt_required()
@require_role(Role.MANAGER, Role.ADMIN)
def toggle_user(user_id: int):
    """Toggle user active status."""
    active = parse_bool(request.args.get("active"))
    if active is None:
        raise DomainError("MISSING_ACTIVE_PARAM", "Missing 'active' query parameter", status_code=400)
    
    user = UserManagementService.toggle_user(user_id, active)
    return jsonify(success_envelope(user.model_dump()))
