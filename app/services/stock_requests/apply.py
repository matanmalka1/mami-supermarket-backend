from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Inventory
from app.models.enums import StockRequestType
from app.services.audit_service import AuditService


def apply_inventory_change(
    branch_id: UUID,
    product_id: UUID,
    request_type: StockRequestType,
    approved_quantity: int,
    actor_id: UUID,
) -> None:
    session = db.session
    inventory = session.execute(
        sa.select(Inventory)
        .where(Inventory.branch_id == branch_id)
        .where(Inventory.product_id == product_id)
        .with_for_update()
    ).scalar_one_or_none()
    if not inventory:
        raise DomainError("NOT_FOUND", "Inventory not found for branch/product", status_code=404)
    old_value = {
        "available_quantity": inventory.available_quantity,
        "reserved_quantity": inventory.reserved_quantity,
    }
    if request_type == StockRequestType.SET_QUANTITY:
        inventory.available_quantity = approved_quantity
    elif request_type == StockRequestType.ADD_QUANTITY:
        inventory.available_quantity += approved_quantity
    session.add(inventory)
    AuditService.log_event(
        entity_type="inventory",
        action="STOCK_REQUEST_APPLY",
        actor_user_id=actor_id,
        entity_id=inventory.id,
        old_value=old_value,
        new_value={
            "available_quantity": inventory.available_quantity,
            "reserved_quantity": inventory.reserved_quantity,
        },
    )
