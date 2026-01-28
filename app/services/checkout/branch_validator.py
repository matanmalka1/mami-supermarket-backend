from __future__ import annotations
from datetime import time
from flask import current_app
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Branch, DeliverySlot
from app.models.enums import FulfillmentType
from app.services.branch import BranchCoreService


class CheckoutBranchValidator:
    @staticmethod
    def resolve_branch(fulfillment_type: FulfillmentType | None, branch_id: int | None) -> int:
        if fulfillment_type == FulfillmentType.DELIVERY:
            source_id = current_app.config.get("DELIVERY_SOURCE_BRANCH_ID", "")
            branch = BranchCoreService.ensure_delivery_source_branch_exists(source_id)
            return branch.id
        if branch_id:
            branch = db.session.get(Branch, branch_id)
            if not branch or not branch.is_active:
                raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
            return branch.id
        raise DomainError("BAD_REQUEST", "Branch is required for pickup", status_code=400)

    @staticmethod
    def validate_delivery_slot(fulfillment_type: FulfillmentType | None, slot_id: int | None, branch_id: int) -> None:
        if fulfillment_type != FulfillmentType.DELIVERY:
            return
        if not slot_id:
            raise DomainError("BAD_REQUEST", "Delivery slot is required for delivery", status_code=400)
        slot = db.session.get(DeliverySlot, slot_id)
        if not slot or not slot.is_active:
            raise DomainError("NOT_FOUND", "Delivery slot not found", status_code=404)
        if slot.branch_id != branch_id:
            raise DomainError("INVALID_SLOT", "Delivery slot does not belong to delivery branch", status_code=400)
        start = slot.start_time
        end = slot.end_time
        if not (time(6, 0) <= start < end <= time(22, 0)) or (end.hour - start.hour) != 2:
            raise DomainError("INVALID_SLOT", "Delivery slot must be a 2-hour window between 06:00-22:00", status_code=400)
