"""Standardized API response envelope helpers."""

from __future__ import annotations
from decimal import Decimal
from typing import Any, Mapping
from uuid import UUID
from pydantic import BaseModel

def _serialize(value: Any) -> Any:
    """Convert Pydantic models and common primitives into JSON-safe structures."""
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize(val) for key, val in value.items()}
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    return value

def success_envelope(data: Any, pagination: Mapping[str, Any] | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"data": _serialize(data)}
    if pagination:
        response["pagination"] = _serialize(pagination)
    return response

def error_envelope(code: str, message: str, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": _serialize(details or {}),
        }
    }

def pagination_envelope(total: int, limit: int, offset: int) -> dict[str, int]:
    """Provide consistent pagination metadata."""
    return {"total": total, "limit": limit, "offset": offset}
