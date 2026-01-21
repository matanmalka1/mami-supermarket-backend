from __future__ import annotations
from uuid import UUID
from sqlalchemy import func, select
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Branch
from app.schemas.branches import BranchResponse
from app.services.audit_service import AuditService


class BranchCoreService:
    @staticmethod
    def ensure_delivery_source_branch_exists(branch_id: str) -> Branch:
        """Ensure configured DELIVERY_SOURCE_BRANCH_ID exists; raise if not."""
        if not branch_id:
            raise DomainError("CONFIG_ERROR", "DELIVERY_SOURCE_BRANCH_ID is not set", status_code=500)
        try:
            branch_uuid = UUID(str(branch_id))
        except ValueError as exc:
            raise DomainError("CONFIG_ERROR", "DELIVERY_SOURCE_BRANCH_ID is not a valid UUID", status_code=500) from exc

        branch = db.session.get(Branch, branch_uuid)
        if not branch:
            raise DomainError(
                "CONFIG_ERROR",
                "Configured DELIVERY_SOURCE_BRANCH_ID does not exist in branches table",
                status_code=500,
            )
        return branch

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
    def create_branch(name: str, address: str) -> BranchResponse:
        branch = Branch(name=name, address=address)
        db.session.add(branch)
        db.session.commit()
        AuditService.log_event(entity_type="branch", action="CREATE", entity_id=branch.id)
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)

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
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)

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
        return BranchResponse(id=branch.id, name=branch.name, address=branch.address, is_active=branch.is_active)
