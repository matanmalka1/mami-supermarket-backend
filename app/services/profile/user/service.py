"""Profile management service."""

from __future__ import annotations
from sqlalchemy.exc import IntegrityError
from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import User
from ....schemas.profile import (
    UpdatePhoneRequest,
    UpdateProfileRequest,
    UserProfileResponse,
)
from app.models.enums import MembershipTier
from app.services.audit_service import AuditService


class ProfileService:
    @staticmethod
    def get_user_profile(user_id: int) -> UserProfileResponse:
        """Get user profile information."""
        user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role.value,
        )

    @staticmethod
    def update_phone(user_id: int, data: UpdatePhoneRequest) -> UserProfileResponse:
        """Update user phone number."""
        user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        old_phone = user.phone
        user.phone = data.phone
        
        try:
            db.session.commit()
            AuditService.log_event(
                entity_type="user",
                action="UPDATE_PHONE",
                entity_id=user.id,
                actor_user_id=user_id,
                old_value={"phone": old_phone},
                new_value={"phone": data.phone},
            )
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError("DATABASE_ERROR", "Could not update phone", details={"error": str(exc)})
        
        return ProfileService.get_user_profile(user_id)

    @staticmethod
    def update_profile(user_id: int, data: UpdateProfileRequest) -> UserProfileResponse:
        """Update user profile information."""
        user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
        
        old_values = {}
        new_values = {}
        
        if data.full_name is not None:
            old_values["full_name"] = user.full_name
            user.full_name = data.full_name
            new_values["full_name"] = data.full_name
        
        if data.phone is not None:
            old_values["phone"] = user.phone
            user.phone = data.phone
            new_values["phone"] = data.phone
        
        if not new_values:
            return ProfileService.get_user_profile(user_id)
        
        try:
            db.session.commit()
            AuditService.log_event(
                entity_type="user",
                action="UPDATE_PROFILE",
                entity_id=user.id,
                actor_user_id=user_id,
                old_value=old_values,
                new_value=new_values,
            )
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError("DATABASE_ERROR", "Could not update profile", details={"error": str(exc)})
        
        return ProfileService.get_user_profile(user_id)

    @staticmethod
    def update_membership(user_id: int, tier: MembershipTier) -> MembershipTier:
        user = db.session.query(User).filter_by(id=user_id, is_active=True).first()
        if not user:
            raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)

        old_tier = user.membership_tier
        user.membership_tier = tier.value

        try:
            db.session.commit()
            AuditService.log_event(
                entity_type="user",
                action="UPDATE_MEMBERSHIP",
                actor_user_id=user_id,
                entity_id=user.id,
                old_value={"membership_tier": old_tier},
                new_value={"membership_tier": tier.value},
            )
        except IntegrityError as exc:
            db.session.rollback()
            raise DomainError("DATABASE_ERROR", "Could not update membership", details={"error": str(exc)})

        return tier
