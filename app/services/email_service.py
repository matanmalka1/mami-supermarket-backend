import httpx
from flask import current_app

from app.middleware.error_handler import DomainError

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"

def _resolve_brevo_template(template_key: str) -> tuple[str, int, str]:
    api_key = current_app.config.get("BREVO_API_KEY")
    template_id = current_app.config.get(template_key)
    sender_email = current_app.config.get("BREVO_SENDER_EMAIL")
    if not api_key or not template_id or not sender_email:
        raise DomainError("EMAIL_CONFIG_MISSING", "Email service is not configured")
    try:
        template_id_int = int(template_id)
    except (TypeError, ValueError) as exc:
        raise DomainError("EMAIL_CONFIG_INVALID", "Email template id is invalid") from exc
    return api_key, template_id_int, sender_email

def _send_template_email(
    api_key: str,
    template_id: int,
    sender_email: str,
    to_email: str,
    params: dict,
) -> None:
    payload = {
        "templateId": template_id,
        "to": [{"email": to_email}],
        "params": params,
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
        current_app.logger.exception("Brevo request failed", exc_info=exc)
        raise DomainError(
            "EMAIL_SEND_FAILED",
            "Could not send email",
            status_code=503,
        ) from exc
    resp_text = getattr(resp, "text", "")
    current_app.logger.info(
    "Brevo template %s responded %s: %s",
    template_id,
    resp.status_code,
    resp_text,
)
    if resp.status_code >= 400:
        raise DomainError(
            "EMAIL_SEND_FAILED",
            "Could not send email",
            status_code=503,
            details={"status": resp.status_code, "body": resp_text},
        )


def send_password_reset_email(to_email: str, reset_url: str) -> None:
    api_key, template_id, sender_email = _resolve_brevo_template("BREVO_RESET_TOKEN_OTP_ID")
    _send_template_email(api_key, template_id, sender_email, to_email, {"reset_url": reset_url})


def send_register_otp_email(to_email: str, otp_code: str) -> None:
    api_key, template_id, sender_email = _resolve_brevo_template("BREVO_REGISTER_OTP_ID")
    _send_template_email(
        api_key,
        template_id,
        sender_email,
        to_email,
        {
            "otp_code": otp_code,
            "code": otp_code,
            "verification_code": otp_code,
        },
    )
