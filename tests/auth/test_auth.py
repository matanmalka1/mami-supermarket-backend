import pytest

from app.middleware.error_handler import DomainError
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService

def test_register_and_authenticate(session, test_app):
    with test_app.app_context():
        payload = RegisterRequest(email="user@example.com", password="secret123", full_name="User One")
        user = AuthService.register(payload)
        authed = AuthService.authenticate(payload.email, payload.password)
        resp = AuthService.build_auth_response(user)

    assert authed.id == user.id
    assert resp.access_token and resp.refresh_token


def test_register_duplicate_user(session, test_app):
    with test_app.app_context():
        payload = RegisterRequest(email="dup@example.com", password="secret123", full_name="Dup User")
        AuthService.register(payload)
        with pytest.raises(DomainError) as exc:
            AuthService.register(payload)
    assert exc.value.code == "USER_EXISTS"


def test_change_password(session, test_app):
    with test_app.app_context():
        payload = RegisterRequest(email="changeme@example.com", password="oldpass123", full_name="Changer")
        user = AuthService.register(payload)
        with pytest.raises(DomainError):
            AuthService.change_password(user.id, "wrongpass", "newpass123")
        AuthService.change_password(user.id, payload.password, "newpass123")
        with pytest.raises(DomainError):
            AuthService.authenticate(payload.email, payload.password)
        authed = AuthService.authenticate(payload.email, "newpass123")
    assert authed.id == user.id
