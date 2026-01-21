from __future__ import annotations
from typing import Generic, Mapping, TypeVar
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field

T = TypeVar("T")

class DefaultModel(BaseModel):
    """Base Pydantic configuration shared across DTOs."""

    model_config = {"extra": "forbid", "populate_by_name": True}

    @staticmethod
    def _serialize_value(value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, UUID):
            return str(value)
        return value

    def model_dump(self, *args, **kwargs):
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
