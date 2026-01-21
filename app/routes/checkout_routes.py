"""Checkout preview and confirm endpoints."""

from __future__ import annotations
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

@blueprint.post("/preview")
@jwt_required()
def preview():
    payload = _parse(CheckoutPreviewRequest, request.get_json())
    result = CheckoutService.preview(payload)
    return jsonify(success_envelope(result))

@blueprint.post("/confirm")
@jwt_required()
def confirm():
    payload = _parse(CheckoutConfirmRequest, request.get_json())
    result = CheckoutService.confirm(payload)
    return jsonify(success_envelope(result)), 201
