from __future__ import annotations
from enum import Enum
from typing import TypeVar, Type

T = TypeVar('T', bound=Enum)

def safe_int(args, name: str, default: int) -> int:
    try:
        return int(args.get(name, default))
    except (TypeError, ValueError):
        return default

def parse_int(value: str | None, default: int = 0, max_value: int | None = None) -> int:
    """Parse integer with optional max value constraint."""
    try:
        result = int(value) if value else default
        if max_value is not None and result > max_value:
            return max_value
        return result
    except (TypeError, ValueError):
        return default

def optional_int(args, name: str) -> int | None:
    value = args.get(name)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None

def parse_bool(value: str | None) -> bool | None:
    """Parse boolean from query parameter."""
    if value is None:
        return None
    truthy = {"1", "true", "yes"}
    falsy = {"0", "false", "no"}
    lowered = value.lower()
    if lowered in truthy:
        return True
    if lowered in falsy:
        return False
    return None

def parse_enum(value: str | None, enum_class: Type[T]) -> T | None:
    """Parse enum from string value."""
    if value is None:
        return None
    try:
        return enum_class(value)
    except (ValueError, KeyError):
        return None

def toggle_flag(args) -> bool:
    active = args.get("active")
    return active != "false"
