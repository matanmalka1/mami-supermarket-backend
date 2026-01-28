from __future__ import annotations
from typing import Generic, Mapping, TypeVar
from decimal import Decimal

from pydantic import BaseModel, Field
from datetime import time, datetime, date

T = TypeVar("T")

class DefaultModel(BaseModel):
    """Base Pydantic configuration shared across DTOs."""

    model_config = {"extra": "forbid", "populate_by_name": True}

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, bool):
            return value
        if isinstance(value, (time, datetime, date)):
            return value.isoformat()
        return value

    def model_dump(self, *args, **kwargs):
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = False
        data = super().model_dump(*args, **kwargs)
        return {k: self._serialize_value(v) for k, v in data.items()}

class ErrorDetails(BaseModel):
    """Structured payload for error details."""

    model_config = {"extra": "forbid"}
    errors: Mapping[str, str] | None = None

class ErrorResponse(DefaultModel):
    error: dict[str, Mapping[str, str] | str] = Field(...)

class Pagination(DefaultModel):
    total: int = Field(ge=0)
    limit: int = Field(ge=0)
    offset: int = Field(ge=0)

class PaginatedResponse(DefaultModel, Generic[T]):
    data: list[T]
    pagination: Pagination
