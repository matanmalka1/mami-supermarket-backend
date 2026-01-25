"""Authentication endpoints."""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from urllib.parse import quote

from app.middleware.error_handler import DomainError
from app.extensions import limiter
from app.services.audit_service import AuditService
from app.utils.responses import success_envelope
from app.schemas.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    UserResponse,
    ResetPasswordRequest,
)
from app.services.auth_service import AuthService
from app.services.password_reset_service import PasswordResetService
from app.services.email_service import send_password_reset_email

blueprint = Blueprint("auth", __name__)


def _parse_payload(request_body: dict | None) -> dict:
    if not request_body:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    return request_body


def _build_response(payload: AuthResponse):
    return jsonify(success_envelope(payload.model_dump()))

@blueprint.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = AuthService.get_user(user_id)
    if not user:
        raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
    return jsonify(
        success_envelope(
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
            )
        )
    )


@blueprint.post("/register")
def register():
    payload = RegisterRequest.model_validate(_parse_payload(request.get_json()))
    user = AuthService.register(payload)
    response = AuthService.build_auth_response(user)
    return _build_response(response), 201


@blueprint.post("/login")
@limiter.limit("5 per minute")
def login():
    payload = LoginRequest.model_validate(_parse_payload(request.get_json()))
    try:
        user = AuthService.authenticate(payload.email, payload.password)
    except DomainError as exc:
        AuditService.log_event(
            entity_type="user_login",
            action="LOGIN_FAILURE",
            context={
                "email": payload.email,
                "reason": exc.code,
            },
        )
        raise
    AuditService.log_event(
        entity_type="user_login",
        action="LOGIN_SUCCESS",
        actor_user_id=user.id,
        entity_id=user.id,
    )
    response = AuthService.build_auth_response(user)
    return _build_response(response)

# Endpoint: POST /forgot-password
@blueprint.post("/forgot-password")
def forgot_password():
    payload = request.get_json() or {}
    email = payload.get("email")
    if not email:
        raise DomainError("BAD_REQUEST", "Email is required", status_code=400)

    user = AuthService.get_user_by_email(email)
    if not user:
        AuditService.log_event(
            entity_type="user_password_reset",
            action="FORGOT_PASSWORD_REQUEST",
            context={"email": email, "result": "USER_NOT_FOUND"},
        )
        return jsonify(success_envelope("Password reset link sent")), 200

    reset_token = PasswordResetService.create_token(user.id)
    base_url = current_app.config.get("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    reset_url = f"{base_url}/reset-password?token={quote(reset_token)}"
    send_password_reset_email(email, reset_url)

    response_body = {"message": "Password reset link sent"}
    if current_app.config.get("APP_ENV") == "development" or current_app.config.get("TESTING"):
        response_body["reset_token"] = reset_token

    AuditService.log_event(
        entity_type="user_password_reset",
        action="FORGOT_PASSWORD_REQUEST",
        actor_user_id=user.id,
        entity_id=user.id,
        context={"email": email, "result": "SUCCESS", "reset_token": "***"},
    )
    return jsonify(success_envelope(response_body)), 200

# Endpoint: POST /auth/reset-password
@blueprint.post("/reset-password")
def reset_password():
    payload = ResetPasswordRequest.model_validate(request.get_json() or {})
    user = AuthService.get_user_by_email(payload.email)
    if not user:
        raise DomainError("USER_NOT_FOUND", "User not found", status_code=404)
    # אימות טוקן
    PasswordResetService.verify_and_consume_token(payload.token, user.id)
    # עדכון סיסמה
    AuthService.set_password(user.id, payload.new_password)
    AuditService.log_event(
        entity_type="user_password_reset",
        action="RESET_PASSWORD",
        actor_user_id=user.id,
        entity_id=user.id,
        context={"email": user.email},
    )
    return jsonify(success_envelope({"message": "Password has been reset"})), 200

@blueprint.post("/change-password")
@jwt_required()
def change_password():
    payload = ChangePasswordRequest.model_validate(_parse_payload(request.get_json()))
    user_id = get_jwt_identity()
    AuthService.change_password(user_id, payload.current_password, payload.new_password)
    return jsonify(success_envelope({"message": "Password updated"}))
