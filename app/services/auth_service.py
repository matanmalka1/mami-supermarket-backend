from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy.exc import IntegrityError
from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import User
from ..schemas.auth import AuthResponse, RegisterRequest, UserResponse
from ..utils.security import hash_password, verify_password

TokenMetadata = dict[str, Any]

class AuthService:
    @staticmethod
    def register(data: RegisterRequest) -> User:
        session = db.session
        exists = session.query(User).filter_by(email=data.email).first()
        if exists:
            raise DomainError("USER_EXISTS", "User already exists")

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role=data.role,
        )
        session.add(user)
        session.flush()
        try:
            session.commit()
        except IntegrityError as exc:
            session.rollback()
            raise DomainError("DATABASE_ERROR", "Could not create user", details={"error": str(exc)})

        return user

    @staticmethod
    def authenticate(email: str, password: str) -> User:
        session = db.session
        user = session.query(User).filter_by(email=email).first()
        if not user:
            raise DomainError("INVALID_CREDENTIALS", "Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise DomainError("INVALID_CREDENTIALS", "Invalid email or password")

        return user

    @staticmethod
    def change_password(user_id: str, current_password: str, new_password: str) -> None:
        session = db.session
        user = session.get(User, user_id)
        if not user:
            raise DomainError("USER_NOT_FOUND", "Authenticated user not found")

        if not verify_password(current_password, user.password_hash):
            raise DomainError("INVALID_CREDENTIALS", "Current password is incorrect")

        user.password_hash = hash_password(new_password)
        session.add(user)
        session.commit()

    @staticmethod
    def build_auth_response(user: User) -> AuthResponse:
        access_expires = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES")
        expires_delta = access_expires if isinstance(access_expires, timedelta) else timedelta(minutes=15)
        now = datetime.utcnow()

        additional_claims = {
            "role": user.role.value,
        }

        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=str(user.id))

        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=now + expires_delta,
        )

    @staticmethod
    def get_user(user_id: str) -> User | None:
        return db.session.get(User, user_id)
