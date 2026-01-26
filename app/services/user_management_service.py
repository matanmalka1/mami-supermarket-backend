"""User management service for admin operations."""

from __future__ import annotations
from uuid import UUID
from sqlalchemy import select, func, or_
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import User
from app.models.enums import Role
from app.schemas.users import UserListItem, UserDetailResponse, UpdateUserRequest
from app.services.audit_service import AuditService
from flask_jwt_extended import get_jwt_identity

class UserManagementService:
    """Service for admin user management operations."""
    @staticmethod
    def list_users(
        q: str | None = None,
        role: Role | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[UserListItem], int]:
    
        query = select(User)
        
        # Apply filters
        if q:
            search = f"%{q}%"
            query = query.where(
                or_(
                    User.email.ilike(search),
                    User.full_name.ilike(search),
                )
            )
        
        if role is not None:
            query = query.where(User.role == role)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = db.session.execute(count_query).scalar_one()
        
        # Apply pagination and ordering
        query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
        
        users = db.session.execute(query).scalars().all()
        
        return [
            UserListItem(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ], total

    @staticmethod
    def get_user(user_id: UUID) -> UserDetailResponse:
        user = db.session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        return UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            default_branch_id=user.default_branch_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def update_user(user_id: UUID, payload: UpdateUserRequest) -> UserDetailResponse:
        current_user_id = get_jwt_identity()
        
        user = db.session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        if str(user.id) == current_user_id and payload.role is not None:
            raise DomainError(
                "CANNOT_MODIFY_SELF_ROLE",
                "Cannot modify your own role",
                status_code=403,
            )
        
        old_values = {}
        new_values = {}
        
        # Update role
        if payload.role is not None and payload.role != user.role:
            old_values["role"] = user.role.value
            new_values["role"] = payload.role.value
            user.role = payload.role
        
        # Update is_active
        if payload.is_active is not None and payload.is_active != user.is_active:
            old_values["is_active"] = user.is_active
            new_values["is_active"] = payload.is_active
            user.is_active = payload.is_active
        
        # Update full_name
        if payload.full_name is not None and payload.full_name != user.full_name:
            old_values["full_name"] = user.full_name
            new_values["full_name"] = payload.full_name
            user.full_name = payload.full_name
        
        # Update phone
        if payload.phone is not None and payload.phone != user.phone:
            old_values["phone"] = user.phone
            new_values["phone"] = payload.phone
            user.phone = payload.phone
        
        # Log audit if changes were made
        if old_values:
            AuditService.log_event(
                entity_type="User",
                entity_id=user.id,
                action="USER_UPDATED",
                actor_user_id=UUID(current_user_id),
                old_value=old_values,
                new_value=new_values,
            )
        
        db.session.commit()
        
        return UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            default_branch_id=user.default_branch_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def toggle_user(user_id: UUID, active: bool) -> UserDetailResponse:
        current_user_id = get_jwt_identity()
        
        user = db.session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        # Prevent admins from deactivating themselves
        if str(user.id) == current_user_id and not active:
            raise DomainError(
                "CANNOT_DEACTIVATE_SELF",
                "Cannot deactivate your own account",
                status_code=403,
            )
        
        if user.is_active != active:
            old_value = {"is_active": user.is_active}
            new_value = {"is_active": active}
            user.is_active = active
            
            AuditService.log_event(
                entity_type="User",
                entity_id=user.id,
                action="USER_TOGGLED",
                actor_user_id=UUID(current_user_id),
                old_value=old_value,
                new_value=new_value,
            )
            
            db.session.commit()
        
        return UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
            default_branch_id=user.default_branch_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
