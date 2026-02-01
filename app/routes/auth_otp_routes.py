"""Temporary OTP verification endpoint (DEV only)."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.middleware.error_handler import DomainError
from app.extensions import limiter
from app.schemas.auth import VerifyRegisterOTPRequest
from app.services.registration_otp_service import RegistrationOTPService
from app.utils.responses import success_envelope

blueprint = Blueprint("auth_otp", __name__)


def _ensure_otp_enabled():
    if current_app.config.get("ENABLE_REGISTRATION_OTP"):
        return
    env = current_app.config.get("APP_ENV", "production").lower()
    if env not in {"development", "testing"} and not current_app.config.get("TESTING"):
        raise DomainError(
            "OTP_NOT_ENVIRONMENT",
            "OTP verification is disabled outside development/testing (TODO: wire real service)",
            status_code=403,
        )


## CREATE (Send Register OTP)
@blueprint.post("/register/send-otp")
@limiter.limit("3 per minute")  
def send_register_otp():
    _ensure_otp_enabled()
    payload = request.get_json() or {}
    email = payload.get("email")
    if not email:
        raise DomainError("BAD_REQUEST", "Email is required", status_code=400)
    code = RegistrationOTPService.create_and_send(email)
    response_body: dict[str, str] = {"message": "OTP sent"}
    env = current_app.config.get("APP_ENV", "production").lower()
    if env in {"development", "testing"} or current_app.config.get("TESTING"):
        response_body["code"] = code
    return jsonify(success_envelope(response_body)), 200


## CREATE (Verify Register OTP)
@blueprint.post("/register/verify-otp")
@limiter.limit("10 per minute")  # Prevent brute force attacks on OTP codes
def verify_register_otp():
    _ensure_otp_enabled()
    payload = VerifyRegisterOTPRequest.model_validate(request.get_json() or {})
    RegistrationOTPService.verify_and_consume(payload.email, payload.code)
    return jsonify(success_envelope({"message": "OTP verified"})), 200
