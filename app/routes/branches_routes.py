"""Branch/public endpoints."""

from __future__ import annotations

# PUBLIC: All endpoints in this file are intentionally unauthenticated for branch and delivery slot info.
from flask import Blueprint, jsonify, request
from app.services.branch import BranchCoreService, DeliverySlotService
from app.utils.responses import success_envelope 
from app.schemas.branches import BranchesQuery , DeliverySlotsQuery

blueprint = Blueprint("branches", __name__)

## READ (Branches)
@blueprint.get("/branches")
def list_branches():
    params = BranchesQuery(**request.args)
    branches, total = BranchCoreService.list_branches(params.limit, params.offset)
    return jsonify(success_envelope(branches, pagination={"total": total, "limit": params.limit, "offset": params.offset}))


## READ (Delivery Slots)
@blueprint.get("/delivery-slots")
def list_delivery_slots():
    params = DeliverySlotsQuery(**request.args)
    slots = DeliverySlotService.list_delivery_slots(params.dayOfWeek, params.branchId)
    return jsonify(success_envelope(slots))
