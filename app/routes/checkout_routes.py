from __future__ import annotations
"""Checkout preview and confirm endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.middleware.error_handler import DomainError
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutPreviewRequest
from app.services.checkout_service import CheckoutService
from app.utils.responses import success_envelope

blueprint = Blueprint("checkout", __name__)

def _parse(body_model, data: dict | None):
    if not data:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    return body_model.model_validate(data)

## CREATE (Checkout Preview)
@blueprint.post("/preview")
@jwt_required()
def preview():
    payload = _parse(CheckoutPreviewRequest, request.get_json())
    result = CheckoutService.preview(payload)
    return jsonify(success_envelope(result))

## CREATE (Checkout Confirm)
@blueprint.post("/confirm")
@jwt_required()
def confirm():
    json_data = request.get_json(silent=True)
    idempotency_key = request.headers.get("Idempotency-Key")
    if not idempotency_key:
        raise DomainError("MISSING_IDEMPOTENCY_KEY", "Idempotency-Key header is required", status_code=400)

    payload = _parse(CheckoutConfirmRequest, json_data)
    result, is_new = CheckoutService.confirm(payload, idempotency_key)
    status_code = 201 if is_new else 200
    return jsonify(success_envelope(result)), status_code
