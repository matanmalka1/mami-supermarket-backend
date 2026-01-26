"""Shared request parsing helpers."""

from __future__ import annotations
from datetime import datetime
from flask import request
from flask_jwt_extended import get_jwt_identity
from app.middleware.error_handler import DomainError

def current_user_id() -> int:
    ident = get_jwt_identity()
    if not ident:
        raise DomainError("AUTH_REQUIRED", "Authentication required", status_code=401)
    try:
        return int(ident)
    except (TypeError, ValueError):
        raise DomainError("AUTH_REQUIRED", "Invalid authentication identity", status_code=401)

def parse_json_or_400() -> dict:
    body = request.get_json()
    if body is None:
        raise DomainError("BAD_REQUEST", "Missing JSON body", status_code=400)
    return body

def parse_pagination(default_limit: int = 50, default_offset: int = 0) -> tuple[int, int]:
    try:
        limit = int(request.args.get("limit", default_limit))
        offset = int(request.args.get("offset", default_offset))
    except (TypeError, ValueError):
        raise DomainError("BAD_REQUEST", "Invalid pagination parameters", status_code=400)
    return limit, offset

def parse_iso_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise DomainError("BAD_REQUEST", "Invalid date format; use ISO 8601", status_code=400)
