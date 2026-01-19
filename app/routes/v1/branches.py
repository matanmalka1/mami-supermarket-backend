"""Branch/public endpoints."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from flask import Blueprint, jsonify, request

from ..services.branches import BranchService
from ..utils.responses import success_envelope

blueprint = Blueprint("branches", __name__)


def _safe_int(name: str, default: int) -> int:
    try:
        return int(request.args.get(name, default))
    except (TypeError, ValueError):
        return default


def _optional_int(name: str) -> int | None:
    value = request.args.get(name)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def _optional_uuid(name: str) -> UUID | None:
    value = request.args.get(name)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


@blueprint.get("/branches")
def list_branches():
    limit = _safe_int("limit", 50)
    offset = _safe_int("offset", 0)
    branches, total = BranchService.list_branches(limit, offset)
    return jsonify(success_envelope(branches, {"total": total, "limit": limit, "offset": offset}))


@blueprint.get("/delivery-slots")
def list_delivery_slots():
    day = _optional_int("dayOfWeek")
    branch_id = _optional_uuid("branchId")
    slots = BranchService.list_delivery_slots(day, branch_id)
    return jsonify(success_envelope(slots))
