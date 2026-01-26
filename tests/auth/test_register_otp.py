import hashlib
import httpx

from app.models.registration_otp import RegistrationOTP
from app.services.registration_otp_service import RegistrationOTPService

def _configure_otp_env(test_app):
    test_app.config.update(
        {
            "BREVO_API_KEY": "test-key",
            "BREVO_REGISTER_OTP_ID": "3",
            "BREVO_SENDER_EMAIL": "sender@example.com",
            "ENABLE_REGISTRATION_OTP": True,
        }
    )

def test_send_register_otp_sends_email(client, monkeypatch, session, test_app):
    _configure_otp_env(test_app)
    captured = {}

    def fake_send(email, code):
        captured["email"] = email
        captured["code"] = code

    monkeypatch.setattr(
        "app.services.registration_otp_service.send_register_otp_email",
        fake_send,
    )
    monkeypatch.setattr(
        "app.services.registration_otp_service.secrets.randbelow", lambda _: 234
    )

    resp = client.post(
        "/api/v1/auth/register/send-otp", json={"email": "otp@example.com"}
    )
    assert resp.status_code == 200
    body = resp.get_json()["data"]
    assert body["message"] == "OTP sent"
    assert body["code"] == captured["code"] == "1234"
    assert captured["email"] == "otp@example.com"

    stored = session.query(RegistrationOTP).filter_by(email="otp@example.com").first()
    assert stored
    expected_hash = hashlib.sha256(body["code"].encode()).hexdigest()
    assert stored.code_hash == expected_hash

def test_send_register_otp_missing_config_fails(client, test_app):
    test_app.config["ENABLE_REGISTRATION_OTP"] = True
    for key in ("BREVO_API_KEY", "BREVO_REGISTER_OTP_ID", "BREVO_SENDER_EMAIL"):
        test_app.config[key] = ""

    resp = client.post(
        "/api/v1/auth/register/send-otp", json={"email": "otp@example.com"}
    )
    assert resp.status_code == 400
    error = resp.get_json()["error"]
    assert error["code"] == "EMAIL_CONFIG_MISSING"

def test_send_register_otp_handles_brevo_failure(client, monkeypatch, test_app):
    _configure_otp_env(test_app)

    class FakeResp:
        status_code = 503
        text = "service down"

    def fake_post(*args, **kwargs):
        return FakeResp()

    monkeypatch.setattr("app.services.email_service.httpx.post", fake_post)

    resp = client.post(
        "/api/v1/auth/register/send-otp", json={"email": "otp@example.com"}
    )
    assert resp.status_code == 503
    assert resp.get_json()["error"]["code"] == "EMAIL_SEND_FAILED"

    monkeypatch.setattr(
        "app.services.email_service.httpx.post",
        lambda *args, **kwargs: (_ for _ in ()).throw(httpx.HTTPError("boom")),
    )
    resp2 = client.post(
        "/api/v1/auth/register/send-otp", json={"email": "otp@example.com"}
    )
    assert resp2.status_code == 503
    assert resp2.get_json()["error"]["code"] == "EMAIL_SEND_FAILED"

def test_verify_register_otp_consumes_code(client, monkeypatch, session, test_app):
    _configure_otp_env(test_app)
    monkeypatch.setattr(
        "app.services.registration_otp_service.send_register_otp_email",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "app.services.registration_otp_service.secrets.randbelow", lambda _: 234
    )

    code = RegistrationOTPService.create_and_send("otp@example.com")
    resp = client.post(
        "/api/v1/auth/register/verify-otp",
        json={"email": "otp@example.com", "code": code},
    )
    assert resp.status_code == 200

    stored = session.query(RegistrationOTP).filter_by(email="otp@example.com").first()
    assert stored.is_used is True

    second = client.post(
        "/api/v1/auth/register/verify-otp",
        json={"email": "otp@example.com", "code": code},
    )
    assert second.status_code == 400

def test_verify_register_otp_blocked_in_production(test_app, client):
    original_testing = test_app.config.get("TESTING")
    original_env = test_app.config.get("APP_ENV")
    test_app.config["TESTING"] = False
    test_app.config["APP_ENV"] = "production"
    test_app.config["ENABLE_REGISTRATION_OTP"] = False
    try:
        response = client.post(
            "/api/v1/auth/register/verify-otp",
            json={"email": "otp@example.com", "code": "1234"},
        )
        assert response.status_code == 403
    finally:
        test_app.config["TESTING"] = original_testing
        test_app.config["APP_ENV"] = original_env
