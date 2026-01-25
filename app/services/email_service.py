import httpx
from flask import current_app

from app.middleware.error_handler import DomainError

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    api_key = current_app.config.get("BREVO_API_KEY")
    template_id = current_app.config.get("BREVO_TEMPLATE_ID")
    sender_email = current_app.config.get("SENDER_EMAIL")
    if not api_key or not template_id or not sender_email:
        raise DomainError("EMAIL_CONFIG_MISSING", "Email service is not configured")
    try:
        template_id_int = int(template_id)
    except (TypeError, ValueError) as exc:
        raise DomainError("EMAIL_CONFIG_INVALID", "Email template id is invalid") from exc

    payload = {
        "templateId": template_id_int,
        "to": [{"email": to_email}],
        "params": {"reset_url": reset_url},
        "sender": {"email": sender_email},
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    try:
        resp = httpx.post(BREVO_SEND_URL, headers=headers, json=payload, timeout=10)
    except httpx.HTTPError as exc:
        raise DomainError("EMAIL_SEND_FAILED", "Could not send reset email", status_code=502) from exc

    if resp.status_code >= 400:
        raise DomainError("EMAIL_SEND_FAILED", "Could not send reset email", status_code=502)
