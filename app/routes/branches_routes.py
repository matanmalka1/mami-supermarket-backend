"""Branch/public endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.branch_service import BranchService
from app.utils.request_params import optional_int, safe_int
from app.utils.responses import success_envelope

blueprint = Blueprint("branches", __name__)


## READ (Branches)
@blueprint.get("/branches")
def list_branches():
    limit = safe_int(request.args, "limit", 50)
    offset = safe_int(request.args, "offset", 0)
    branches, total = BranchService.list_branches(limit, offset)
    return jsonify(success_envelope(branches, pagination={"total": total, "limit": limit, "offset": offset}))


## READ (Delivery Slots)
@blueprint.get("/delivery-slots")
def list_delivery_slots():
    day = optional_int(request.args, "dayOfWeek")
    branch_id = optional_int(request.args, "branchId")
    slots = BranchService.list_delivery_slots(day, branch_id)
    return jsonify(success_envelope(slots))
