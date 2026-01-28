from __future__ import annotations

from sqlalchemy import select

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Inventory
from app.schemas.checkout import MissingItem
from app.services.audit_service import AuditService


class CheckoutInventoryManager:
    def __init__(self, branch_id: int):
        self.branch_id = branch_id

    def lock_inventory(self, cart_items) -> dict[tuple[int, int], Inventory]:
        inv_ids = [item.product_id for item in cart_items]
        inventory_rows = (
            db.session.execute(
                select(Inventory)
                .where(Inventory.product_id.in_(inv_ids))
                .where(Inventory.branch_id == self.branch_id)
                .with_for_update()
            )
            .scalars()
            .all()
        )
        return {(inv.product_id, inv.branch_id): inv for inv in inventory_rows}

    def missing_items(self, cart_items, inv_map=None) -> list[MissingItem]:
        missing: list[MissingItem] = []
        for item in cart_items:
            if inv_map is None:
                inv_row = db.session.execute(
                    select(Inventory).where(Inventory.product_id == item.product_id, Inventory.branch_id == self.branch_id)
                ).scalar_one_or_none()
            else:
                inv_row = inv_map.get((item.product_id, self.branch_id))
            available = inv_row.available_quantity if inv_row else 0
            if available < item.quantity:
                missing.append(
                    MissingItem(
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=available,
                    )
                )
        return missing

    def decrement_inventory(self, cart_items, inv_map) -> None:
        for item in cart_items:
            key = (item.product_id, self.branch_id)
            inv_row = inv_map.get(key)
            if not inv_row:
                continue
            if inv_row.available_quantity < item.quantity:
                raise DomainError(
                    "INSUFFICIENT_STOCK",
                    f"Not enough stock for product {item.product_id}",
                    status_code=400,
                )
            old_value = {
                "available_quantity": inv_row.available_quantity,
                "reserved_quantity": inv_row.reserved_quantity,
            }
            inv_row.available_quantity -= item.quantity
            db.session.add(inv_row)
            AuditService.log_event(
                entity_type="inventory",
                action="DECREMENT",
                entity_id=inv_row.id,
                old_value=old_value,
                new_value={
                    "available_quantity": inv_row.available_quantity,
                    "reserved_quantity": inv_row.reserved_quantity,
                },
            )
