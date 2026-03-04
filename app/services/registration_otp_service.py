from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models.registration_otp import RegistrationOTP
from app.models.user import User
from app.services.email_service import send_register_otp_email


OTP_EXPIRY_MINUTES = 10


class RegistrationOTPService:
    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _hash_code(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    @classmethod
    def _ensure_table_exists(cls) -> None:
        bind = db.session.get_bind()
        if bind is not None:
            RegistrationOTP.__table__.create(bind=bind, checkfirst=True)

    @classmethod
    def create_and_send(cls, email: str) -> str:
        cls._ensure_table_exists()
        normalized = cls._normalize_email(email)
        session = db.session
        
        # Check if user already exists
        existing_user = session.query(User).filter_by(email=normalized).first()
        if existing_user:
            raise DomainError(
                "USER_ALREADY_EXISTS",
                "An account with this email already exists",
                status_code=409,
            )
        
        session.query(RegistrationOTP).filter_by(email=normalized).delete(
            synchronize_session=False
        )
        code = f"{secrets.randbelow(9000) + 1000:04d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
        otp = RegistrationOTP(
            email=normalized,
            code_hash=cls._hash_code(code),
            expires_at=expires_at,
            is_used=False,
        )
        session.add(otp)
        session.commit()
        send_register_otp_email(email, code)
        return code

    @classmethod
    def verify_and_consume(cls, email: str, code: str) -> None:
        normalized = cls._normalize_email(email)
        code_hash = cls._hash_code(code)
        now = datetime.now(timezone.utc)
        otp = (
            db.session.query(RegistrationOTP)
            .filter(
                RegistrationOTP.email == normalized,
                RegistrationOTP.code_hash == code_hash,
                RegistrationOTP.is_used.is_(False),
                RegistrationOTP.expires_at > now,
            )
            .first()
        )
        if not otp:
            raise DomainError(
                "INVALID_REGISTRATION_OTP",
                "Invalid or expired OTP code",
                status_code=400,
            )
        otp.is_used = True
        db.session.add(otp)
        db.session.commit()
