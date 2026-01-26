import hashlib
from datetime import datetime, timedelta

from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService
from app.services.password_reset_service import PasswordResetService
from app.models.password_reset_token import PasswordResetToken

def _register_user(test_app):
    payload = RegisterRequest(email="resetuser@example.com", password="Secret123!", full_name="Reset User")
    with test_app.app_context():
        user = AuthService.register(payload)
        user_id = user.id
    return user_id, payload.email

def _configure_email(test_app):
    test_app.config.update(
        {
            "BREVO_API_KEY": "test-key",
            "BREVO_RESET_TOKEN_OTP_ID": "1",
            "BREVO_SENDER_EMAIL": "sender@example.com",
            "FRONTEND_BASE_URL": "http://frontend",
            "APP_ENV": "development",
        }
    )

def test_forgot_password_sends_email_and_persists_hash(monkeypatch, client, session, test_app):
    called = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        called["url"] = url
        called["json"] = json

        class Resp:
            status_code = 200

            @property
            def text(self) -> str:
                return "{}"

        return Resp()

    monkeypatch.setattr("app.services.email_service.httpx.post", fake_post)
    _configure_email(test_app)
    user_id, email = _register_user(test_app)

    resp = client.post("/api/v1/auth/forgot-password", json={"email": email})
    assert resp.status_code == 200
    body = resp.get_json().get("data")
    assert body.get("reset_token")
    assert called["url"].endswith("/smtp/email")
    assert body["reset_token"] in called["json"]["params"]["reset_url"]

    token_hash = hashlib.sha256(body["reset_token"].encode()).hexdigest()
    stored = session.query(PasswordResetToken).filter_by(user_id=user_id).first()
    assert stored and stored.token_hash == token_hash


def test_forgot_password_unknown_email_is_generic(monkeypatch, client):
    called = False

    def fake_post(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr("app.services.email_service.httpx.post", fake_post)

    resp = client.post("/api/v1/auth/forgot-password", json={"email": "missing@example.com"})
    assert resp.status_code == 200
    assert resp.get_json().get("data") == "Password reset link sent"
    assert called is False

def test_reset_password_consumes_token_and_changes_password(client, session, test_app):
    user_id, email = _register_user(test_app)
    token = PasswordResetService.create_token(user_id)

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "token": token, "new_password": "NewSecret123!"},
    )
    assert reset_resp.status_code == 200

    with test_app.app_context():
        authenticated = AuthService.authenticate(email, "NewSecret123!")
    assert str(authenticated.id) == str(user_id)

def test_reset_password_rejects_expired_token(client, session, test_app):
    user_id, email = _register_user(test_app)
    token = PasswordResetService.create_token(user_id)
    expired_at = datetime.utcnow() - timedelta(minutes=1)
    session.query(PasswordResetToken).filter_by(user_id=user_id).update({"expires_at": expired_at})
    session.commit()

    reset_resp = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "token": token, "new_password": "Another123!"},
    )
    assert reset_resp.status_code == 400

def test_reset_password_rejects_used_token(client, session, test_app):
    user_id, email = _register_user(test_app)
    token = PasswordResetService.create_token(user_id)

    first = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "token": token, "new_password": "First123!"},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/auth/reset-password",
        json={"email": email, "token": token, "new_password": "Second123!"},
    )
    assert second.status_code == 400
