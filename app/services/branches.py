"""Services for branches, delivery slots, and inventory."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Branch, DeliverySlot, Inventory
from ..schemas.branches import (
    BranchResponse,
    DeliverySlotResponse,
    InventoryListResponse,
    InventoryResponse,
    InventoryUpdateRequest,
)
from ..services.audit import AuditService


class BranchService:
    @staticmethod
    def list_branches(limit: int, offset: int) -> tuple[list[BranchResponse], int]:
        stmt = (
            select(Branch)
            .where(Branch.is_active.is_(True))
            .offset(offset)
            .limit(limit)
        )
        branches = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(
            select(func.count()).select_from(Branch).where(Branch.is_active.is_(True))
        )
        return ([BranchResponse(**b.__dict__) for b in branches], total or 0)

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
    def create_branch(name: str, address: str) -> BranchResponse:
        branch = Branch(name=name, address=address)
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(entity_type="branch", action="CREATE", entity_id=branch.id)
        return BranchResponse(**branch.__dict__)

    @staticmethod
    def update_branch(branch_id: UUID, name: str, address: str) -> BranchResponse:
        branch = db.session.get(Branch, branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        old_value = {"name": branch.name, "address": branch.address}
        branch.name = name
        branch.address = address
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(
            entity_type="branch",
            action="UPDATE",
            entity_id=branch.id,
            old_value=old_value,
            new_value={"name": name, "address": address},
        )
        return BranchResponse(**branch.__dict__)

    @staticmethod
    def toggle_branch(branch_id: UUID, active: bool) -> BranchResponse:
        branch = db.session.get(Branch, branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        branch.is_active = active
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(
            entity_type="branch",
            action="DEACTIVATE" if not active else "ACTIVATE",
            entity_id=branch.id,
            new_value={"is_active": active},
        )
        return BranchResponse(**branch.__dict__)

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


class InventoryService:
    @staticmethod
    def list_inventory(
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> InventoryListResponse:
        stmt = select(Inventory).options(
            selectinload(Inventory.branch), selectinload(Inventory.product)
        )
        if branch_id:
            stmt = stmt.where(Inventory.branch_id == branch_id)
        if product_id:
            stmt = stmt.where(Inventory.product_id == product_id)
        total = db.session.scalar(select(func.count()).select_from(stmt.subquery()))
        items = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        responses = [
            InventoryResponse(
                id=item.id,
                branch_id=item.branch_id,
                branch_name=item.branch.name,
                product_id=item.product_id,
                product_name=item.product.name,
                available_quantity=item.available_quantity,
                reserved_quantity=item.reserved_quantity,
                limit=limit,
                offset=offset,
                total=total or 0,
            )
            for item in items
        ]
        return InventoryListResponse(items=responses, pagination={
            "total": total or 0,
            "limit": limit,
            "offset": offset,
        })

    @staticmethod
    def update_inventory(item_id: UUID, payload: InventoryUpdateRequest) -> InventoryResponse:
        inventory = db.session.get(Inventory, item_id)
        if not inventory:
            raise DomainError("NOT_FOUND", "Inventory not found", status_code=404)
        old_value = {
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
        }
        inventory.available_quantity = payload.available_quantity
        inventory.reserved_quantity = payload.reserved_quantity
        db.session.add(inventory)
        db.session.commit()
        AuditService.log_event(
            entity_type="inventory",
            action="UPDATE",
            entity_id=inventory.id,
            old_value=old_value,
            new_value={
                "available_quantity": payload.available_quantity,
                "reserved_quantity": payload.reserved_quantity,
            },
        )
        return InventoryResponse(
            id=inventory.id,
            branch_id=inventory.branch_id,
            branch_name=inventory.branch.name,
            product_id=inventory.product_id,
            product_name=inventory.product.name,
            available_quantity=inventory.available_quantity,
            reserved_quantity=inventory.reserved_quantity,
            limit=0,
            offset=0,
            total=0,
        )
