from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Branch, Inventory, Product
from ..schemas.branches import (
    InventoryCreateRequest,
    InventoryListResponse,
    InventoryResponse,
    InventoryUpdateRequest,
)
from .audit_service import AuditService


class InventoryService:
    @staticmethod
    def list_inventory(
        branch_id: int | None,
        product_id: int | None,
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
                product_sku=item.product.sku,
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
    def update_inventory(item_id: int, payload: InventoryUpdateRequest) -> InventoryResponse:
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
            product_sku=inventory.product.sku,
            available_quantity=inventory.available_quantity,
            reserved_quantity=inventory.reserved_quantity,
            limit=0,
            offset=0,
            total=0,
        )

    @staticmethod
    def create_inventory(payload: InventoryCreateRequest) -> InventoryResponse:
        existing = (
            db.session.execute(
                select(Inventory).where(
                    Inventory.product_id == payload.product_id,
                    Inventory.branch_id == payload.branch_id,
                )
            ).scalar_one_or_none()
        )
        if existing:
            raise DomainError(
                "DUPLICATE_INVENTORY",
                "Inventory record already exists for the selected product and branch.",
                status_code=409,
            )
        product = db.session.get(Product, payload.product_id)
        if not product:
            raise DomainError("NOT_FOUND", "Product not found", status_code=404)
        branch = db.session.get(Branch, payload.branch_id)
        if not branch:
            raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
        inventory = Inventory(
            product_id=payload.product_id,
            branch_id=payload.branch_id,
            available_quantity=payload.available_quantity,
            reserved_quantity=payload.reserved_quantity,
        )
        db.session.add(inventory)
        db.session.commit()
        AuditService.log_event(
            entity_type="inventory",
            action="CREATE",
            actor_user_id=None,
            entity_id=inventory.id,
            new_value={
                "available_quantity": inventory.available_quantity,
                "reserved_quantity": inventory.reserved_quantity,
            },
        )
        return InventoryResponse(
            id=inventory.id,
            branch_id=inventory.branch_id,
            branch_name=branch.name,
            product_id=inventory.product_id,
            product_name=product.name,
            product_sku=product.sku,
            available_quantity=inventory.available_quantity,
            reserved_quantity=inventory.reserved_quantity,
            limit=0,
            offset=0,
            total=0,
        )
