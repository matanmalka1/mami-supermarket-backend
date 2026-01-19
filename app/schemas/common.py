"""Shared schema primitives for API responses."""

from __future__ import annotations

from typing import Generic, Mapping, TypeVar

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


T = TypeVar("T")


class DefaultModel(BaseModel):
    """Base Pydantic configuration shared across DTOs."""

    model_config = {
        "extra": "forbid",
        "populate_by_name": True,
        "json_encoders": {
            Decimal: lambda value: str(value),
            UUID: lambda value: str(value),
        },
    }


class ErrorDetails(BaseModel):
    """Structured payload for error details."""

    model_config = {"extra": "forbid"}
    errors: Mapping[str, str] | None = None


class ErrorResponse(DefaultModel):
    error: dict[str, Mapping[str, str] | str] = Field(
        ...,
        example={"code": "SOME_CODE", "message": "Human readable", "details": {}},
    )


class Pagination(DefaultModel):
    total: int = Field(ge=0)
    limit: int = Field(ge=0)
    offset: int = Field(ge=0)


class PaginatedResponse(DefaultModel, Generic[T]):
    data: list[T]
    pagination: Pagination
