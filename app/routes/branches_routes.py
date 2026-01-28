"""Branch/public endpoints."""

from __future__ import annotations


# PUBLIC: All endpoints in this file are intentionally unauthenticated for branch and delivery slot info.
from flask import Blueprint, jsonify, request

from app.services.branch_service import BranchService
from app.utils.request_params import optional_int, safe_int
from app.utils.responses import success_envelope

blueprint = Blueprint("branches", __name__)


## READ (Branches)
@blueprint.get("/branches")
def list_branches():
    from app.schemas.branches_query import BranchesQuery
    try:
        params = BranchesQuery(**request.args)
    except Exception as e:
        return jsonify({"error": str(e)}), 422
    branches, total = BranchService.list_branches(params.limit, params.offset)
    return jsonify(success_envelope(branches, pagination={"total": total, "limit": params.limit, "offset": params.offset}))


## READ (Delivery Slots)
@blueprint.get("/delivery-slots")
def list_delivery_slots():
    from app.schemas.branches_query import DeliverySlotsQuery
    try:
        params = DeliverySlotsQuery(**request.args)
    except Exception as e:
        return jsonify({"error": str(e)}), 422
    slots = BranchService.list_delivery_slots(params.dayOfWeek, params.branchId)
    return jsonify(success_envelope(slots))
