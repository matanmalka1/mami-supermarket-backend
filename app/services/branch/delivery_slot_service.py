from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Branch, DeliverySlot
from app.schemas.branches import DeliverySlotResponse
from app.services.audit_service import AuditService


class DeliverySlotService:
    @staticmethod
    def list_delivery_slots(day_of_week: int | None, branch_id: UUID | None) -> list[DeliverySlotResponse]:
        stmt = select(DeliverySlot).where(DeliverySlot.is_active.is_(True))
        if day_of_week is not None:
            stmt = stmt.where(DeliverySlot.day_of_week == day_of_week)
        if branch_id is not None:
            stmt = stmt.where(DeliverySlot.branch_id == branch_id)
        slots = db.session.execute(stmt).scalars().all()
        return [
            DeliverySlotResponse(
                id=slot.id,
                branch_id=slot.branch_id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
            )
            for slot in slots
        ]

    @staticmethod
    def create_delivery_slot(
        branch_id: UUID,
        day_of_week: int,
        start_time,
        end_time,
    ) -> DeliverySlotResponse:
        branch = db.session.get(Branch, branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        slot = DeliverySlot(
            branch_id=branch_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(slot)
        db.session.commit()
        AuditService.log_event(entity_type="delivery_slot", action="CREATE", entity_id=slot.id)
        return DeliverySlotResponse(
            id=slot.id,
            branch_id=slot.branch_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
        )

    @staticmethod
    def update_delivery_slot(
        slot_id: UUID,
        day_of_week: int,
        start_time,
        end_time,
    ) -> DeliverySlotResponse:
        slot = db.session.get(DeliverySlot, slot_id)
        if not slot:
            raise DomainError("NOT_FOUND", "Delivery slot not found", status_code=404)
        old_value = {
            "day_of_week": slot.day_of_week,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
        }
        slot.day_of_week = day_of_week
        slot.start_time = start_time
        slot.end_time = end_time
        db.session.add(slot)
        db.session.commit()
        AuditService.log_event(
            entity_type="delivery_slot",
            action="UPDATE",
            entity_id=slot.id,
            old_value=old_value,
            new_value={
                "day_of_week": day_of_week,
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        return DeliverySlotResponse(
            id=slot.id,
            branch_id=slot.branch_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
        )

    @staticmethod
    def toggle_delivery_slot(slot_id: UUID, active: bool) -> DeliverySlotResponse:
        slot = db.session.get(DeliverySlot, slot_id)
        if not slot:
            raise DomainError("NOT_FOUND", "Delivery slot not found", status_code=404)
        slot.is_active = active
        db.session.add(slot)
        db.session.commit()
        AuditService.log_event(
            entity_type="delivery_slot",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=slot.id,
            new_value={"is_active": active},
        )
        return DeliverySlotResponse(
            id=slot.id,
            branch_id=slot.branch_id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
        )
