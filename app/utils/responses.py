"""Standardized API response envelope helpers."""

from __future__ import annotations
from decimal import Decimal
from typing import Any, Mapping
from pydantic import BaseModel

def _serialize(value: Any) -> Any:
    """Convert Pydantic models and common primitives into JSON-safe structures."""
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    if isinstance(value, Decimal):
        return str(value)
    return value

def success_envelope(data: Any, meta: Mapping[str, Any] | None = None, pagination: Mapping[str, Any] | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"data": _serialize(data)}
    # If called with 'pagination', use that key (legacy/test endpoints)
    if pagination is not None:
        response["pagination"] = _serialize(pagination)
    # If called with 'meta', use that key (catalog contract endpoints)
    elif meta is not None:
        response["meta"] = _serialize(meta)
    return response

def error_envelope(
    code: str,
    message: str,
    *,
    status_code: int = 500,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
            "details": _serialize(details or {}),
        }
    }

def pagination_envelope(total: int, limit: int, offset: int) -> dict[str, int]:
    """Provide consistent pagination metadata."""
    return {"total": total, "limit": limit, "offset": offset}
