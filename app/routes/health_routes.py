"""Health endpoint."""

# PUBLIC: This endpoint is intentionally unauthenticated for health checks.
from flask import Blueprint, jsonify
from app.utils.responses import success_envelope

blueprint = Blueprint("health", __name__)

@blueprint.get("")
def health():
    return jsonify(success_envelope({"status": "ok"}))
