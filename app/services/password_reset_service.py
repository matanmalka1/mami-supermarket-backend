from datetime import datetime, timedelta, timezone
import secrets

from app.extensions import db
from app.models.password_reset_token import PasswordResetToken
from app.middleware.error_handler import DomainError
from sqlalchemy import and_
import hashlib

RESET_TOKEN_EXPIRY_MINUTES = 30

class PasswordResetService:
    @staticmethod
    def create_token(user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)
        db.session.add(PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        ))
        db.session.commit()
        return token

    @staticmethod
    def verify_and_consume_token(token: str, user_id: int) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        prt = db.session.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.expires_at > now
            )
        ).first()
        if not prt:
            raise DomainError("INVALID_OR_EXPIRED_TOKEN", "Invalid or expired reset token", status_code=400)
        db.session.delete(prt)
        db.session.commit()

    @staticmethod
    def cleanup_expired():
        now = datetime.now(timezone.utc)
        db.session.query(PasswordResetToken).filter(PasswordResetToken.expires_at < now).delete()
        db.session.commit()
