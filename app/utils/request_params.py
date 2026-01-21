from __future__ import annotations
from uuid import UUID

def safe_int(args, name: str, default: int) -> int:
    try:
        return int(args.get(name, default))
    except (TypeError, ValueError):
        return default

def optional_int(args, name: str) -> int | None:
    value = args.get(name)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None

def safe_bool(value: str | None) -> bool | None:
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

def optional_uuid(args, name: str) -> UUID | None:
    value = args.get(name)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None

def toggle_flag(args) -> bool:
    active = args.get("active")
    return active != "false"
